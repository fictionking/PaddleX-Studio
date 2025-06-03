from flask import Flask, request, jsonify, render_template, send_from_directory, send_file
import os
import json
import datetime
import subprocess
import sys
# 初始化Flask应用
app = Flask(__name__, template_folder='templates')  # 明确模板目录

paddlex_root = os.path.dirname('C:\\UGit\\PaddleX\\')
paddlex_main = os.path.join(paddlex_root,'main.py')

@app.route('/')
def index():
    """首页路由，返回平台介绍信息"""
    return render_template('index.html')  # 仅渲染模板

@app.route('/app.js')
def send_app_js():
    """提供app.js静态文件"""
    return send_from_directory('templates', 'app.js')

@app.route('/components/<path:filename>')
def send_components(filename):
    filepath = os.path.join('components',filename)
    return render_template(filepath)

@app.route('/modules.json')
def get_modules():
    """返回modules.json文件内容"""
    return send_file('modules.json', mimetype='application/json')


@app.route('/models/<modelId>', methods=['GET'])
def get_model_detail(modelId):
    """API接口：根据模型ID获取单个模型详细信息"""
    # 从全局模型列表中查找指定ID的模型
    for model in models:
        if model.get('id') == modelId:
            return jsonify(model)
    # 未找到模型返回404
    return jsonify({'code': 404, 'message': '未找到指定模型'}), 404

@app.route('/models')
def get_models():
    return jsonify(models)  # 返回JSON格式的模型数据

@app.route('/models/<model_id>/delete', methods=['GET'])
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


@app.route('/models/new', methods=['POST'])
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

@app.route('/models/<model_id>/check/<path:filename>')
def send_check_dataset_file(model_id, filename):
    check_path = os.path.join(models_root, model_id, 'check')
    return send_from_directory(check_path, filename)

@app.route('/models/<model_id>/check', methods=['POST'])
def checkDataSet(model_id):
    check_data = request.get_json()
    dataset_id = check_data.get('dataset_id')
    # 查找模型
    model = next((m for m in models if m.get('id') == model_id), None)
    if not model:
        return jsonify({'code': 404,'message': '未找到指定模型'}), 404
    # 查找数据集
    dataset = next((d for d in datasets if d.get('id') == dataset_id), None)
    if not dataset:
        return jsonify({'code': 404,'message': '未找到指定数据集'}), 404
    # 运行检查命令
    yaml_path = os.path.join(paddlex_root, "paddlex","configs","modules", model['module_id'], model['pretrained']+".yaml")
    dataset_path = os.path.join(dataset_root, dataset_id)
    check_path = os.path.join(models_root, model_id, 'check')
    result = subprocess.run(
        [sys.executable, paddlex_main, 
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



@app.route('/datasets')  # 新增数据集接口
def get_datasets():
    return jsonify(datasets)  # 返回JSON格式的数据集数据

datasets = [
    {
        "name": "test",
        "id": "test",
        "description": "10类图像分类数据集，包含6万张32x32彩色图像",
        "category": "CV",
        "module_id": "object_detection",
        "module_name": "目标检测",
        "type": "LabelMe",
        "update_time": "2025-05-28 14:32:27"
    },
    {
        "name": "COCO",
        "id": "coco",
        "description": "目标检测、分割和描述数据集，包含超过33万张图像",
        "category": "CV",
        "module_id": "image_classification",
        "module_name": "图像分类",
        "type": "LabelMe",
        "update_time": "2025-05-28 14:32:27"
    },
    {
        "name": "IMDB",
        "id": "imdb",
        "description": "从输入图像中自动识别并定位人脸的位置和大小",
        "category": "CV",
        "module_id": "face_detection",
        "module_name": "人脸检测",        
        "type": "LabelMe",
        "update_time": "2025-05-28 14:32:27"
    }
]

def create_directories():
    # 检查并创建models、dataset、pretrained目录
    required_dirs = ['models', 'dataset', 'pretrained']
    for dir_name in required_dirs:
        # 获取当前文件所在目录的绝对路径，拼接目标目录路径
        dir_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), dir_name)
        if not os.path.exists(dir_path):
            # 创建目录（允许已存在时不报错）
            os.makedirs(dir_path, exist_ok=True)
            print(f'成功创建目录：{dir_path}')
        else:
            print(f'目录已存在：{dir_path}')

# 全局模型数据变量
models = []
models_root = os.path.join(os.path.dirname(os.path.abspath(__file__)),'models')
dataset_root = os.path.join(os.path.dirname(os.path.abspath(__file__)),'dataset')
pretrained_root = os.path.join(os.path.dirname(os.path.abspath(__file__)),'pretrained')
models_config_path = os.path.join(models_root, 'models_config.json')
def load_or_create_models_config():
    """加载或创建模型配置文件，并返回模型数据列表"""
    # 检查文件是否存在
    if not os.path.exists(models_config_path):
        # 创建空配置文件
        with open(models_config_path, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=4)
        print(f'创建空模型配置文件：{models_config_path}')
        return []

    # 读取配置文件
    try:
        with open(models_config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        # 处理JSON格式错误（返回空列表并覆盖文件）
        print(f'配置文件 {models_config_path} 格式错误，重置为空文件')
        with open(models_config_path, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=4)
        return []



def save_model_config(new_model):
    """
    保存模型配置信息到JSON文件（存在则更新，不存在则添加）
    :param new_model: 要保存的模型配置字典（需包含'name'属性）
    """
    # 检查是否存在同名模型
    global models  # 引用全局变量
    if new_model is not None:
        # 确保模型配置包含必要的字段
        found = False
        for i, model in enumerate(models):
            if model.get('id') == new_model.get('id'):
                # 存在则更新整个对象
                models[i] = new_model
                found = True
                break

        if not found:
            # 不存在则添加新对象
            models.append(new_model)

    # 写回JSON文件
    try:
        with open(models_config_path, 'w', encoding='utf-8') as f:
            json.dump(models, f, ensure_ascii=False, indent=4)
        print(f'成功保存模型配置：{new_model["name"]}')
    except Exception as e:
        print(f'保存模型配置失败：{str(e)}')

if __name__ == '__main__':
    # 启动时执行目录检查
    create_directories()
    models = load_or_create_models_config()
    app.run(host='0.0.0.0', port=5000,debug=True)