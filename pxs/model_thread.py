import threading
import queue
import logging
from paddlex import create_model
import paddle
import gc

import time

class ModelThread(threading.Thread):
    """
    模型运行线程类，负责模型的加载、推理和销毁
    """
    def __init__(self, model_params):
        """
        初始化模型线程
        
        Args:
            model_creator: 模型创建函数
            model_params: 模型创建参数
        """
        super().__init__()
        self.model_params = model_params    # 模型参数
        self.model = None                   # 模型实例
        self.queue = queue.Queue()          # 推理任务队列
        self.running = False                # 线程运行标志
        self.lock = threading.Lock()        # 线程锁
        self.loaded = False                 # 模型加载完成标志
        self.error = None                   # 错误信息

    def run(self):
        """线程主循环，处理模型加载和推理任务"""
        self.running = True
        try:
            # 加载模型
            logging.info(f"模型线程 {self.ident} 开始加载模型")
            self.model = create_model(**self.model_params)
            self.loaded = True
            logging.info(f"模型线程 {self.ident} 模型加载成功")

            # 处理推理任务
            while self.running:
                try:
                    # 1秒超时，允许检查running状态
                    task = self.queue.get(timeout=1)
                    if task['type'] == 'infer':
                        # 执行推理
                        result = self.model.infer(task['data'])
                        task['callback'](result, None)
                    self.queue.task_done()
                except queue.Empty:
                    continue
        except Exception as e:
            self.error = str(e)
            logging.error(f"模型线程错误: {str(e)}", exc_info=True)
            # 通知所有等待的任务发生错误
            while not self.queue.empty():
                task = self.queue.get()
                if task['type'] == 'infer':
                    task['callback'](None, str(e))
                self.queue.task_done()
        finally:
            # 释放模型资源
            if self.model:
                del self.model
                self.model = None
                paddle.device.cuda.empty_cache()
                gc.collect()
            self.loaded = False
            logging.info(f"模型线程 {self.ident} 已退出")

    def stop(self):
        """停止线程并释放资源"""
        with self.lock:
            self.running = False
        # 清空任务队列
        while not self.queue.empty():
            self.queue.get()
            self.queue.task_done()
        # 等待线程退出
        self.join(timeout=5)
        if self.is_alive():
            logging.warning(f"模型线程 {self.ident} 无法正常终止")

    def submit_task(self, task_type, data, callback):
        """
        提交任务到队列
        
        Args:
            task_type: 任务类型，如'infer'
            data: 任务数据
            callback: 任务完成回调函数
            
        Returns:
            bool: 任务提交是否成功
        """
        if not self.running:
            return False, "模型线程未运行"
        if not self.loaded and self.error:
            return False, f"模型加载失败: {self.error}"
            
        self.queue.put({
            'type': task_type,
            'data': data,
            'callback': callback
        })
        return True, "任务已提交"

    def is_loaded(self):
        """检查模型是否加载完成"""
        return self.loaded

    def get_error(self):
        """获取错误信息"""
        return self.error