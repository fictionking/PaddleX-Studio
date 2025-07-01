import os
import json
from flask import Blueprint, jsonify

# 创建蓝图
define_bp = Blueprint('define', __name__)

modules = []
def init():
    global modules
    modules = load_module_definitions()

def load_module_definitions():
    """加载模块定义的三级结构数据
    返回格式: [
        {
            "category": {"id": "cv", "name": "计算机视觉", ...},
            "modules": [
                {
                    "id": "object_detection",
                    "name": "目标检测",
                    "description": "...",
                    "pretrained": [{}...]
                }...
            ]
        }...
    ]
    """
    # 读取分类信息
    category_info_path = os.path.join(os.getcwd(), 'define', 'module', 'category_info.json')
    try:
        with open(category_info_path, 'r', encoding='utf-8') as f:
            categories = json.load(f)
    except Exception as e:
        print(f"加载分类信息失败: {str(e)}")
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
            if filename.endswith('.json') and filename != 'category_info.json':
                file_path = os.path.join(category_dir, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        module = json.load(f)
                        # 提取模型类型基本信息和预训练模型列表
                        modules_define.append(module)
                except Exception as e:
                    print(f"加载模型定义文件 {filename} 失败: {str(e)}")
                    continue

        result.append({
            'category': category,
            'modules': modules_define
        })

    return result

@define_bp.route('/define/modules', methods=['GET'])
def get_module_definitions():
    return jsonify(modules)