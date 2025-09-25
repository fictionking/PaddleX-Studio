from flask import Blueprint, make_response, jsonify, request, Response
import os
import json
import logging
import uuid
import multiprocessing
import re
from datetime import datetime
import threading
import signal

import pxs.paddlexCfg as cfg
from pxs.workflow.pipeline import WorkflowPipeline

# 创建Flask蓝图
workflow_mgr = Blueprint('workflow_mgr', __name__)

# 全局变量
workflows_root = None
workflows_config_path = None
workflows = []  # 数组类型
# workflow_lock = threading.Lock() - 这个变量没有被使用

# 当前运行的工作流
current_workflow_id = None
current_workflow_process = None

# 用于进程间通信的队列
workflow_status_queue = multiprocessing.Queue(maxsize=1)

# 用于通知工作流进程退出的事件标志
exit_event = multiprocessing.Event()

# 当前运行的工作流
current_workflow_id = None
current_workflow_process = None

# 用于进程间通信的队列
workflow_status_queue = multiprocessing.Queue(maxsize=100)

def workflow_process_func(workflow_id, workflow_definition, workflow_dir, status_queue, exit_event):
    """工作流执行进程函数
    
    Args:
        workflow_id: 工作流ID
        workflow_definition: 工作流定义
        workflow_dir: 工作流目录
        status_queue: 状态队列
        exit_event: 退出事件标志
    """
    # 定义日志文件路径
    log_file_path = os.path.join(workflow_dir, 'log.txt')
    log_file = None
    
    try:
        # 打开日志文件，使用写入模式
        log_file = open(log_file_path, 'w', encoding='utf-8')
        
        # 创建工作流实例并执行推理
        workflow = WorkflowPipeline(workflow_definition)
        
        logging.info(f'工作流 {workflow_id} 已启动')
        
        # 执行工作流并获取状态
        last_status = None
        try:
            for result in workflow.predict():
                # 检查是否收到退出信号
                if exit_event.is_set():
                    logging.info(f'工作流 {workflow_id} 收到退出信号')
                    break
                
                # 缓存最后一条运行状态到队列中
                last_status = result
                # 如果队列已满，则移除最早的元素
                if status_queue.full():
                    try:
                        status_queue.get_nowait()
                    except:
                        pass
                status_data = {'workflow_id': workflow_id, 'status': 'running', 'data': result}
                status_queue.put(status_data)
                
                # 将状态数据写入日志文件
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                log_entry = f'[{timestamp}] {json.dumps(status_data, ensure_ascii=False)}\n'
                
                try:
                    if log_file and not log_file.closed:
                        log_file.write(log_entry)
                        log_file.flush()  # 确保数据写入磁盘
                except Exception as log_e:
                    logging.error(f'写入日志失败：{str(log_e)}')
        except Exception as inner_e:
            logging.error(f'工作流 {workflow_id} 执行过程中出错：{str(inner_e)}')
            # 发送错误状态
            if status_queue.full():
                try:
                    status_queue.get_nowait()
                except:
                    pass
            error_status = {'workflow_id': workflow_id, 'status': 'error', 'error': str(inner_e)}
            status_queue.put(error_status)
            
            # 将错误状态写入日志文件
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
            log_entry = f'[{timestamp}] {json.dumps(error_status, ensure_ascii=False)}\n'
            try:
                if log_file and not log_file.closed:
                    log_file.write(log_entry)
                    log_file.flush()
            except Exception as log_e:
                logging.error(f'写入错误日志失败：{str(log_e)}')
        
        # 工作流执行完成或被中断
        if status_queue.full():
            try:
                status_queue.get_nowait()
            except:
                pass
        
        if exit_event.is_set():
            # 工作流被中断
            complete_status = {'workflow_id': workflow_id, 'status': 'stopped', 'message': '工作流已被停止'}
        else:
            # 工作流正常完成
            complete_status = {'workflow_id': workflow_id, 'status': 'completed', 'last_result': last_status}
        
        status_queue.put(complete_status)
        
        # 将完成状态写入日志文件
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        log_entry = f'[{timestamp}] {json.dumps(complete_status, ensure_ascii=False)}\n'
        try:
            if log_file and not log_file.closed:
                log_file.write(log_entry)
                log_file.flush()
        except Exception as log_e:
            logging.error(f'写入完成日志失败：{str(log_e)}')
        
        logging.info(f'工作流 {workflow_id} 已完成')
    except Exception as e:
        logging.error(f'工作流 {workflow_id} 执行出错：{str(e)}')
        # 发送错误状态
        if status_queue.full():
            try:
                status_queue.get_nowait()
            except:
                pass
        error_status = {'workflow_id': workflow_id, 'status': 'error', 'error': str(e)}
        status_queue.put(error_status)
        
        # 将错误状态写入日志文件
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        log_entry = f'[{timestamp}] {json.dumps(error_status, ensure_ascii=False)}\n'
        try:
            with open(log_file_path, 'a', encoding='utf-8') as temp_log_file:
                temp_log_file.write(log_entry)
        except Exception as log_e:
            logging.error(f'写入错误日志失败：{str(log_e)}')
    finally:
        # 确保关闭日志文件
        try:
            if log_file and not log_file.closed:
                log_file.close()
        except Exception as close_e:
            logging.warning(f'关闭日志文件时出错：{str(close_e)}')
        
        # 在进程中无法直接修改主进程的全局变量，需要通过队列通知
        if status_queue.full():
            try:
                status_queue.get_nowait()
            except:
                pass
        status_queue.put({'workflow_id': workflow_id, 'status': 'stopped', 'process_completed': True})


def init():
    """初始化工作流管理器，加载工作流配置"""
    global workflows_root, workflows_config_path, workflows
    workflows_root = os.path.join(cfg.studio_root, 'workflows')
    # 确保工作流根目录存在
    os.makedirs(workflows_root, exist_ok=True)
    # 加载工作流配置
    workflows_config_path = os.path.join(workflows_root, 'workflows_config.json')
    workflows = load_or_create_workflows_config()


def load_or_create_workflows_config():
    """加载或创建工作流配置文件，直接返回数组"""
    if not os.path.exists(workflows_config_path):
        with open(workflows_config_path, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=4)
        logging.info(f'创建空工作流配置文件：{workflows_config_path}')
        return []
    try:
        with open(workflows_config_path, 'r', encoding='utf-8') as f:
            workflows_list = json.load(f)
            # 直接返回数组
            return workflows_list
    except json.JSONDecodeError:
        logging.error(f'配置文件 {workflows_config_path} 格式错误，重置为空文件')
        return []
    except Exception as e:
        logging.error(f'加载工作流配置文件时发生未知错误：{str(e)}，返回空数组')
        return []


def save_workflow_config():
    """
    保存工作流配置信息到JSON文件，直接保存数组
    """
    with open(workflows_config_path, 'w', encoding='utf-8') as f:
        json.dump(workflows, f, ensure_ascii=False, indent=4)
    logging.info(f'工作流配置已保存到 {workflows_config_path}')


@workflow_mgr.route('/workflows', methods=['GET'])
def list_workflows():
    """
    获取所有工作流列表
    :return: JSON格式的工作流列表
    """
    # 为每个工作流添加状态信息
    workflows_with_status = []
    for workflow in workflows:
        workflow_with_status = workflow.copy()
        workflow_with_status['status'] = 'running' if workflow['id'] == current_workflow_id else 'stopped'
        workflows_with_status.append(workflow_with_status)
    return jsonify(workflows_with_status)


@workflow_mgr.route('/workflows/<workflow_id>', methods=['GET'])
def get_workflow(workflow_id):
    """
    获取单个工作流的详细信息和定义
    :param workflow_id: 工作流ID
    :return: JSON格式的工作流详细信息或错误消息
    """
    # 在数组中查找指定ID的工作流
    workflow = next((w for w in workflows if w['id'] == workflow_id), None)
    
    if workflow:
        workflow_with_status = workflow.copy()
        workflow_with_status['status'] = 'running' if workflow_id == current_workflow_id else 'stopped'
        
        # 尝试加载工作流定义文件
        workflow_dir = os.path.join(workflows_root, workflow_id)
        workflow_config_path = os.path.join(workflow_dir, 'workflow.json')
        if os.path.exists(workflow_config_path):
            try:
                with open(workflow_config_path, 'r', encoding='utf-8') as f:
                    workflow_definition = json.load(f)
                workflow_with_status['definition'] = workflow_definition
            except Exception as e:
                logging.error(f'加载工作流定义文件时出错：{str(e)}')
                workflow_with_status['definition'] = None
        
        return jsonify(workflow_with_status), 200
    else:
        return jsonify({'success': False, 'error': f'工作流 ID {workflow_id} 不存在'}), 404

@workflow_mgr.route('/workflows/<workflow_id>', methods=['PUT'])
def save_workflow(workflow_id):
    """
    保存工作流定义
    :param workflow_id: 工作流ID
    :return: JSON格式的保存结果
    """
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': '请求体不能为空'}), 400
    
    # 检查工作流是否存在
    workflow = next((w for w in workflows if w['id'] == workflow_id), None)
    if not workflow:
        return jsonify({'success': False, 'error': f'工作流 ID {workflow_id} 不存在'}), 404
    
    try:
        # 更新工作流基本信息
        if 'name' in data:
            workflow['name'] = data['name']
        if 'description' in data:
            workflow['description'] = data['description']
        workflow['update_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 创建工作流目录（如果不存在）
        workflow_dir = os.path.join(workflows_root, workflow_id)
        os.makedirs(workflow_dir, exist_ok=True)
        
        # 保存工作流定义到workflow.json文件
        workflow_definition = data.get('definition', {})
        config_path = os.path.join(workflow_dir, 'workflow.json')
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(workflow_definition, f, ensure_ascii=False, indent=4)
        
        # 保存工作流配置
        save_workflow_config()
        
        logging.info(f'工作流 {workflow_id} 已保存')
        return jsonify({'success': True, 'message': '工作流保存成功'}), 200
    except Exception as e:
        logging.error(f'保存工作流 {workflow_id} 失败：{str(e)}')
        return jsonify({'success': False, 'error': f'保存工作流失败：{str(e)}'}), 500

@workflow_mgr.route('/workflows', methods=['POST'])
def create_workflow():
    """
    新建工作流
    :return: JSON格式的创建结果
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': '请求体不能为空'}), 400
        
        # 检查是否提供了自定义ID
        custom_id = data.get('id')
        if custom_id:
            # 验证自定义ID格式（只能包含字母、数字和下划线）
            if not re.match(r'^[a-zA-Z0-9_]+$', custom_id):
                return jsonify({'success': False, 'error': '工作流ID只能包含字母、数字和下划线'}), 400
            # 验证自定义ID长度
            if len(custom_id) > 50:
                return jsonify({'success': False, 'error': '工作流ID长度不能超过50个字符'}), 400
            # 检查ID是否已存在
            if any(wf['id'] == custom_id for wf in workflows):
                return jsonify({'success': False, 'error': '工作流ID已存在'}), 400
            workflow_id = custom_id
        else:
            # 未提供自定义ID，生成唯一UUID
            workflow_id = str(uuid.uuid4())
            
        workflow_name = data.get('name', f'工作流_{datetime.now().strftime("%Y%m%d%H%M%S")}')
        workflow_desc = data.get('description', '')
        workflow_definition = data.get('definition', {})
        
        # 创建新工作流对象
        new_workflow = {
            'id': workflow_id,
            'name': workflow_name,
            'description': workflow_desc,
            'create_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 创建工作流目录
        workflow_dir = os.path.join(workflows_root, workflow_id)
        try:
            os.makedirs(workflow_dir, exist_ok=True)
            
            # 保存工作流定义到workflow.json文件
            config_path = os.path.join(workflow_dir, 'workflow.json')
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(workflow_definition, f, ensure_ascii=False, indent=4)
            
            # 将新工作流添加到数组并保存配置
            workflows.append(new_workflow)
            save_workflow_config()
            
            return jsonify({'success': True, 'workflow_id': workflow_id, 'message': '工作流创建成功'}), 201
        except Exception as e:
            # 发生错误时清理
            if os.path.exists(workflow_dir):
                os.rmdir(workflow_dir)
            # 从数组中移除已添加的工作流
            if new_workflow in workflows:
                workflows.remove(new_workflow)
            return jsonify({'success': False, 'error': f'创建工作流失败：{str(e)}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': f'处理请求时出错：{str(e)}'}), 500


@workflow_mgr.route('/workflows/<workflow_id>/run', methods=['POST'])
def run_workflow(workflow_id):
    """
    运行指定的工作流
    :param workflow_id: 工作流ID
    :return: JSON格式的运行结果
    """
    global current_workflow_id, current_workflow_process
    
    # 检查工作流是否存在
    workflow = next((w for w in workflows if w['id'] == workflow_id), None)
    if not workflow:
        return jsonify({'success': False, 'error': f'工作流 ID {workflow_id} 不存在'}), 404
    
    # 检查工作流定义文件是否存在
    workflow_dir = os.path.join(workflows_root, workflow_id)
    workflow_config_path = os.path.join(workflow_dir, 'workflow.json')
    if not os.path.exists(workflow_config_path):
        return jsonify({'success': False, 'error': f'工作流定义文件不存在'}), 404
    
    # 加载工作流定义
    try:
        with open(workflow_config_path, 'r', encoding='utf-8') as f:
            workflow_definition = json.load(f)
        # 检查是否有正在运行的工作流
        if current_workflow_id is not None:
            return jsonify({'success': False, 'error': f'工作流 {current_workflow_id} 正在运行，请先停止'}), 400
        # 在线程中运行工作流
        current_workflow_id = workflow_id
        
        # 重置退出事件标志
        exit_event.clear()
        # 清空队列
        while not workflow_status_queue.empty():
            workflow_status_queue.get()
        # 启动工作流进程
        global current_workflow_process
        current_workflow_process = multiprocessing.Process(
            target=workflow_process_func,
            args=(workflow_id, workflow_definition, workflow_dir, workflow_status_queue, exit_event)
        )
        # 在Windows上，设置daemon=True可能会导致进程无法正确终止
        current_workflow_process.daemon = False
        current_workflow_process.start()
        return jsonify({'success': True, 'message': f'工作流 {workflow_id} 已开始运行'}), 200
    except Exception as e:
        current_workflow_id = None
        return jsonify({'success': False, 'error': f'启动工作流失败：{str(e)}'}), 500


@workflow_mgr.route('/workflows/<workflow_id>/stop', methods=['POST'])
def stop_workflow(workflow_id):
    """
    停止正在运行的工作流（优先使用优雅退出，失败时再强制终止）
    :param workflow_id: 工作流ID
    :return: JSON格式的停止结果
    """
    global current_workflow_id, current_workflow_process
    
    if current_workflow_id != workflow_id:
        return jsonify({'success': False, 'error': f'工作流 {workflow_id} 未在运行'}), 400
    
    try:
        # 首先尝试优雅地通知工作流进程退出
        exit_event.set()
        
        # 给工作流进程一些时间来清理资源并退出
        graceful_timeout = 3  # 优雅退出等待时间（秒）
        if current_workflow_process and current_workflow_process.is_alive():
            logging.info(f'等待工作流 {workflow_id} 优雅退出...')
            current_workflow_process.join(timeout=graceful_timeout)
        
        # 如果进程仍然存活，尝试强制终止
        force_terminated = False
        if current_workflow_process and current_workflow_process.is_alive():
            try:
                logging.warning(f'工作流 {workflow_id} 未能优雅退出，尝试强制终止...')
                current_workflow_process.terminate()
                # 等待进程终止（最多等待5秒）
                current_workflow_process.join(timeout=5)
                force_terminated = True
                
                # 如果进程仍然存活，再次尝试
                if current_workflow_process.is_alive():
                    try:
                        logging.warning(f'工作流 {workflow_id} 强制终止失败，再次尝试...')
                        current_workflow_process.kill()
                    except Exception as kill_e:
                        logging.warning(f'强制终止工作流进程失败：{str(kill_e)}')
            except Exception as term_e:
                logging.warning(f'终止工作流进程时出错：{str(term_e)}')
        
        # 清空状态队列并添加停止状态
        while not workflow_status_queue.empty():
            try:
                workflow_status_queue.get_nowait()
            except:
                break
        
        # 添加停止状态到队列
        if force_terminated:
            stop_status = {'workflow_id': workflow_id, 'status': 'stopped', 'message': '工作流已被强制停止'}
        else:
            stop_status = {'workflow_id': workflow_id, 'status': 'stopped', 'message': '工作流已停止'}
        workflow_status_queue.put(stop_status)
        
        # 重置全局变量
        current_workflow_id = None
        current_workflow_process = None
        
        logging.info(f'工作流 {workflow_id} 已停止')
        return jsonify({'success': True, 'message': f'工作流 {workflow_id} 已停止'}), 200
    except Exception as e:
        logging.error(f'停止工作流 {workflow_id} 时发生错误：{str(e)}')
        # 尝试重置全局变量
        try:
            current_workflow_id = None
            current_workflow_process = None
        except:
            pass
        return jsonify({'success': False, 'error': f'停止工作流时发生错误：{str(e)}'}), 500


@workflow_mgr.route('/workflows/<workflow_id>', methods=['DELETE'])
def delete_workflow(workflow_id):
    """
    删除指定的工作流
    :param workflow_id: 工作流ID
    :return: JSON格式的删除结果
    """
    # 检查工作流是否存在
    workflow = next((w for w in workflows if w['id'] == workflow_id), None)
    if not workflow:
        return jsonify({'success': False, 'error': f'工作流 ID {workflow_id} 不存在'}), 404
    
    # 检查工作流是否正在运行
    if current_workflow_id == workflow_id:
        return jsonify({'success': False, 'error': f'工作流 {workflow_id} 正在运行，请先停止'}), 400
    
    # 删除工作流目录
    workflow_dir = os.path.join(workflows_root, workflow_id)
    try:
        # 从数组中删除工作流
        workflows.remove(workflow)
        save_workflow_config()
        
        # 删除工作流目录及其内容
        import shutil
        if os.path.exists(workflow_dir):
            shutil.rmtree(workflow_dir)
        
        return jsonify({'success': True, 'message': f'工作流 {workflow_id} 已删除'}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': f'删除工作流失败：{str(e)}'}), 500

def get_workflows_status():
    global current_workflow_id
    if current_workflow_id:
        return '运行中'
    return '未运行'


@workflow_mgr.route('/workflow-status/stream')
def get_workflow_status_stream():
    """
    提供工作流状态的SSE流，持续从队列中获取运行状态并推送给前端
    :return: SSE响应流
    """
    def event_stream():
        """生成SSE事件流"""
        # 声明全局变量
        global current_workflow_id, current_workflow_process
        
        # 首先发送当前工作流的基本状态
        base_status = {
            'current_workflow_id': current_workflow_id,
            'status': 'running' if current_workflow_id is not None else 'idle'
        }
        yield 'data: ' + json.dumps(base_status) + "\n\n"
        
        last_status = None
        # 持续检查队列中的最新状态
        while True:
            try:
                # 非阻塞方式检查队列中是否有新状态
                if not workflow_status_queue.empty():
                    # 获取队列中的最后一个状态
                    # 由于我们限制队列长度为1，所以只需要获取一次
                    current_status = workflow_status_queue.get_nowait()
                    yield 'data: ' + json.dumps(current_status) + "\n\n"
                    last_status = current_status
                    # 检查工作流是否已完成，如已完成则重置全局变量
                    if current_status.get('process_completed'):
                        current_workflow_id = None
                        current_workflow_process = None
                        logging.info(f'工作流 {current_status.get("workflow_id")} 完成，已重置全局状态')
                        return
                else:
                    # 如果队列为空，发送当前工作流的基础状态
                    if last_status:
                        yield 'data: ' + json.dumps(last_status) + "\n\n"
                    else:
                        yield 'data: ' + json.dumps(base_status) + "\n\n"
                
                # 每秒检查一次更新
                import time
                time.sleep(1)
            except GeneratorExit:
                # 客户端断开连接
                break
            except Exception as e:
                logging.error(f"SSE流错误: {str(e)}")
                # 发生错误时，尝试继续运行
                import time
                time.sleep(1)
    
    # 设置SSE响应头
    return Response(event_stream(), mimetype='text/event-stream', headers={
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive'
    })


@workflow_mgr.route('/workflow-status/current', methods=['GET'])
def get_current_workflow():
    """
    获取当前正在运行的工作流ID
    :return: JSON格式的当前工作流ID信息
    """
    return jsonify({
        'current_workflow_id': current_workflow_id,
        'status': 'running' if current_workflow_id is not None else 'idle'
    }), 200


@workflow_mgr.route('/workflows/<workflow_id>/logs', methods=['GET'])
def get_workflow_logs(workflow_id):
    """
    获取指定工作流的运行日志
    :param workflow_id: 工作流ID
    :return: JSON格式的日志内容或错误信息
    """
    try:
        # 构建日志文件路径
        workflow_dir = os.path.join(workflows_root, workflow_id)
        log_file_path = os.path.join(workflow_dir, 'log.txt')
        
        # 检查工作流目录是否存在
        if not os.path.exists(workflow_dir):
            return jsonify({'success': False, 'error': f'工作流 {workflow_id} 不存在'}), 404
        
        # 检查日志文件是否存在
        if not os.path.exists(log_file_path):
            return jsonify({'success': True, 'logs': '', 'message': '日志文件不存在'}), 200
        
        # 读取日志文件内容
        with open(log_file_path, 'r', encoding='utf-8') as log_file:
            logs_content = log_file.read()
        
        return jsonify({
            'success': True,
            'logs': logs_content,
            'workflow_id': workflow_id
        }), 200
    except Exception as e:
        logging.error(f"读取工作流日志失败: {str(e)}")
        return jsonify({'success': False, 'error': f'读取日志文件失败：{str(e)}'}), 500
