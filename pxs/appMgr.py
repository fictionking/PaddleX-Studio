from flask import Blueprint, jsonify, request,Response
import os
import json
import logging
from werkzeug.utils import secure_filename
from paddlex import create_model
from flask import request
import threading
from io import BytesIO
import pxs.paddlexCfg as cfg

# 全局变量跟踪当前运行的应用和模型
current_app_id = None
current_model = None
current_result_type = None
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
    resetAppsStatus()


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
        with open(apps_config_path, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=4)
        return {}
    except KeyError as e:
        logging.error(f'应用配置文件中存在缺失id字段的应用：{str(e)}，重置为空文件')
        with open(apps_config_path, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=4)
        return {}
    except Exception as e:
        logging.error(f'加载应用配置文件时发生未知错误：{str(e)}，返回空字典')
        return {}

def resetAppsStatus():
    """重置所有应用状态，将异常状态恢复为初始配置状态"""
    changed = False
    for app in apps.values():
        match app['status']:
            case 'starting':
                app['status'] = 'config'
                changed = True
            case 'running':
                app['status'] = 'config'
                changed = True
            case _:
                pass
    if changed:
        save_app_config()


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
    return jsonify(apps.values())

@app_mgr.route('/apps/<app_id>/config', methods=['GET'])
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

@app_mgr.route('/apps/<app_id>/config', methods=['POST'])
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
    
    # 确保应用目录存在
    os.makedirs(app_dir, exist_ok=True)
    
    # 保存配置文件
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=4)
        
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
    启动指定应用的模型，停止当前正在运行的应用（如果有）
    
    Args:
        app_id: 要启动的应用ID
        
    Returns:
        tuple: (状态消息, HTTP状态码)
    """
    global app_lock
    with app_lock:

        global current_app_id, current_model, current_result_type, apps
        
        try:
            # 如果已有应用在运行，先停止它
            if current_app_id is not None and current_app_id != app_id:
                stop_current_application()
            
            # 检查应用是否存在
            if app_id not in apps:
                return json.dumps({'status': 'error', 'message': f'Application {app_id} not found'}), 404
            
            # 构建应用目录路径
            app_dir = os.path.join(apps_root, app_id)
            config_path = os.path.join(app_dir, 'config.json')
            
            # 读取推理配置参数
            if not os.path.exists(config_path):
                return json.dumps({'status': 'error', 'message': 'Config file not found'}), 404
            
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 提取推理所需参数
            # 从配置中获取模型参数和结果类型
            model_params = config.get('model_params', {})
            result_types = config.get('result', {})
            

            # 加载模型
            model = create_model(**model_params)
            
            # 更新全局状态
            current_app_id = app_id
            current_model = model
            current_result_type = result_types
            
            logging.info(f'Application {app_id} started successfully')
            
        except Exception as e:
            raise e


def stop_current_application():
    """
    停止当前运行的应用，释放模型资源
    
    Returns:
        tuple: (状态消息, HTTP状态码)
    """
    global app_lock
    with app_lock:

        global current_app_id, current_model
        
        try:
            if current_app_id is None:
                return json.dumps({'status': 'warning', 'message': 'No application is currently running'}), 200
            
            app_id = current_app_id
            # 释放模型资源
            if current_model is not None:
                try:
                    # 尝试调用PaddleX模型的关闭方法（如果存在）
                    if hasattr(current_model, 'close'):
                        current_model.close()
                    # 如果没有close方法，尝试删除模型释放资源
                    else:
                        del current_model
                except Exception as e:
                    logging.warning(f'Error releasing model resources: {str(e)}')
            
            current_app_id = None
            current_model = None
            
            logging.info(f'Application {app_id} stopped successfully')
        except Exception as e:
            raise e


@app_mgr.route('/apps/<app_id>/start', methods=['POST'])
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


@app_mgr.route('/apps/stop', methods=['POST'])
def stop_application_api():
    """
    停止当前应用的API端点
    """
    try:
        return stop_current_application()
    except Exception as e:
        logging.error(f'Failed to stop application: {str(e)}')
        return json.dumps({'status': 'error', 'message': f'Failed to stop application: {str(e)}'}), 500


@app_mgr.route('/apps/<app_id>/infer/<result_type>', methods=['POST'])
def infer_application(app_id, result_type):
    global current_app_id, current_model, current_result_type, apps
 
    # 1. 验证应用是否存在
    if app_id not in apps:
        return jsonify({"error": f"应用 {app_id} 不存在"}), 404

    # 2. 确保模型已加载且为当前应用
    if current_app_id != app_id or current_model is None:
        try:
            start_application(app_id)
        except Exception as e:
            logging.error(f"启动应用 {app_id} 失败: {str(e)}")
            return jsonify({"error": f"启动应用失败: {str(e)}"}), 500
    
    # 3. 验证结果类型是否支持
    if not current_result_type.get(result_type, False):
        return jsonify({
            "error": f"不支持的结果类型: {result_type}",
            "supported_types": [k for k, v in current_result_type.items() if v]
        }), 400
    
    # 4. 获取请求数据
    try:
        # 初始化临时文件列表
        temp_files = []
        input = None
        
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
            input = temp_file_path
            logging.info(f"上传文件已保存至临时路径: {temp_file_path}")
            
            # 添加临时文件清理标记
            temp_files.append(temp_file_path)
        
        # 2. 如果没有文件上传，则尝试从JSON获取输入数据
        if input is None:
            try:
                data = request.get_json()
                if not data or 'input' not in data:
                    return jsonify({"error": "请求数据中缺少input字段"}), 400
                input = data['input']
                logging.info(f"使用JSON输入: {str(input)[:100]}...")
            except Exception as e:
                return jsonify({"error": "解析JSON请求失败: " + str(e)}), 400
        
        # 验证输入是否有效
        if input is None:
            return jsonify({"error": "未提供有效的输入数据"}), 400
        

        # 调用模型predict方法进行推理
        try:
            # 执行预测，获取generator结果
            prediction_generator = current_model.predict(input)
            
            # 处理generator结果
            # 处理generator结果
            result_type = data.get('result_type', 'json')
            output = []
            img_saved = False
            for result in prediction_generator:
                if result_type == 'img':
                    # 图片类型只取第一个结果
                    if not img_saved:
                        # 获取可视化图像并转换为HTTP响应
                        img = result.get('img')  # 使用get方法，避免KeyError
                        if img:
                            # 将PIL.Image转换为字节流
                            img_byte_arr = BytesIO()
                            img.save(img_byte_arr, format='PNG')
                            img_byte_arr.seek(0)
                            
                            # 创建HTTP响应对象
                            # 添加文件名到响应头
                            output = Response(img_byte_arr, mimetype='image/png', headers={
                                'Content-Disposition': 'inline; filename="result.png"'
                            })
                            img_saved = True
                            break  # 处理完第一个后跳出循环
                else:
                    # 根据结果类型获取对应属性
                    if result_type == 'str':
                        output.append(result.str)
                    elif result_type == 'json':
                        output.append(result.json)
                    elif result_type == 'html':
                        output.append(result.html)
                    else:
                        raise ValueError(f"不支持的结果类型: {result_type}")
            
            # 记录处理样本数量
            sample_count = len(output) if result_type != 'img' else (1 if img_saved else 0)
            logging.info(f"推理完成，共处理 {sample_count} 个样本")
            
            return output
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
    