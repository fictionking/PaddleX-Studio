from flask import Blueprint, jsonify, request, send_from_directory
import os
import json
import datetime
import subprocess
import sys
import datasetMgr
import paddlexCfg

# 初始化模型管理蓝图
model_bp = Blueprint('model', __name__)

# 全局模型数据变量
models = []
models_root = os.path.join(os.path.dirname(os.path.abspath(__file__)),'models')
models_config_path = os.path.join(models_root, 'models_config.json')

def init():
    """初始化模型数据，从JSON文件加载或创建"""
    global models
    models = load_or_create_models_config()

def load_or_create_models_config():
    """加载或创建模型配置文件，并返回模型数据列表"""
    if not os.path.exists(models_config_path):
        with open(models_config_path, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=4)
        print(f'创建空模型配置文件：{models_config_path}')
        return []
    try:
        with open(models_config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f'配置文件 {models_config_path} 格式错误，重置为空文件')
        with open(models_config_path, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=4)
        return []


def save_model_config(new_model):
    """
    保存模型配置信息到JSON文件（存在则更新，不存在则添加）
    :param new_model: 要保存的模型配置字典（需包含'name'属性）
    """
    global models
    if new_model is not None:
        found = False
        for i, model in enumerate(models):
            if model.get('id') == new_model.get('id'):
                models[i] = new_model
                found = True
                break
        if not found:
            models.append(new_model)
    try:
        with open(models_config_path, 'w', encoding='utf-8') as f:
            json.dump(models, f, ensure_ascii=False, indent=4)
        print(f'成功保存模型配置：{new_model["name"]}')
    except Exception as e:
        print(f'保存模型配置失败：{str(e)}')

@model_bp.route('/models/<modelId>', methods=['GET'])
def get_model_detail(modelId):
    """API接口：根据模型ID获取单个模型详细信息"""
    # 从全局模型列表中查找指定ID的模型
    for model in models:
        if model.get('id') == modelId:
            return jsonify(model)
    # 未找到模型返回404
    return jsonify({'code': 404, 'message': '未找到指定模型'}), 404

@model_bp.route('/models')
def get_models():
    return jsonify(models)  # 返回JSON格式的模型数据

@model_bp.route('/models/<model_id>/delete', methods=['GET'])
def delete_model(model_id):
    if not model_id:
        return jsonify({'code': 400, 'message': '缺少模型ID参数'}), 400

    global models
    # 查找要删除的模型索引
    delete_index = None
    for i, model in enumerate(models):
        if model.get('id') == model_id:
            delete_index = i
            break

    if delete_index is None:
        return jsonify({'code': 404, 'message': '未找到指定模型'}), 404

    # 删除模型
    del models[delete_index]
    # 保存更新后的模型列表
    save_model_config(None)  # 传入None触发全量保存
    return jsonify({'code': 200, 'message': '模型删除成功'})


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
        'fine_tune_time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # 初始化为当前日期时间，精确到秒
        'status': '未开始'  # 初始状态为处理中
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
    model = next((m for m in models if m.get('id') == model_id), None)
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
        
        # 更新图像路径为包含model_id的完整路径
        base_path = f"models/{model_id}/check/"
        check_result['attributes']['train_sample_paths'] = [base_path + path.replace("\\","/") for path in check_result['attributes']['train_sample_paths']]
        check_result['attributes']['val_sample_paths'] = [base_path + path.replace("\\","/") for path in check_result['attributes']['val_sample_paths']]
        check_result['analysis']['histogram'] = base_path + check_result['analysis']['histogram'].replace("\\","/")

        return jsonify({'code': 200,'message': '检查完成','data': check_result})

