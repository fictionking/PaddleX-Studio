from flask import Blueprint, jsonify, request,send_file
import os
import shutil
import json
import logging
import time
from werkzeug.utils import secure_filename
import threading
import pxs.paddlexCfg as cfg
from pxs.model_infer import ModelProcess

# 全局变量跟踪当前运行的应用和模型
current_app_id = None
current_model_thread = None
current_result_types = None
current_predict_params = None
app_lock = threading.Lock()
# 线程锁用于确保启动/停止操作的原子性
app_lock = threading.Lock()

# 创建Flask蓝图
app_mgr = Blueprint('app_mgr', __name__)
apps_root = None
apps_config_path = None
apps = {}


def init():
    """初始化应用管理器，加载应用配置"""
    global apps_root, apps_config_path, apps
    apps_root = cfg.app_root
    # 加载应用配置
    apps_config_path = os.path.join(apps_root, 'apps_config.json')
    apps = load_or_create_apps_config()

def load_or_create_apps_config():
    """加载或创建应用配置文件，并返回以app id为键的字典"""
    if not os.path.exists(apps_config_path):
        with open(apps_config_path, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=4)
        logging.info(f'创建空应用配置文件：{apps_config_path}')
        return {}
    try:
        with open(apps_config_path, 'r', encoding='utf-8') as f:
            apps_list = json.load(f)
            # 将列表转换为以id为键的字典（假设每个app都有唯一的id字段）
            return {app['id']: app for app in apps_list}
    except json.JSONDecodeError:
        logging.error(f'配置文件 {apps_config_path} 格式错误，重置为空文件')
        return {}
    except KeyError as e:
        logging.error(f'应用配置文件中存在缺失id字段的应用：{str(e)}，重置为空文件')
        return {}
    except Exception as e:
        logging.error(f'加载应用配置文件时发生未知错误：{str(e)}，返回空字典')
        return {}

def save_app_config(new_app=None):
    """
    保存应用配置信息到JSON文件（存在则更新，不存在则添加），始终保存为数组格式
    :param new_app: 要保存的应用配置字典（需包含'id'属性）
    """
    global apps
    if new_app is not None:
        app_id = new_app.get('id')
        # 更新或添加应用到字典
        apps[app_id] = new_app
    # 转换为数组用于保存
    apps_list = list(apps.values())
    with open(apps_config_path, 'w', encoding='utf-8') as f:
        # 始终保存为数组格式
        json.dump(apps_list, f, ensure_ascii=False, indent=4)
    logging.info(f'应用配置已保存到 {apps_config_path}')

@app_mgr.route('/apps', methods=['GET'])
def list_applications():
    apps_list = list(apps.values())
    for app in apps_list:
        app['status'] = 'running' if app['id'] == current_app_id else 'stopped'
    return jsonify(apps_list)

def new_applications(app_id,app_name,app_type,app_category,app_module_name,app_model_name,app_config):
    # 检查ID唯一性
    global apps
    if app_id in apps:
        return False, f'App ID {app_id} already exists'

    # 创建新应用对象
    new_app = {
        'id': app_id,
        'name': app_name,
        'type': app_type,
        'category': app_category,
        'module_name': app_module_name,
        'model_name': app_model_name
    }
    app_dir = os.path.join(apps_root, app_id)
    try:
        # 保存apps数据
        save_app_config(new_app)
        # 创建应用目录
        os.makedirs(app_dir, exist_ok=True)

        # 创建配置文件
        config_path = os.path.join(app_dir, 'config.json')
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(app_config, f, ensure_ascii=False, indent=2)

        return True,'success'

    except Exception as e:
        # 发生错误时回滚
        if app_id in apps:
            del apps[app_id]
            os.rmdir(app_dir)
            save_app_config()
        return False,f'Failed to create app: {str(e)}'

@app_mgr.route('/apps/delete/<app_id>', methods=['DELETE'])
def del_applcation(app_id):
    global apps
    if app_id in apps:
        app_dir = os.path.join(apps_root, app_id)
        del apps[app_id]
        save_app_config()
        try:
            shutil.rmtree(app_dir)
            return jsonify({'success': True, 'app': app_id}), 204
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    else:
        return jsonify({'success': False, 'error': f'App ID {app_id} not exists'}), 404

@app_mgr.route('/apps/config/<app_id>', methods=['GET'])
def get_application_config(app_id):
    """获取指定应用的配置信息

    Args:
        app_id: 应用ID

    Returns:
        json: 应用配置信息或错误消息
    """
    global apps_root
    # 构建应用配置文件路径
    app_dir = os.path.join(apps_root, app_id)
    config_path = os.path.join(app_dir, 'config.json')
    
    # 检查应用目录是否存在
    if not os.path.exists(app_dir):
        return jsonify({
            'status': 'error',
            'message': f'应用 {app_id} 不存在',
            'data': None
        }), 404
    
    # 检查配置文件是否存在，不存在则返回空配置
    if not os.path.exists(config_path):
        return jsonify({
            'status': 'success',
            'message': f'应用 {app_id} 配置文件不存在，返回默认配置',
            'data': {}
        })
    
    # 读取并返回配置文件
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        #将app的所有属性添加到config
        app=apps[app_id]
        for key in app:
            config[key]=app[key]
        
        if app_id == current_app_id:
            config['status']='running'
        else:
            config['status']='stopped'
        
        return jsonify({
            'status': 'success',
            'message': f'获取应用 {app_id} 配置成功',
            'data': config
        })
    except json.JSONDecodeError:
        return jsonify({
            'status': 'error',
            'message': f'应用 {app_id} 配置文件格式错误',
            'data': None
        }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'读取应用 {app_id} 配置失败: {str(e)}',
            'data': None
        }), 500

@app_mgr.route('/apps/config/<app_id>', methods=['POST'])
def save_application_config(app_id):
    """保存指定应用的配置信息

    Args:
        app_id: 应用ID

    Returns:
        json: 保存结果消息
    """
    global apps_root, apps
    # 获取请求中的配置数据
    config_data = request.get_json()
    if not config_data:
        return jsonify({
            'status': 'error',
            'message': '配置数据不能为空',
            'data': None
        }), 400
    
    # 构建应用配置文件路径
    app_dir = os.path.join(apps_root, app_id)
    config_path = os.path.join(app_dir, 'config.json')
    
    # 保存配置文件
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        #将config_data中的属性添加到config
        for key in config_data['model_params']:
            config['model_params'][key]['value']=config_data['model_params'][key]
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        return jsonify({
            'status': 'success',
            'message': f'应用 {app_id} 配置保存成功',
            'data': config_data
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'保存应用 {app_id} 配置失败: {str(e)}',
            'data': None
        }), 500

def start_application(app_id):
    """
    启动指定应用的模型，在独立线程中运行
    
    Args:
        app_id: 要启动的应用ID
        
    Returns:
        tuple: (状态消息, HTTP状态码)
    """
    global current_app_id, current_model_thread, current_result_types, current_predict_params
    # 停止当前运行的应用
    stop_current_application()

    try:
        with app_lock:

            if app_id not in apps:
                raise ValueError(f'应用 {app_id} 不存在')

            # 构建应用目录路径
            app_dir = os.path.join(apps_root, app_id)
            config_path = os.path.join(app_dir, 'config.json')

            # 读取推理配置参数
            if not os.path.exists(config_path):
                raise ValueError('配置文件不存在')

            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # 提取推理所需参数
            model_params = config.get('model_params', {})
            params={}
            for key, value in model_params.items():
                if 'value' in value:
                    params[key] = value['value']
            params['device'] = cfg.device

            # 创建并启动模型线程
            current_model_thread = ModelProcess(params)
            current_model_thread.start()

            # 等待模型加载完成（最多等待300秒）
            start_time = time.time()
            while not current_model_thread.is_loaded() and time.time() - start_time < 300:
                if current_model_thread.get_error():
                    raise RuntimeError(f'模型加载失败: {current_model_thread.get_error()}')
                time.sleep(0.5)

            if not current_model_thread.is_loaded():
                raise RuntimeError('模型加载超时')

            # 更新全局状态
            current_app_id = app_id
            current_predict_params = config.get('predict_params', {})
            current_result_types = config.get('result_types', {})

        logging.info(f'应用 {app_id} 已在独立线程启动')

    except Exception as e:
        logging.error(f'启动应用失败: {str(e)}', exc_info=True)
        # 确保线程被正确清理
        if current_model_thread:
            current_model_thread.stop()
            current_model_thread = None
        raise e


def stop_current_application():
    """
    停止当前运行的应用线程
    
    Returns:
        tuple: (状态消息, HTTP状态码)
    """
    global current_app_id, current_model_thread

    try:
        with app_lock:
            if current_model_thread and current_model_thread.is_alive():
                current_model_thread.stop()
                current_model_thread = None
            current_app_id = None
        logging.info('当前应用已停止')
    except Exception as e:
        logging.error(f'停止应用失败: {str(e)}', exc_info=True)
        raise e

def get_apps_status():
    if current_model_thread:
        return '运行中'
    return '未运行'

@app_mgr.route('/apps/start/<app_id>', methods=['GET'])
def start_application_api(app_id):
    """
    启动指定应用的API端点
    """
    try:
        start_application(app_id)
        return json.dumps({'status': 'success', 'message': f'Application {app_id} started successfully'}), 200
    except Exception as e:
        logging.error(f'Failed to start application: {str(e)}')
        return json.dumps({'status': 'error', 'message': f'Failed to start application: {str(e)}'}), 500


@app_mgr.route('/apps/stop', methods=['GET'])
def stop_application_api():
    """
    停止当前应用的API端点
    """
    try:
        stop_current_application()
        return json.dumps({'status': 'success', 'message': f'Application stopped successfully'}), 200
    except Exception as e:
        logging.error(f'Failed to stop application: {str(e)}')
        return json.dumps({'status': 'error', 'message': f'Failed to stop application: {str(e)}'}), 500


@app_mgr.route('/apps/infer/<app_id>/<result_type>', methods=['POST'])
def infer_application(app_id, result_type):
    global current_model_thread, current_app_id, current_result_types, apps, current_predict_params
 
    # 1. 验证应用是否存在
    if app_id not in apps:
        return jsonify({"error": f"应用 {app_id} 不存在"}), 404

    # 2. 确保模型线程已加载且为当前应用
    if current_app_id != app_id or not current_model_thread or not current_model_thread.is_alive() or not current_model_thread.is_loaded():
        logging.error(f"应用 {app_id} 未启动")
        return jsonify({"error": "应用未启动"}), 500
    
    # 3. 验证结果类型是否支持
    if result_type not in current_result_types:
        return jsonify({
            "error": f"不支持的结果类型: {result_type}",
            "supported_types": current_result_types
        }), 400
    
    # 4. 获取请求数据
    try:
        # 处理请求输入数据
        input, temp_files, error_response = process_request_input(request, app_id, apps_root)
        if error_response:
            return error_response
        
        # 从FormData中获取预测参数（支持multipart/form-data格式）
        predict_params_str = request.form.get('predict_params', '{}')
        try:
            predict_params = json.loads(predict_params_str)
        except json.JSONDecodeError:
            return jsonify({"error": "预测参数格式错误: 无效的JSON字符串"}), 400
            
        valid,predict_params, error_msg = check_predict_params(predict_params, current_predict_params)
        if not valid:
            return jsonify({"error": f"预测参数格式错误: {error_msg}"}), 400

        # 调用模型线程进行推理
        try:
            # 创建结果存储和事件
            result = []
            error = None

            # 提交推理任务
            # 创建结果文件存储目录
            result_dir = os.path.join(apps_root, app_id, 'results')
            os.makedirs(result_dir, exist_ok=True)
            task_data = {'input': input, 'predict_params': predict_params, 'result_type': result_type, 'result_dir': result_dir}
            success, task_id = current_model_thread.submit_task(task_data)
            if not success:
                return jsonify({"error": task_id}), 500

            # 等待结果（设置超时）
            start_time = time.time()
            result = None
            error = None
            while time.time() - start_time < 30:
                result_data = current_model_thread.get_result(timeout=1)
                if result_data:
                    task_id_result, result, error = result_data
                    if task_id_result == task_id:
                        break
                time.sleep(0.1)
            
            if not result and not error:
                return jsonify({"error": "推理超时"}), 504
            if error:
                return jsonify({"error": error}), 500

            # 处理不同结果类型
            match result_type:
                case 'img':
                    if result:
                        return send_file(result)
                    else:
                        return jsonify({"error": "未生成图像结果"}), 500
                case 'json':
                    if result:
                        return jsonify(result), 200
                    else:
                        return jsonify({"error": "未生成json结果"}), 500
                case 'html':
                    if result:
                        return result, 200
                    else:
                        return jsonify({"error": "未生成html结果"}), 500
        except Exception as e:
            logging.error(f"推理过程发生错误: {str(e)}", exc_info=True)
            raise
        finally:
            # 清理临时文件
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                        logging.info(f"临时文件已清理: {temp_file}")
                    except Exception as e:
                        logging.warning(f"清理临时文件失败: {str(e)}")

    except Exception as e:
        logging.error(f"解析请求数据失败: {str(e)}")
        return jsonify({"error": "解析请求数据失败，确保请求为JSON格式且包含input_data字段"}), 400


def process_request_input(request, app_id, apps_root):
    """
    处理请求输入数据，支持文件上传和JSON输入
    :param request: Flask请求对象
    :param app_id: 当前应用ID
    :param apps_root: 应用根目录
    :return: tuple(input_data, temp_files, error_response)
             - input_data: 处理后的输入数据
             - temp_files: 需要清理的临时文件列表
             - error_response: 错误响应元组 (response, status_code)，无错误则为None
    """
    temp_files = []
    input_data = None
    
    # 1. 优先处理文件上传
    if 'file' in request.files and request.files['file'].filename != '':
        file = request.files['file']
        # 确保upload目录存在
        upload_dir = os.path.join(apps_root, app_id, 'upload')
        os.makedirs(upload_dir, exist_ok=True)
        
        # 保存上传文件到临时路径
        filename = secure_filename(file.filename)
        temp_file_path = os.path.join(upload_dir, filename)
        file.save(temp_file_path)
        input_data = temp_file_path
        logging.info(f"上传文件已保存至临时路径: {temp_file_path}")
        
        # 添加临时文件清理标记
        temp_files.append(temp_file_path)
    
    # 2. 如果没有文件上传，则尝试从form或JSON获取输入数据
    if input_data is None:
        try:
            # 先尝试从form获取input
            input_data = request.form.get('input')
            if input_data is None:
                # form中没有则尝试从JSON获取
                data = request.get_json()
                if not data or 'input' not in data:
                    return None, temp_files, (jsonify({"error": "请求数据中缺少input字段"}), 400)
                input_data = data['input']
                logging.info(f"使用JSON输入: {str(input_data)[:100]}...")
            else:
                logging.info(f"使用Form输入: {str(input_data)[:100]}...")
        except Exception as e:
            return None, temp_files, (jsonify({"error": "解析请求失败: " + str(e)}), 400)
    
    # 验证输入是否有效
    if input_data is None:
        return None, temp_files, (jsonify({"error": "未提供有效的输入数据"}), 400)
    
    return input_data, temp_files, None


# 检测预测参数是否符合current_predict_params定义
def check_predict_params(predict_params, current_predict_params):
    """
    验证预测参数是否符合定义要求
    :param predict_params: 待验证的参数字典
    :param current_predict_params: 参数定义字典
    :return: (bool, str) 验证结果和错误信息
    """
    errors = []
    params = {}
    for param_name, param_def in current_predict_params.items():
        # 获取参数值，不存在则使用默认值
        param_value = predict_params.get(param_name, param_def.get('default'))
        # 如果参数值为None跳过
        if param_value is None:
            continue
        # 类型检查
        expected_type = param_def['type']
        if expected_type == 'int':
            if not isinstance(param_value, int):
                errors.append(f"{param_name}必须为整数")
        elif expected_type == 'float':
            if not isinstance(param_value, (int, float)):
                errors.append(f"{param_name}必须为数字")
            else:
                param_value = float(param_value)
        elif expected_type == 'dict':
            if not isinstance(param_value, dict):
                errors.append(f"{param_name}必须为字典")
        elif expected_type == 'list':
            if not isinstance(param_value, list):
                errors.append(f"{param_name}必须为列表")

        # 最小值检查
        if 'min' in param_def and param_def['min'] is not None:
            if param_value < param_def['min']:
                errors.append(f"{param_name}不能小于{param_def['min']}")
        
        # 最大值检查
        if 'max' in param_def and param_def['max'] is not None:
            if param_value > param_def['max']:
                errors.append(f"{param_name}不能大于{param_def['max']}")
        
        params[param_name] = param_value
    return len(errors) == 0,params, ", ".join(errors)