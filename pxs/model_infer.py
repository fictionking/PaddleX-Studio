import multiprocessing as mp
from multiprocessing import Queue
from queue import Empty
import os
import logging

from jinja2.nodes import Output
from paddlex import create_model
import gc
import time

# 使用独立进程运行模型，确保可以完全释放占用资源
class ModelProcess(mp.Process):
    """
    模型运行进程类，负责模型的加载、推理和销毁
    """
    def __init__(self, model_params):
        """
        初始化模型进程
        
        Args:
            model_params: 模型创建参数
            cwd: 进程工作目录，默认为None
        """
        super().__init__()
        self.model_params = model_params    # 模型参数
        self.model = None                   # 模型实例
        self.task_queue = Queue()           # 推理任务队列
        self.result_queue = Queue()         # 结果返回队列
        self.running = mp.Value('b', False)  # 进程运行标志(共享内存)
        self.lock = mp.Lock()               # 进程锁
        self.loaded = mp.Value('b', False)  # 模型加载完成标志(共享内存)
        self.error = None                   # 错误信息

    def stop(self):
        """停止进程并释放资源"""
        with self.lock:
            self.running.value = False
        # 清空任务队列
        while not self.task_queue.empty():
            self.task_queue.get()
        # 等待线程退出
        self.join(timeout=5)
        if self.is_alive():
            logging.warning(f"模型进程 {os.getpid()} 无法正常终止")

    def run(self):
        """进程主循环，处理模型加载和推理任务"""
        self.running.value = True
        try:
            # 加载模型
            print(f"模型进程 {os.getpid()} 开始加载模型")
            print(self.model_params)
            self.model = create_model(**self.model_params)
            with self.lock:
                self.loaded.value = True
            print(f"模型进程 {os.getpid()} 模型加载成功")

            # 处理推理任务
            while self.running.value:
                try:
                    if self.task_queue.empty():
                        time.sleep(1)
                        continue
                    task = self.task_queue.get(timeout=1)
                    task_data=task['data']
                    input=task_data['input']
                    params=task_data['predict_params']
                    result_type=task_data['result_type']
                    result_dir=task_data['result_dir']
                    output = self.model.predict(input,**params)
                    for res in output:
                        result = res
                    match result_type:
                        case 'img':
                            file_path=os.path.join(result_dir,'result.png')
                            result.save_to_img(file_path)
                            result_data = file_path
                        case 'json':
                            result_data = result.json
                        case 'html':
                            result_data = result.html
                    self.result_queue.put((task['task_id'], result_data, None))
                except Exception as e:
                    self.error = str(e)
                    logging.error(f"任务处理错误: {str(e)}", exc_info=True)
        except Exception as e:
            while not self.task_queue.empty():
                task = self.task_queue.get()
                self.result_queue.put((task['task_id'], None, str(e)))
        finally:
            # 释放模型资源
            if self.model:
                del self.model
                self.model = None
                gc.collect()
            self.loaded = False
            print(f"模型进程 {os.getpid()} 已退出")

    def submit_task(self,data):
        """
        提交任务到队列
        
        Args:
            data: 任务数据
            
        Returns:
            tuple: (bool, task_id/error_msg) 任务提交是否成功和任务ID或错误信息
        """
        if not self.running:
            return False, "模型进程未运行"
        if not self.loaded and self.error:
            return False, f"模型加载失败: {self.error}"
            
        task_id = id(data)
        self.task_queue.put({
            'data': data,
            'task_id': task_id
        })
        return True, task_id

    def get_result(self, timeout=None):
        """获取推理结果

        Returns:
            tuple: 推理结果、错误信息等
        """
        try:
            return self.result_queue.get(timeout=timeout)
        except Empty:
            return None

    def is_loaded(self):
        """检查模型是否加载完成"""
        return self.loaded.value

    def get_error(self):
        """获取错误信息"""
        return self.error
