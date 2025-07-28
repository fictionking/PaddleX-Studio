import os
import json
import requests
import tarfile
from flask import Blueprint, jsonify, stream_with_context, Response,request
import pxs.paddlexCfg as cfg
from pxs.appMgr import new_applications
import time
import logging
import shutil
import yaml
from paddlex.inference.utils.official_models import OFFICIAL_MODELS as OFFICIAL_MODELS_INFER
# 创建蓝图
define_bp = Blueprint('define', __name__)

modules = []
dataset_types = []
cancel_cache=False
train_params={}
def init():
    global modules
    global dataset_types
    global train_params
    modules = load_module_definitions()
    dataset_types = load_dataset_type_definitions()
    train_params=load_train_params()

def load_train_params():
    train_params_path = os.path.join(os.getcwd(), 'define', 'train_parameters.json')
    try:
        with open(train_params_path, 'r', encoding='utf-8') as f:
            train_params = json.load(f)
    except Exception as e:
        logging.error(f"加载训练参数失败: {str(e)}")
        return {}
    return train_params

def load_module_definitions():
    # 读取分类信息
    category_info_path = os.path.join(os.getcwd(), 'define', 'module', 'category_info.json')
    try:
        with open(category_info_path, 'r', encoding='utf-8') as f:
            categories = json.load(f)
    except Exception as e:
        logging.error(f"加载分类信息失败: {str(e)}")
        return []

    result = []
    for category in categories:
        category_id = category.get('id')
        if not category_id:
            continue

        # 构建分类目录路径
        category_dir = os.path.join(os.getcwd(), 'define', 'module', category_id)
        if not os.path.isdir(category_dir):
            continue

        modules_define = []
        # 遍历分类目录下的所有模型定义文件
        for filename in os.listdir(category_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(category_dir, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        module = json.load(f)
                        module=parse_module_define(module)
                        modules_define.append(module)
                except Exception as e:
                    logging.error(f"加载模型定义文件 {filename} 失败: {str(e)}")
                    continue

        result.append({
            'category': category,
            'modules': modules_define
        })

    return result

def parse_module_define(module):
    #从paddlex\configs\modules中读取对应的模型清单合并
    module_dir=os.path.join(cfg.paddlex_root,'paddlex','configs', 'modules', module['id'])
    if not os.path.isdir(module_dir):
        return module
    #读取module_dir下的所有yml文件
    for filename in os.listdir(module_dir):
        if filename.endswith('.yaml') or filename.endswith('.yml'):
            file_path = os.path.join(module_dir, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    model_yml = yaml.safe_load(f)
                    model_name=model_yml['Global']['model']
                    pretrain_weight_path=model_yml.get('Train', {}).get('pretrain_weight_path', '')
                    if not pretrain_weight_path:
                        pretrain_weight_path=''
                    inference_weight_path=OFFICIAL_MODELS_INFER.get(model_name, '')
                    model_define=module['models'].get(model_name, None)
                    if model_define:
                        if 'inference_model_url' not in model_define or model_define['inference_model_url']=='':
                            model_define['inference_model_url']=inference_weight_path
                        if 'pretrained_model_url' not in model_define or model_define['pretrained_model_url']=='':
                            model_define['pretrained_model_url']=pretrain_weight_path
                    else:
                        model_define={
                            'description':'',
                            'inference_model_url':inference_weight_path,
                            'pretrained_model_url':pretrain_weight_path,
                            'model_size':''
                        }
                    model_define['name']=model_name
                    module['models'][model_name]=model_define
            except Exception as e:
                logging.error(f"加载模型定义文件 {filename} 失败: {str(e)}")
                continue
    return module

def load_dataset_type_definitions():
    # 读取分类信息
    define_path = os.path.join(os.getcwd(), 'define', 'dataset', 'dataset.json')
    try:
        with open(define_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"加载数据集类型定义文件失败: {str(e)}")
        return []

def getModule(category_id,module_id):
    for category in modules:
        if category['category']['id'] == category_id:
            for module in category['modules']:
                if module['id'] == module_id:
                    return module
    return None

def getModel(category_id,module_id,model_id):
    module=getModule(category_id,module_id)
    if module:
        model=module['models'][model_id]
        return model
    return None

def getModelByModule(module,model_id):
    if module:
        model=module['models'][model_id]
        return model
    return None

@define_bp.route('/define/modules', methods=['GET'])
def get_module_definitions():
    return jsonify(modules)

@define_bp.route('/define/modules/cached', methods=['GET'])
def get_module_cached_models():
    #获取weights所有子目录名称返回
    cached_models=[]
    weights_dir=os.path.join(cfg.weights_root)
    for dir in os.listdir(weights_dir):
        cached_models.append(dir)
    return jsonify(cached_models)

@define_bp.route('/define/dataset_types', methods=['GET'])
def get_dataset_type_definitions():
    return jsonify(dataset_types)

@define_bp.route('/define/module/<category_id>/<module_id>/<model_id>/cacheModel', methods=['GET'])
def get_module_cache_model(category_id, module_id, model_id):
    """
    下载模型文件并返回实时进度，支持同时下载pretrained和inference模型，tar格式自动解压
    
    参数:
    - category_id: 类别ID
    - module_id: 模块ID
    - model_id: 模型ID
    
    返回:
    - 流式响应，包含下载进度信息（text/event-stream）
    """
    # 从配置文件中获取缓存路径
    cache_dir = os.path.join(cfg.weights_root,model_id)
    pretrained_model_url = None
    inference_model_url = None 
    model=getModel(category_id,module_id,model_id)
    if model:
        pretrained_model_url = model['pretrained_model_url']
        inference_model_url = model['inference_model_url']
    else:
        return jsonify({'error': '没有可下载的模型URL'})
                    
    # 收集需要下载的URL列表
    download_urls = []
    if pretrained_model_url:
        absurl=os.path.abspath(pretrained_model_url)
        #如果和cache_dir相同，则不下载
        if not absurl.startswith(cache_dir):
            download_urls.append(('pretrained', pretrained_model_url))
    
    if inference_model_url:
        absurl=os.path.abspath(inference_model_url)
        #如果和cache_dir相同，则不下载
        if not absurl.startswith(cache_dir):
            download_urls.append(('inference', inference_model_url))
        
    if not download_urls:
        return jsonify({'error': '没有可下载的模型URL'})
    
    # 确保缓存目录存在
    is_new=not os.path.exists(cache_dir)
    os.makedirs(cache_dir, exist_ok=True)
    
    def extract_tar(file_path,dest_path):
        """解压tar文件到同名子目录并删除原tar文件

        增强功能：如果tar包中只包含一个顶层目录，则将该目录下的内容直接解压到目标路径，
        否则保持原行为（将所有内容解压到同名子目录）
        """
        if file_path.endswith('.tar'):
            os.makedirs(dest_path, exist_ok=True)
            # 解压文件
            with tarfile.open(file_path, 'r') as tar:
                # 获取所有成员并分析顶层目录
                members = tar.getmembers()
                top_level_dirs = set()
                for member in members:
                    # 分割路径并获取顶层目录（处理不同操作系统的路径分隔符）
                    if '/' in member.name:
                        parts = member.name.split('/')
                    else:
                        parts = member.name.split('\\')
                    
                    # 过滤空字符串和当前目录符号'.'
                    filtered_parts = [p for p in parts if p not in ('', '.')]
                    
                    top_level = filtered_parts[0]
                    top_level_dirs.add(top_level)
                
                # 如果只有一个顶层目录且存在文件
                if len(top_level_dirs) == 1:
                    top_dir = top_level_dirs.pop()
                    # 提取该目录下的所有文件并调整路径
                    for member in members:
                        if member.name.startswith(f'./{top_dir}/') or member.name.startswith(f'.\\{top_dir}\\'):
                            # 移除顶层目录
                            member.name = member.name[len(top_dir)+3:]
                            tar.extract(member, path=dest_path)
                        elif member.name.startswith(f'{top_dir}/') or member.name.startswith(f'{top_dir}\\'):
                            # 移除顶层目录
                            member.name = member.name[len(top_dir)+1:]
                            tar.extract(member, path=dest_path)
                else:
                    # 正常解压所有文件
                    tar.extractall(path=dest_path)
            #如果有子目录名称与当前模型id相同的，则把子目录内容移动到当前目录
            for dir in os.listdir(dest_path):
                if dir != model_id:
                    continue
                src_dir = os.path.join(dest_path, dir)
                #把src_dir下的子内容移到dest_path，并删除src_dir
                for file in os.listdir(src_dir):
                    src_file = os.path.join(src_dir, file)
                    shutil.move(src_file, dest_path)
                shutil.rmtree(src_dir)
            # 解压完成后删除tar文件
            os.remove(file_path)
            return True
        return False
    
    # 定义流式下载生成器函数
    def download_generator():
        for model_type, url in download_urls:
            try:
                # 从URL中提取文件名（处理可能的查询参数）
                filename = os.path.basename(url.split('?')[0])
                extract_path = os.path.join(cache_dir, model_type)
                save_path = os.path.join(extract_path,filename)
                save_path_tmp = f"{save_path}.tmp"
                os.makedirs(extract_path, exist_ok=True)
                # 发送开始下载事件
                yield f"data: {json.dumps({'status': 'starting', 'type': model_type, 'file': filename,'speed':'-- MB/s','remain_time':'--:--:--'})}\n\n"
                
                # 发送GET请求，流式获取内容
                start_time = time.time()
                with requests.get(url, stream=True, timeout=30) as r:
                    r.raise_for_status()  # 检查HTTP错误状态码
                    total_size = int(r.headers.get('content-length', 0))
                    downloaded_size = 0
                    block_size = 1024 * 10  # 10KB块大小
                    
                    with open(save_path_tmp, 'wb') as f:
                        last_data_time = time.time()
                        global cancel_cache
                        cancel_cache=False
                        for chunk in r.iter_content(chunk_size=block_size):
                            if cancel_cache:
                                raise Exception('取消下载')
                            #超过30秒没有数据则发送心跳包
                            if time.time() - last_data_time > 30:
                                last_data_time = time.time()
                                yield "data: {}\n\n"

                            if chunk:  # 过滤掉保持连接的空块
                                f.write(chunk)
                                downloaded_size += len(chunk)
                                
                                # 计算进度并发送
                                if total_size > 0:
                                    progress = int((downloaded_size / total_size) * 100)
                                    #计算下载速度
                                    speed = downloaded_size / (time.time() - start_time) / 1024 / 1024
                                    speed_str = f"{speed:.2f} MB/s"
                                    #计算剩余时间
                                    remain_time = (total_size - downloaded_size) / 1024 / 1024 / speed
                                    #将剩余时间换算成时:分:秒
                                    hour = int(remain_time / 3600)
                                    min = int((remain_time - hour * 3600) / 60)
                                    sec = int(remain_time - hour * 3600 - min * 60)
                                    remain_time_str = f"{hour}:{min}:{sec}"

                                    yield f"data: {json.dumps({'status': 'downloading', 'type': model_type, 'progress': progress, 'file': filename,'speed':speed_str,'remain_time':remain_time_str})}\n\n"
                
                # 下载完成，先删除已存在文件再重命名临时文件
                if os.path.exists(save_path):
                    os.remove(save_path)
                os.rename(save_path_tmp, save_path)
                
                # 下载完成，检查是否需要解压
                is_tar = extract_tar(save_path,extract_path)
                if is_tar:
                    yield f"data: {json.dumps({'status': 'extracted', 'model_type': model_type, 'filename': filename,'speed':'-- MB/s','remain_time':'--:--:--'})}\n\n"
                
                # 发送完成事件
                yield f"data: {json.dumps({'status': 'completed', 'type': model_type, 'progress': 100, 'file': filename,'speed':'-- MB/s','remain_time':'--:--:--'})}\n\n"
                
            except Exception as e:
                # 捕获并发送错误信息
                if os.path.exists(save_path_tmp):
                    os.remove(save_path_tmp)
                if is_new:
                    shutil.rmtree(cache_dir)
                yield f"data: {json.dumps({'status': 'failed', 'type': model_type, 'error': str(e)})}\n\n"
                return
        
        # 所有文件处理完成
        yield f"data: {json.dumps({'status': 'all_completed'})}\n\n"
    
    # 返回SSE响应
    return Response(stream_with_context(download_generator()), mimetype='text/event-stream')

@define_bp.route('/define/module/cacheModel/cancel', methods=['GET'])
def cancel_cache_model():
    global cancel_cache
    cancel_cache=True
    return jsonify({'status': 'success'})

@define_bp.route('/define/module/createapp', methods=['POST'])
def create_module_app():
    data = request.get_json()
    if not data:
        return jsonify({'message': '请提供应用配置'}),400
    app_id = data['id']
    app_name = data['name']
    category_id=data['category']
    module_id=data['module_id']
    model_name=data['pretrained']

    module = getModule(category_id,module_id)
    if not module:
        return jsonify({'message': '模块不存在'}),400
    model = getModelByModule(module,model_name)
    if not model:
        return jsonify({'message': '模型不存在'}),400
    config=module['infer_params']
    config['model_params']['model_name']={
      "config_able": False,
      "value": model['name']
    }
    infer_path=os.path.join('weights',model['name'],'inference')
    if not os.path.exists(infer_path):
        infer_path=''
    config['model_params']['model_dir']={
      "config_able": False,
      "value": infer_path
    }
    succ,msg=new_applications(app_id,app_name,"module",[category_id,module['name'],model['name']],config)
    if succ:
        return jsonify({'message': '应用创建成功'}),200
    return jsonify({'message': msg}),400

@define_bp.route('/define/module/setModelRate', methods=['POST'])
def setModelRate():
    data = request.get_json()
    if not data:
        return jsonify({'message': '请提供应用配置'}),400
    category_id = data['category_id']
    module_id = data['module_id']
    model_name = data['model_name']
    rate = data['rate']
    module = getModule(category_id,module_id)
    if not module:
        return jsonify({'message': '模块不存在'}),400
    model = getModelByModule(module,model_name)
    if not model:
        return jsonify({'message': '模型不存在'}),400
    model['rate']=rate
    with open(f'define/module/{category_id}/{module["id"]}.json', 'r+',encoding='utf-8') as f:
        data = json.load(f)
        data['models'][model_name]['rate']=rate
        f.seek(0)
        json.dump(data, f, indent=4, ensure_ascii=False)
        f.truncate()
    return jsonify({'message': '设置成功'}),200
