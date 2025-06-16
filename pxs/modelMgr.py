from flask import Blueprint, jsonify, request, send_from_directory
import os
import json
import datetime
import subprocess
import sys
import pxs.datasetMgr as datasetMgr
import pxs.paddlexCfg as paddlexCfg
from pxs.utils import copy_files
import shutil
import threading
import time
# 初始化训练队列相关变量（全局作用域）
import queue
from threading import Lock

task_queue = queue.Queue()
lock = Lock()
# 初始化模型管理蓝图
model_bp = Blueprint('model', __name__)

# 全局模型数据变量
modules = []
models = {}
models_root = os.path.join(os.getcwd(),'models')
models_config_path = os.path.join(models_root, 'models_config.json')
abort_model_id = None

def init():
    """初始化模型管理模块"""
    global modules
    # 从配置文件加载模块信息
    config_path = os.path.join(os.getcwd(), 'modules.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        modules = json.load(f)

    """初始化模型数据，从JSON文件加载或创建，并通过轮询监听配置文件变化"""
    global models
    models = load_or_create_models_config()
    resetModelsStatus()
    # 获取初始修改时间
    last_modified = os.path.getmtime(models_config_path)
    
    def check_modification():
        nonlocal last_modified
        while True:
            current_modified = os.path.getmtime(models_config_path)
            if current_modified != last_modified:
                global models
                models = load_or_create_models_config()
                last_modified = current_modified
                print("模型配置文件已更新，重新加载成功")
            time.sleep(5)  # 每5秒检查一次
    # 启动训练队列处理线程
    threading.Thread(target=process_tasks, daemon=True).start()
    # 启动配置文件检查后台线程
    threading.Thread(target=check_modification, daemon=True).start()

def resetModelsStatus():
    changed=False
    for model in models.values():
        match model['status']:
            case 'queued':
                model['status'] = 'config'
                changed = True
            case 'training':
                model['status'] = 'config'
                changed = True
            case _:
                pass
    if changed:
        save_model_config()

# 定义任务处理函数
def process_tasks():
    global task_queue,lock, abort_model_id
    while True:
        time.sleep(1)  # 队列空时等待1秒，避免频繁检查
        with lock:
            if task_queue.empty():
                continue
            model_id, cmd, train_log_path = task_queue.get()
        abort_model_id = None
        run_subprocess(model_id,cmd,train_log_path)

# 定义线程函数：运行subprocess并等待完成
def run_subprocess(modelid,command,log_path):
    model = models[modelid]
    if model==None:
        return
    model['status'] = 'training'  # 更新模型状态为完成
    save_model_config(model) 
    # 打开日志文件（追加模式，避免覆盖历史日志）
    target_encoding = 'gbk' if sys.platform == 'win32' else 'utf-8'
    with open(log_path, 'w', encoding=target_encoding) as log_file:
        # 复制当前环境变量并设置PYTHONIOENCODING为utf-8，避免子程序用gbk解码
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = target_encoding
        process = subprocess.Popen(
            command,
            stdout=log_file,  # 标准输出仍丢弃
            stderr=subprocess.STDOUT,  # 标准错误输出到日志文件
            text=True,
            encoding=target_encoding,  # 确保日志文件使用utf-8编码
            # errors='ignore',  # 忽略解码错误
            env=env  # 传递修改后的环境变量
        )
        # 循环检查进程状态和中止信号（每0.5秒检查一次）
        while True:
            # 检查子进程是否已结束
            if process.poll() is not None:
                log_file.write(f"训练结束，返回码: {process.returncode}\n")
                # 训练完成后更新模型状态
                model['status'] = 'finished'  # 更新模型状态为完成
                save_model_config(model)  # 保存模型配置
                print(f"模型 {modelid} 训练完成")
                break
            # 检查是否收到中止指令（假设abort_model_id是全局共享的中止标记）
            if abort_model_id == modelid:
                # 根据操作系统类型选择终止方式
                if sys.platform == 'win32':
                    # Windows: 使用taskkill终止主进程及所有子进程
                    subprocess.run(["taskkill", "/F", "/T", "/PID", str(process.pid)], check=False)
                else:
                    # Linux: 使用killpg终止进程组（包含所有子进程）
                    try:
                        pgid = os.getpgid(process.pid)  # 获取进程组ID
                        os.killpg(pgid, os.SIGTERM)     # 发送终止信号
                    except OSError:
                        pass  # 进程可能已终止
                process.wait()  # 等待进程完全终止
                log_file.write("训练已被中止\n")
                model['status'] = 'aborted'  # 更新状态为中止
                save_model_config(model)
                break
            time.sleep(0.5)  # 短暂休眠减少CPU占用
        
    
        
def load_or_create_models_config():
    """加载或创建模型配置文件，并返回以model id为键的字典"""
    if not os.path.exists(models_config_path):
        with open(models_config_path, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=4)
        print(f'创建空模型配置文件：{models_config_path}')
        return {}
    try:
        with open(models_config_path, 'r', encoding='utf-8') as f:
            models_list = json.load(f)
            # 将列表转换为以id为键的字典（假设每个model都有唯一的id字段）
            return {model['id']: model for model in models_list}
    except json.JSONDecodeError:
        print(f'配置文件 {models_config_path} 格式错误，重置为空文件')
        with open(models_config_path, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=4)
        return {}
    except KeyError as e:
        print(f'模型配置文件中存在缺失id字段的模型：{str(e)}，重置为空文件')
        with open(models_config_path, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=4)
        return {}
    except Exception as e:
        print(f'加载模型配置文件时发生未知错误：{str(e)}，返回空字典')
        return {}



def save_model_config(new_model=None):
    """
    保存模型配置信息到JSON文件（存在则更新，不存在则添加），始终保存为数组格式
    :param new_model: 要保存的模型配置字典（需包含'id'和'name'属性）
    """
    global models
    if new_model is not None:
        model_id = new_model.get('id')
        # 更新或添加模型到字典
        models[model_id] = new_model
        # 转换为数组用于保存
    models_list = list(models.values())
    with open(models_config_path, 'w', encoding='utf-8') as f:
        # 始终保存为数组格式
        json.dump(models_list, f, ensure_ascii=False, indent=4)

@model_bp.route('/models/<modelId>', methods=['GET','DELETE'])
def handle_model(modelId):
    model=models.get(modelId)
    if not model:
        # 未找到模型返回404
        return jsonify({'message': '未找到指定模型'}), 404
    if request.method == 'GET':
        return jsonify(model)
    elif request.method == 'DELETE':
        # 删除模型
        model_dir = os.path.join(models_root, modelId)
        if os.path.exists(model_dir):
            shutil.rmtree(model_dir)  # 删除模型目录及其内容
            print(f"已删除模型目录: {model_dir}")
        models.pop(modelId, None)  # 从模型字典中删除
        # 保存更新后的模型列表
        save_model_config(None)  # 传入None触发全量保存
        return jsonify({'message': '模型删除成功'}),204
    

@model_bp.route('/models')
def get_models():
    return jsonify(list(models.values()))  # 返回JSON格式的模型数据

@model_bp.route('/models/new', methods=['POST'])
def new_model():
    model_data = request.get_json()
    # 转换为符合models配置的格式（补充category和module字段）
    formatted_model = {
        'name': model_data['name'],
        'id': model_data['id'], 
        'description': model_data['description'],
        'category': model_data['category'],
        'module_id': model_data['module_id'], 
        'module_name': model_data['module_name'],
        'pretrained': model_data['pretrained'],
        'update_time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # 初始化为当前日期时间，精确到秒
        'status': 'config',  # 初始状态为配置中（数据准备阶段）,config:配置中、training:训练中、finished:运行完成
        'step': 0  # 新增步骤字段（0:数据准备，1:参数准备，2:提交训练）
    }
    save_model_config(formatted_model)
    return {'code': 200, 'message': '保存成功'}

@model_bp.route('/models/<model_id>/check/<path:filename>')
def send_check_dataset_file(model_id, filename):
    check_path = os.path.join(models_root, model_id, 'check')
    return send_from_directory(check_path, filename)

@model_bp.route('/models/<model_id>/check', methods=['POST'])
def checkDataSet(model_id):
    check_data = request.get_json()
    dataset_id = check_data.get('dataset_id')
    # 查找模型
    model = models[model_id]
    if not model:
        return jsonify({'code': 404,'message': '未找到指定模型'}), 404
    # 查找数据集
    dataset = next((d for d in datasetMgr.datasets if d.get('id') == dataset_id), None)
    if not dataset:
        return jsonify({'code': 404,'message': '未找到指定数据集'}), 404
    # 运行检查命令
    yaml_path = os.path.join(paddlexCfg.paddlex_root, "paddlex","configs","modules", model['module_id'], model['pretrained']+".yaml")
    dataset_path = os.path.join(datasetMgr.dataset_root, dataset_id)
    check_path = os.path.join(models_root, model_id, 'check')
    result = subprocess.run(
        [sys.executable, paddlexCfg.paddlex_main, 
        "-c",yaml_path,
        "-o", "Global.mode=check_dataset",
        "-o","Global.output="+check_path,
        "-o", "Global.dataset_dir="+dataset_path,
        "-o", "CheckDataset.convert.enable=True",
        "-o", "CheckDataset.convert.src_dataset_type="+dataset['type']],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    # 保存运行输出到日志文件
    with open(os.path.join(check_path, 'check_dataset.log'), 'w', encoding='utf-8') as f:
        # 处理可能的None值（subprocess可能返回None）
        stdout = result.stdout if result.stdout is not None else ''
        stderr = result.stderr if result.stderr is not None else ''
        f.write(f"STDOUT:\n{stdout}\n\nSTDERR:\n{stderr}")
        
    if result.returncode != 0:
        print(f"检查失败: {result.stderr}")
        return jsonify({'code': 500,'message': '检查失败'}), 200
    else:
        # 读取检查结果文件内容
        with open(os.path.join(check_path, 'check_dataset_result.json'), 'r', encoding='utf-8') as f:
            check_result = json.load(f)
        model['step'] = 1
        save_model_config(model) 
        # 更新图像路径为包含model_id的完整路径
        base_path = f"models/{model_id}/check/"
        check_result['attributes']['train_sample_paths'] = [base_path + path.replace("\\","/") for path in check_result['attributes']['train_sample_paths']]
        check_result['attributes']['val_sample_paths'] = [base_path + path.replace("\\","/") for path in check_result['attributes']['val_sample_paths']]
        check_result['analysis']['histogram'] = base_path + check_result['analysis']['histogram'].replace("\\","/")

        return jsonify({'code': 200,'message': '检查完成','data': check_result})


@model_bp.route('/models/<model_id>/train', methods=['POST'])
def train(model_id):
    # 获取请求参数（需与前端约定参数名）：
    # {
    #     epochs: 100,
    #     batchSize: 8,
    #     classNum: 4,
    #     learningRate: 0.00010,
    #     warmUpSteps: 100,
    #     logInterval: 10,
    #     trainEvalInterval: 1
    # }
    params = request.get_json()
     # 查找模型
    model = models[model_id]
    if not model:
        return jsonify({'code': 404,'message': '未找到指定模型'}), 404
    yaml_path = os.path.join(paddlexCfg.paddlex_root, "paddlex","configs","modules", model['module_id'], model['pretrained']+".yaml")
    output_dir = os.path.join(models_root, model_id, 'train')
    dataset_dir = os.path.join(models_root, model_id, 'dataset')
    # 删除已存在的训练目录
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    # 逐级查找匹配的预训练模型路径
    pretrained_model = None
    for category_item in modules:
        # 匹配category
        if category_item['category'] != model['category']:
            continue
        # 匹配module_id
        for module_item in category_item['modules']:
            if module_item['id'] != model['module_id']:
                continue
            # 匹配pretrained.name
            for pretrained_item in module_item['pretrained']:
                if pretrained_item['name'] == model['pretrained']:
                    pretrained_model = pretrained_item['pretrained_model']
                    break
            if pretrained_model:
                break
        if pretrained_model:
            break
    # 从url中提取文件名
    pretrained_file_name = os.path.basename(pretrained_model)
    # 构建完整的预训练模型路径
    pretrain_weight_path = os.path.join(paddlexCfg.pretrained_root, pretrained_file_name)
    # 检查预训练模型是否存在
    if not os.path.exists(pretrain_weight_path):
        pretrain_weight_path=pretrained_model
        
    # 构建训练命令（参考checkDataSet使用sys.executable和paddlex_main）
    cmd = [
        sys.executable,  # 使用当前环境的Python解释器（替代硬编码的'python'）
        paddlexCfg.paddlex_main,  # 使用paddlex主脚本路径（替代硬编码的'main.py'）
        '-c', yaml_path,
        '-o', f'Global.mode=train',
        '-o', f'Global.output={output_dir}',
        '-o', f'Global.dataset_dir={dataset_dir}',
        '-o', f'Global.device={paddlexCfg.device}',
        '-o', f'Train.epochs_iters={params.get("epochs")}',
        '-o', f'Train.batch_size={params.get("batchSize")}',
        '-o', f'Train.num_classes={params.get("classNum")}',
        '-o', f'Train.learning_rate={params.get("learningRate")}',
        '-o', f'Train.warmup_steps={params.get("warmUpSteps")}',
        '-o', f'Train.log_interval={params.get("logInterval")}',
        '-o', f'Train.eval_interval={params.get("trainEvalInterval")}',
        '-o', f'Train.pretrain_weight_path="{pretrain_weight_path}"'
    ]

    # 创建训练日志目录
    train_log_dir = os.path.join(output_dir, 'logs')
    os.makedirs(train_log_dir, exist_ok=True)
    train_log_path = os.path.join(train_log_dir, 'train.log')

    # 主逻辑：检查队列状态并添加任务
    with lock:
        task_queue.put((model_id, cmd, train_log_path))
    model['status'] = 'queued'
    save_model_config(model)  # 保存模型配置
    return jsonify({  # 返回包含日志路径的信息供前端轮询
        'code': 200,
        'message': '训练任务已加入队列' if model['status'] == 'queued' else '训练已启动',
        'log_path': f'/models/{model_id}/train/log'
    })

@model_bp.route('/models/<model_id>/train/log', methods=['GET'])
def get_train_log(model_id):
    """获取训练实时日志接口"""
    # 检查模型是否存在
    model = models[model_id]
    if not model:
        return jsonify({'code': 404, 'message': '未找到指定模型'}), 404
    if model['status'] == 'queued':
        return jsonify({'code': 200,'data': '训练任务已加入队列'})   
    # 构建日志路径
    output_dir = os.path.join(models_root, model_id, 'train')
    train_log_path = os.path.join(output_dir, 'logs','train.log')
    
    # 读取日志内容（最多返回最后1000行防止内存溢出）
    try:
        # 动态判断编码：Windows使用gbk，其他系统使用utf-8
        target_encoding = 'gbk' if sys.platform == 'win32' else 'utf-8'
        with open(train_log_path, 'r', encoding=target_encoding) as f:
            lines = f.readlines()
            # 取最后1000行保证实时性
            log_content = ''.join(lines[-1000:]) if len(lines) > 1000 else ''.join(lines)
        if log_content=='':
            log_content = '正在启动训练...'
        return jsonify({'code': 200, 'status':model['status'],'data': log_content})
    except FileNotFoundError:
        return jsonify({'code': 404, 'message': '日志文件未生成或训练未启动'}), 404

@model_bp.route('/models/<model_id>/train/stop', methods=['GET'])
def stop_train(model_id):
    """停止训练接口"""
    # 检查模型是否存在
    model = models[model_id]
    if not model:
        return jsonify({'code': 404,'message': '未找到指定模型'}), 404
    if model['status'] == 'queued':
        # 从队列中删除任务（保留其他任务）
        with lock:
            # 取出所有任务到临时列表
            temp_tasks = []
            while not task_queue.empty():
                temp_tasks.append(task_queue.get())
            # 过滤目标任务并重新入队其他任务
            for task in temp_tasks:
                if task[0] == model_id:
                    print(f"已从队列中删除模型 {model_id} 的训练任务")
                else:
                    task_queue.put(task)
        model['status'] = 'config'
        save_model_config(model)  # 保存模型配置
        return jsonify({'code': 200,'message': '训练任务已停止'}), 200
    elif model['status'] == 'training':
        global abort_model_id
        with lock:
            abort_model_id = model_id
        return jsonify({'code': 200,'message': '训练已停止'}), 200
    else:
        return jsonify({'code': 400,'message': '当前训练状态无法停止'}), 400

@model_bp.route('/models/<model_id>/<status>/<step>', methods=['GET'])
def setStatus(model_id,status,step):
    model = models[model_id]
    if not model:
        return jsonify({'code': 404,'message': '未找到指定模型'}), 404
    try:
        model['status'] = status
        model['step'] = int(step)
        save_model_config(model)  # 保存模型配置
        return jsonify({'code': 200,'message': '模型状态已更新'})
    except ValueError:
        return jsonify({'code': 400,'message': '无效的状态值'}), 400

@model_bp.route('/models/<model_id>/copyds', methods=['POST'])
def copydataset(model_id):
    check_data = request.get_json()
    dataset_id = check_data.get('dataset_id')
    # 查找模型
    model = models[model_id]
    if not model:
        return jsonify({'code': 404,'message': '未找到指定模型'}), 404
    # 查找数据集
    dataset = next((d for d in datasetMgr.datasets if d.get('id') == dataset_id), None)
    if not dataset:
        return jsonify({'code': 404,'message': '未找到指定数据集'}), 404
    # 复制数据集到模型目录
    dataset_path = os.path.join(datasetMgr.dataset_root, dataset_id)
    model_path = os.path.join(models_root, model_id,'dataset')
    # 根据模型的类型选择复制方式
    match model['module_id']:
        case 'object_detection':
            copyCOCODetDataset(dataset_path,model_path)
    model['update_time'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 更新时间
    save_model_config(model)
    return jsonify({'code': 200,'message': '复制完成','data': model})

def copyCOCODetDataset(dataset_path,model_path):
    # 复制annotations和images目录到模型目录
    annotations_path = os.path.join(dataset_path, 'annotations')
    model_annotations_path = os.path.join(model_path, 'annotations')
    images_path = os.path.join(model_path, 'images')
    # 如果目录存在则清空
    if os.path.exists(model_annotations_path):
        shutil.rmtree(model_annotations_path)
    if os.path.exists(images_path):
        shutil.rmtree(images_path)
    files = [{"src":os.path.join(annotations_path,'instance_train.json'),"dst":model_annotations_path},
             {"src":os.path.join(annotations_path,'instance_val.json'),"dst":model_annotations_path},
             {"src":os.path.join(dataset_path, 'images'),"dst":images_path}]
    copy_files(files)

