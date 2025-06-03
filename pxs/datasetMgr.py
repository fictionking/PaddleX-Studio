from flask import Blueprint, jsonify, request
import os
import json
import datetime
# 初始化数据集管理蓝图
dataset_bp = Blueprint('dataset_bp', __name__)

# 定义数据集列表
datasets = []
dataset_root = os.path.join(os.getcwd(),'dataset')
dataset_config_path = os.path.join(dataset_root, 'dataset_config.json')

def init():
    """初始化模型数据，从JSON文件加载或创建"""
    global datasets
    datasets = load_or_create_dataset_config()

def load_or_create_dataset_config():
    """加载或创建模型配置文件，并返回模型数据列表"""
    if not os.path.exists(dataset_config_path):
        with open(dataset_config_path, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=4)
        print(f'创建空数据集配置文件：{dataset_config_path}')
        return []
    try:
        with open(dataset_config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f'配置文件 {dataset_config_path} 格式错误，重置为空文件')
        with open(dataset_config_path, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=4)
        return []

@dataset_bp.route('/datasets')  # 数据集接口
def get_datasets():
    """返回JSON格式的数据集数据"""
    return jsonify(datasets)