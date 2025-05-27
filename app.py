from flask import Flask, request, jsonify, render_template

# 初始化Flask应用
app = Flask(__name__)

@app.route('/')
def index():
    """首页路由，返回平台介绍信息"""
    return render_template('index.html')  # 仅渲染模板

@app.route('/api/models')
def get_models():
    """API接口：获取模型列表数据"""
    models = [  # 模型列表数据（新增预训练名称、微调时间、训练状态）
        {
            'name': 'ResNet-50',
            'description': '深度残差网络，适用于图像分类任务',
            'category': ['CV','图像分类'],
            'pretrained_name': 'ResNet-50-ImageNet',  # 预训练模型名称
            'fine_tune_time': '2024-06-15 09:30:00',  # 微调日期时间
            'status': 'success'  # 训练状态（运行中/成功/失败）
        },
        {
            'name': 'BERT-base',
            'description': '双向Transformer模型，适用于自然语言处理任务',
            'category': ['LLM','自然语言处理'],
            'pretrained_name': 'BERT-base-uncased',  # 预训练模型名称
            'fine_tune_time': '2024-06-16 14:15:00',  # 微调日期时间
            'status': 'processing'  # 训练状态（运行中/成功/失败）
        },
        {
            'name': 'YOLOv5',
            'description': '实时目标检测模型，适用于物体检测任务',
            'category': ['CV','目标检测'],
            'pretrained_name': 'YOLOv5s-coco',  # 预训练模型名称
            'fine_tune_time': '2024-06-14 11:00:00',  # 微调日期时间
            'status': 'fail'  # 训练状态（运行中/成功/失败）
        }
    ]
    return jsonify(models)  # 返回JSON格式的模型数据


@app.route('/api/datasets')  # 新增数据集接口
def get_datasets():
    # 示例数据集数据（包含名称、描述、分类）
    datasets = [
        {
            "name": "CIFAR-10",
            "description": "10类图像分类数据集，包含6万张32x32彩色图像",
            "category": "图像分类"
        },
        {
            "name": "COCO",
            "description": "目标检测、分割和描述数据集，包含超过33万张图像",
            "category": "目标检测"
        },
        {
            "name": "IMDB",
            "description": "电影评论情感分析数据集，包含5万条评论",
            "category": "自然语言处理"
        }
    ]
    return jsonify(datasets)  # 返回JSON格式的数据集数据

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)