from flask import Blueprint, make_response, jsonify, request, Response
import os
import json
import logging
import uuid
import threading
import re
from datetime import datetime
from queue import Queue

import pxs.paddlexCfg as cfg
from pxs.workflow.pipeline import WorkflowPipeline

# 创建Flask蓝图
workflow_mgr = Blueprint('workflow_mgr', __name__)

# 全局变量
workflows_root = None
workflows_config_path = None
workflows = []  # 数组类型
workflow_lock = threading.Lock()

# 当前运行的工作流
current_workflow_id = None
current_workflow_thread = None

# 用于缓存工作流运行状态的队列，限制长度为1
workflow_status_queue = Queue(maxsize=1)


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

@workflow_mgr.route('/workflows/<workflow_id>', methods=['POST'])
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
    global current_workflow_id, current_workflow_thread
    
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
        def workflow_thread_func():
            """工作流执行线程函数"""
            global current_workflow_id
            # 定义日志文件路径
            log_file_path = os.path.join(workflow_dir, 'log.txt')
               
            try:
                # 创建工作流实例并执行推理
                workflow = WorkflowPipeline(workflow_definition)
                
                logging.info(f'工作流 {workflow_id} 已启动')
                
                # 执行工作流并获取状态
                last_status = None
                try:
                    for result in workflow.predict():
                        # 缓存最后一条运行状态到队列中
                        last_status = result
                        # 如果队列已满，则移除最早的元素
                        if workflow_status_queue.full():
                            workflow_status_queue.get_nowait()
                        status_data = {'workflow_id': workflow_id, 'status': 'running', 'data': result}
                        workflow_status_queue.put(status_data)
                        
                        # 将状态数据写入日志文件
                        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                        log_entry = f'[{timestamp}] {json.dumps(status_data, ensure_ascii=False)}\n'
                        with open(log_file_path, 'a', encoding='utf-8') as log_file:
                            log_file.write(log_entry)
                except Exception as inner_e:
                    logging.error(f'工作流 {workflow_id} 执行过程中出错：{str(inner_e)}')
                    # 发送错误状态
                    if workflow_status_queue.full():
                        workflow_status_queue.get_nowait()
                    error_status = {'workflow_id': workflow_id, 'status': 'error', 'error': str(inner_e)}
                    workflow_status_queue.put(error_status)
                    
                    # 将错误状态写入日志文件
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                    log_entry = f'[{timestamp}] {json.dumps(error_status, ensure_ascii=False)}\n'
                    with open(log_file_path, 'a', encoding='utf-8') as log_file:
                        log_file.write(log_entry)
                
                # 工作流执行完成
                if workflow_status_queue.full():
                    workflow_status_queue.get_nowait()
                complete_status = {'workflow_id': workflow_id, 'status': 'completed', 'last_result': last_status}
                workflow_status_queue.put(complete_status)
                
                # 将完成状态写入日志文件
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                log_entry = f'[{timestamp}] {json.dumps(complete_status, ensure_ascii=False)}\n'
                with open(log_file_path, 'a', encoding='utf-8') as log_file:
                    log_file.write(log_entry)
                
                logging.info(f'工作流 {workflow_id} 已完成')
            except Exception as e:
                logging.error(f'工作流 {workflow_id} 执行出错：{str(e)}')
                # 发送错误状态
                if workflow_status_queue.full():
                    workflow_status_queue.get_nowait()
                error_status = {'workflow_id': workflow_id, 'status': 'error', 'error': str(e)}
                workflow_status_queue.put(error_status)
                
                # 将错误状态写入日志文件
                log_file_path = os.path.join(workflow_dir, 'log.txt')
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
                log_entry = f'[{timestamp}] {json.dumps(error_status, ensure_ascii=False)}\n'
                with open(log_file_path, 'a', encoding='utf-8') as log_file:
                    log_file.write(log_entry)
            finally:
                current_workflow_id = None
        # 启动工作流线程
        current_workflow_thread = threading.Thread(target=workflow_thread_func)
        current_workflow_thread.daemon = True
        current_workflow_thread.start()
        return jsonify({'success': True, 'message': f'工作流 {workflow_id} 已开始运行'}), 200
    except Exception as e:
        current_workflow_id = None
        return jsonify({'success': False, 'error': f'启动工作流失败：{str(e)}'}), 500


@workflow_mgr.route('/workflows/<workflow_id>/stop', methods=['POST'])
def stop_workflow(workflow_id):
    """
    停止正在运行的工作流
    :param workflow_id: 工作流ID
    :return: JSON格式的停止结果
    """
    global current_workflow_id, current_workflow_thread
    
    if current_workflow_id != workflow_id:
        return jsonify({'success': False, 'error': f'工作流 {workflow_id} 未在运行'}), 400
    
    # 目前只能等待线程自然结束，因为没有简单的方法强制终止线程
    # 这里我们仅设置current_workflow_id为None，表示工作流不再标记为运行中
    current_workflow_id = None
    
    return jsonify({'success': True, 'message': f'工作流 {workflow_id} 已停止'}), 200


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
    """
    获取所有工作流的状态信息
    :return: 工作流状态字典
    """
    status = {}
    for workflow in workflows:
        status[workflow['id']] = {
            'name': workflow['name'],
            'status': 'running' if workflow['id'] == current_workflow_id else 'stopped'
        }
    return status


@workflow_mgr.route('/workflows/status/stream')
def get_workflow_status_stream():
    """
    提供工作流状态的SSE流，持续从队列中获取运行状态并推送给前端
    :return: SSE响应流
    """
    def event_stream():
        """生成SSE事件流"""
        last_status = None
        
        # 首先发送当前工作流的基本状态
        base_status = {
            'current_workflow_id': current_workflow_id,
            'status': 'running' if current_workflow_id is not None else 'idle'
        }
        yield "data: " + json.dumps(base_status) + "\n\n"
        
        # 持续检查队列中的最新状态
        while True:
            try:
                # 非阻塞方式检查队列中是否有新状态
                if not workflow_status_queue.empty():
                    # 获取队列中的最后一个状态
                    # 由于我们限制队列长度为1，所以只需要获取一次
                    current_status = workflow_status_queue.get_nowait()
                    
                    # 直接发送从队列中获取的状态，不再进行比较
                    # 工作流运行时已经确保只有变化时才输出状态
                    yield "data: " + json.dumps(current_status) + "\n\n"
                    last_status = current_status
                else:
                    # 如果队列为空，发送当前工作流的基础状态
                    current_base_status = {
                        'current_workflow_id': current_workflow_id,
                        'status': 'running' if current_workflow_id is not None else 'idle'
                    }
                    # 直接发送基础状态，不再进行比较
                    # 每秒定期更新前端显示的工作流运行状态
                    yield "data: " + json.dumps(current_base_status) + "\n\n"
                    base_status = current_base_status
                
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
