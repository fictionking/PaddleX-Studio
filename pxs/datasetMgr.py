from flask import Blueprint, jsonify, request, send_file
import os
import json
import datetime
import time
import threading
import shutil
import zipfile
import tarfile
import mimetypes
import logging
import pxs.paddlexCfg as cfg
# 初始化数据集管理蓝图
dataset_bp = Blueprint('dataset_bp', __name__)

# 定义数据集列表
datasets = []
dataset_root = None
dataset_config_path = None

def init():
    """初始化模型数据，从JSON文件加载或创建"""
    global datasets,dataset_root,dataset_config_path
    dataset_root = cfg.datasets_root
    dataset_config_path = os.path.join(dataset_root, 'dataset_config.json')
    datasets = load_or_create_dataset_config()
    # 获取初始修改时间
    last_modified = os.path.getmtime(dataset_config_path)
    def check_modification():
        nonlocal last_modified
        while True:
            current_modified = os.path.getmtime(dataset_config_path)
            if current_modified != last_modified:
                global datasets
                datasets = load_or_create_dataset_config()
                last_modified = current_modified
                logging.info("数据集配置文件已更新，重新加载成功")
            time.sleep(5)  # 每5秒检查一次
    # 启动配置文件检查后台线程
    threading.Thread(target=check_modification, daemon=True).start()

def load_or_create_dataset_config():
    """加载或创建模型配置文件，并返回模型数据列表"""
    if not os.path.exists(dataset_config_path):
        with open(dataset_config_path, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=4)
        logging.info(f'创建空数据集配置文件：{dataset_config_path}')
        return []
    try:
        with open(dataset_config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        logging.error(f'配置文件 {dataset_config_path} 格式错误，重置为空文件')
        with open(dataset_config_path, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=4)
        return []

@dataset_bp.route('/datasets')  # 数据集接口
def get_datasets():
    """返回JSON格式的数据集数据，支持按category和dataset_type过滤"""
    category = request.args.get('category')
    module = request.args.get('module')
    
    filtered_datasets = datasets
    if category:
        filtered_datasets = [d for d in filtered_datasets if d.get('category').get('id') == category]
    if module:
        filtered_datasets = [d for d in filtered_datasets if d.get('module').get('id') == module]
    
    return jsonify(filtered_datasets)

@dataset_bp.route('/datasets/new', methods=['POST'])  # 新增数据集接口
def add_dataset():
    """新增数据集"""
    data = request.json
    #检测id是否唯一
    if any(d['id'] == data.get('id') for d in datasets):
        return jsonify({'error': '数据集ID已存在'}), 400

    new_dataset = {
            'id': data.get('id'),
            'name': data.get('name'),
            'description': data.get('description'),
            'category': data.get('category', ''),
            'dataset_type': data.get('dataset_type', ''),
            'module': data.get('module', ''),
            'update_time': datetime.datetime.now().isoformat()
        }
    datasets.append(new_dataset)
    save_dataset_config()
    store_dir = os.path.join(dataset_root, new_dataset['id'])
    if not os.path.exists(store_dir):
        # 使用安全目录创建函数
        success, message, error = _create_directory_safely(dataset_root, new_dataset['id'])
        if success:
            logging.info(f"已创建数据集目录: {store_dir}")
        else:
            logging.error(f"创建数据集目录失败: {error}")
            # 回滚数据集添加操作
            datasets.remove(new_dataset)
            save_dataset_config()
            return jsonify({'error': f'创建数据集目录失败: {error}'}), 500
    return jsonify(new_dataset), 201

@dataset_bp.route('/datasets/<dataset_id>', methods=['GET', 'PUT', 'DELETE'])  # 单个数据集接口
def handle_dataset(dataset_id):
    """处理单个数据集的GET、PUT和DELETE请求"""
    dataset = next((d for d in datasets if d['id'] == dataset_id), None)
    if not dataset:
        return jsonify({'error': 'Dataset not found'}), 404
    if request.method == 'GET':
        return jsonify(dataset)
    elif request.method == 'PUT':
        data = request.json
        dataset.update({
                'name': data.get('name', dataset['name']),
                'description': data.get('description', dataset['description']),
                'category': data.get('category', dataset['category']),
                'dataset_type': data.get('dataset_type', dataset['dataset_type']),
                'dataset_type_name': data.get('mdataset_type_name', dataset['dataset_type_name']),
                'type': data.get('type', dataset['type']),
                'update_time': datetime.datetime.now().isoformat()       
            })
        save_dataset_config()
        return jsonify(dataset)
    elif request.method == 'DELETE':
        store_dir = os.path.join(dataset_root, dataset_id)
        if os.path.exists(store_dir):
            shutil.rmtree(store_dir)  # 删除模型目录及其内容
            logging.info(f"已删除数据集目录: {store_dir}")
        datasets.remove(dataset)
        save_dataset_config()
        return jsonify({'message': 'Dataset deleted'}), 204

@dataset_bp.route('/datasets/<dataset_id>/upload', methods=['POST'])
def upload_dataset_file(dataset_id):
    """上传数据集文件并保存到对应目录，如为压缩文件则解压"""
    # 检查数据集是否存在
    dataset = next((d for d in datasets if d['id'] == dataset_id), None)
    if not dataset:
        return jsonify({'error': 'Dataset not found'}), 404
    
    # 检查是否有文件上传
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # 确定保存目录
    store_dir = os.path.join(dataset_root, dataset_id)
    os.makedirs(store_dir, exist_ok=True)
    
    # 获取并处理子目录参数
    directory = request.form.get('directory', '/')
    # 移除开头的斜杠或反斜杠，确保为相对路径
    directory = directory.lstrip('/\\')
    final_dir = os.path.join(store_dir, directory)
    
    # 验证路径安全性，防止路径遍历攻击
    if not os.path.abspath(final_dir).startswith(os.path.abspath(store_dir)):
        return jsonify({'error': 'Invalid directory path'}), 400
    
    # 创建最终保存目录
    os.makedirs(final_dir, exist_ok=True)
    
    # 保存文件到指定子目录
    file_path = os.path.join(final_dir, file.filename)
    file.save(file_path)
    
    # 检查是否为压缩文件并解压到指定子目录
    if file.filename.endswith('.zip'):
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(final_dir)
        os.remove(file_path)  # 删除压缩包
    elif file.filename.endswith(('.tar', '.tar.gz', '.tar.bz2', '.tar.xz')):
        with tarfile.open(file_path, 'r') as tar_ref:
            tar_ref.extractall(final_dir)
        os.remove(file_path)  # 删除压缩包
    
    return jsonify({'message': 'File uploaded and processed successfully'}), 200

@dataset_bp.route('/datasets/<dataset_id>/mkdir', methods=['POST'])
def create_dataset_directory(dataset_id):
    """在数据集目录下创建新目录

    接收目录名称参数，在指定数据集目录下创建新目录，并返回创建结果
    """
    # 检查数据集是否存在
    dataset = next((d for d in datasets if d['id'] == dataset_id), None)
    if not dataset:
        return jsonify({'error': 'Dataset not found'}), 404
    
    # 获取请求数据
    data = request.json
    dir_name = data.get('dir_name')
    if not dir_name:
        return jsonify({'error': 'Directory name is required'}), 400
    
    # 构建目录路径
    dataset_dir = os.path.join(dataset_root, dataset_id)
    new_dir_path = os.path.join(dataset_dir, dir_name)
    
    # 安全检查：确保新目录在数据集目录内
    if not os.path.abspath(new_dir_path).startswith(os.path.abspath(dataset_dir)):
        return jsonify({'error': 'Access denied: invalid directory path'}), 403
    
    # 创建目录
    success, message, error = _create_directory_safely(dataset_dir, dir_name)
    if success:
        return jsonify({
            'message': message,
            'path': dir_name
        }), 201
    elif error == 'Access denied: invalid directory path':
        return jsonify({'error': error}), 403
    elif error.startswith('Directory "') and error.endswith('already exists'):
        return jsonify({'error': error}), 409
    else:
        return jsonify({'error': error}), 500

@dataset_bp.route('/datasets/<dataset_id>/files', methods=['GET'])
def get_dataset_files(dataset_id):
    """获取数据集目录下的文件列表，以树形结构返回包含嵌套子目录"""
    # 检查数据集是否存在
    dataset = next((d for d in datasets if d['id'] == dataset_id), None)
    if not dataset:
        return jsonify({'error': 'Dataset not found'}), 404
    
    # 确定数据集目录路径
    store_dir = os.path.join(dataset_root, dataset_id)
    if not os.path.exists(store_dir):
        return jsonify({'error': 'Directory not found'}), 404
    
    # 递归构建目录树结构
    def build_directory_tree(path, current_relative_path=""):
        tree_node = {
            'name': os.path.basename(path),
            'type': 'directory',
            'path': current_relative_path,
            'children': []
        }
        try:
            with os.scandir(path) as entries:
                for entry in entries:
                    if entry.is_dir(follow_symlinks=False):
                        # 递归处理子目录
                        new_relative_path = f"{current_relative_path}/{entry.name}" if current_relative_path else entry.name
                        tree_node['children'].append(build_directory_tree(entry.path, new_relative_path))
                    else:
                        # 添加文件信息
                        stat = entry.stat()
                        tree_node['children'].append({
                            'name': entry.name,
                            'type': 'file',
                            'path': f"{current_relative_path}/{entry.name}" if current_relative_path else entry.name,
                            'size': stat.st_size,
                            'modified_time': datetime.datetime.fromtimestamp(stat.st_mtime).isoformat()
                        })
        except PermissionError:
            tree_node['error'] = 'Permission denied'
        return tree_node
    
    # 生成目录树并返回
    directory_tree = build_directory_tree(store_dir)
    return jsonify(directory_tree)

@dataset_bp.route('/datasets/<dataset_id>/files/<path:file_path>', methods=['GET'])
def preview_dataset_file(dataset_id, file_path):
    """预览数据集目录下的文件内容，HTML文件直接返回，大文本文件返回部分内容"""
    # 检查数据集是否存在
    dataset = next((d for d in datasets if d['id'] == dataset_id), None)
    if not dataset:
        return jsonify({'error': 'Dataset not found'}), 404
    
    # 构建完整文件路径
    dataset_dir = os.path.join(dataset_root, dataset_id)
    full_path = os.path.join(dataset_dir, file_path)
    
    # 安全检查：确保文件在数据集目录内
    if not os.path.abspath(full_path).startswith(os.path.abspath(dataset_dir)):
        return jsonify({'error': 'Access denied'}), 403
    
    # 检查文件是否存在
    if not os.path.exists(full_path) or not os.path.isfile(full_path):
        return jsonify({'error': 'File not found'}), 404
    
    # 获取文件MIME类型
    mime_type, _ = mimetypes.guess_type(full_path)
    is_text_file = mime_type and (mime_type.startswith('text/') or mime_type in ['application/json', 'application/javascript'])
    is_image_file = mime_type and mime_type.startswith('image/')
    
    # 处理图片类型文件
    if is_image_file:
        try:
            return send_file(full_path, mimetype=mime_type)
        except Exception as e:
            return jsonify({'error': f'Failed to send image: {str(e)}'}), 500
    
    # 处理文本类型文件
    if is_text_file:
        # 读取文件内容（限制大小）
        max_preview_size = 1024 * 100  # 100KB
        truncated = False
        content = ''
        
        try:
            with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read(max_preview_size)
                # 检查是否还有更多内容
                if f.read(1):
                    truncated = True
                    content += '\n\n[内容已截断，文件过大]'
        except Exception as e:
            return jsonify({'error': f'Failed to read file: {str(e)}'}), 500
        
        return jsonify({
            'file_path': file_path,
            'mime_type': mime_type,
            'truncated': truncated,
            'content': content
        })
    
    # 不支持的文件类型
    return jsonify({
        'error': 'Unsupported file type',
        'mime_type': mime_type,
        'supported_types': 'text/*, application/json, application/javascript, image/*'
    }), 415

@dataset_bp.route('/datasets/<dataset_id>/files/dl/<path:file_path>', methods=['GET'])
def download_dataset_file(dataset_id, file_path):
    # 检查数据集是否存在
    dataset = next((d for d in datasets if d['id'] == dataset_id), None)
    if not dataset:
        return jsonify({'error': 'Dataset not found'}), 404
    
    # 构建完整文件路径
    dataset_dir = os.path.join(dataset_root, dataset_id)
    full_path = os.path.join(dataset_dir, file_path)
    
    # 安全检查：确保文件在数据集目录内
    if not os.path.abspath(full_path).startswith(os.path.abspath(dataset_dir)):
        return jsonify({'error': 'Access denied'}), 403
    
    # 检查文件是否存在
    if not os.path.exists(full_path) or not os.path.isfile(full_path):
        return jsonify({'error': 'File not found'}), 404
    
    # 获取文件MIME类型
    mime_type, _ = mimetypes.guess_type(full_path)
    try:
        return send_file(full_path, mimetype=mime_type)
    except Exception as e:
        return jsonify({'error': f'Failed to send file: {str(e)}'}), 500

@dataset_bp.route('/datasets/<dataset_id>/files/delete', methods=['DELETE'])
def delete_dataset_files(dataset_id):
    """删除数据集目录下的文件或目录列表"""
    # 检查数据集是否存在
    dataset = next((d for d in datasets if d['id'] == dataset_id), None)
    if not dataset:
        return jsonify({'error': 'Dataset not found'}), 404
    
    # 获取要删除的路径列表
    data = request.json
    if not data or 'paths' not in data or not isinstance(data['paths'], list):
        return jsonify({'error': 'Invalid request, paths list required'}), 400
    paths_to_delete = data['paths']
    
    # 确定数据集目录
    dataset_dir = os.path.join(dataset_root, dataset_id)
    results = []
    
    for path in paths_to_delete:
        # 构建完整路径
        full_path = os.path.join(dataset_dir, path)
        result = {
            'path': path,
            'success': False,
            'error': None
        }
        
        # 如果是datset_dir则不能删除
        if os.path.abspath(full_path) == os.path.abspath(dataset_dir):
            return jsonify({'error': 'Root directory cannot be deleted'}), 400

        # 安全检查：确保在数据集目录内
        if not os.path.abspath(full_path).startswith(os.path.abspath(dataset_dir)):
            result['error'] = 'Access denied: path outside dataset directory'
            results.append(result)
            continue
        
        # 检查路径是否存在
        if not os.path.exists(full_path):
            result['error'] = 'Path not found'
            results.append(result)
            continue
        
        # 执行删除
        try:
            if os.path.isfile(full_path):
                os.remove(full_path)
            elif os.path.isdir(full_path):
                shutil.rmtree(full_path)
            result['success'] = True
        except Exception as e:
            result['error'] = str(e)
        
        results.append(result)
    
    # 返回删除结果
    return jsonify({
        'results': results,
        'total': len(results),
        'success_count': sum(1 for r in results if r['success'])
    }),204

def _create_directory_safely(base_dir, relative_path):
    """安全地创建目录
    
    在指定的基础目录下创建相对路径的目录，确保不会跳出基础目录，并处理创建过程中的异常
    
    Args:
        base_dir: 基础目录路径
        relative_path: 相对于基础目录的新目录路径
        
    Returns:
        tuple: (success, message, error)
            - success: 布尔值，表示是否创建成功
            - message: 成功时的消息
            - error: 失败时的错误信息
    """
    new_dir_path = os.path.join(base_dir, relative_path)
    
    # 安全检查：确保新目录在基础目录内
    if not os.path.abspath(new_dir_path).startswith(os.path.abspath(base_dir)):
        return False, None, 'Access denied: invalid directory path'
    
    try:
        os.makedirs(new_dir_path, exist_ok=False)
        return True, f'Directory "{relative_path}" created successfully', None
    except FileExistsError:
        return False, None, f'Directory "{relative_path}" already exists'
    except Exception as e:
        return False, None, f'Failed to create directory: {str(e)}'

def save_dataset_config():
    """保存数据集配置到JSON文件"""
    with open(dataset_config_path, 'w', encoding='utf-8') as f:
        json.dump(datasets, f, ensure_ascii=False, indent=4)