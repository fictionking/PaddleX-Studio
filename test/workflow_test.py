import sys
import os
import json
from datetime import datetime

from flask import jsonify

# 将项目根目录添加到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from pxs.workflow import create_workflow

# 工作流配置：图片输入 -> 目标识别 -> 分类识别 -> 输出JSON结果到文件
config = {
    "workflow_name": "image_object_classification_workflow",
    "start": "filepath",
    "end": "json",
    "nodes": [
        {
            "id": "image_input",
            "name": "图像输入节点",
            "type": "load_image",
            "params": {},
            "inputs": ["files"],
            "outputs": ["images","count"]

        },
        {
            "id": "object_detection",
            "name": "目标识别节点",
            "type": "model",
            "params": {
                "module_name": "object_detection",
                "model_name": "PP-YOLOE_plus-L",
                "model_dir": "weights\PP-YOLOE_plus-L\inference",
                "model_params": {
                    "threshold": 0.5
                },
                "infer_params": {
                    "threshold": 0.5
                }
            },
            "inputs": ["images"],
            "outputs": ["images", "boxes","count"]
        },
        {
            "id": "image_classification",
            "name": "图像分类节点",
            "type": "model",
            "params": {
                "module_name": "image_classification",
                "model_name": "PP-HGNetV2-B6",
                "model_dir": "weights\PP-HGNetV2-B6\inference",
                "model_params": {
                    "topk": 5
                },
                "infer_params": {
                    "topk": 1
                }
            },
            "inputs": ["images"],  # 接收目标识别节点的输出
            "outputs": ["labels"]
        },
        {
            "id": "json_output",
            "name": "JSON输出节点",
            "type": "textfile_output",
            "params": {
                "format": "json_lines",
                "path": f"output/file/json_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl",
            },
            "inputs": ["input"],
            "outputs": ["files"]
        },
        {
            "id": "image_output",
            "name": "图像输出节点",
            "type": "save_image",
            "params": {
                "format": "png",
                "path": f"output/images_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            },
            "inputs": ["images"],
            "outputs": ["files"]
        },
        {
            "id": "obj_threshold",
            "name": "目标识别阈值节点",
            "type": "number_const",
            "params": {
                "value": 0.5
            },
            "inputs": [],
            "outputs": ["value"]
        },
        {
            "id": "welcome",
            "name": "欢迎语",
            "type": "text_const",
            "params": {
                "value": "hello world"
            },
            "inputs": [],
            "outputs": ["value"]
        }
    ],
    "connections": [
        {"from": "welcome.outputs.value", "to": "end"},
        {"from": "start", "to": "image_input.inputs.files"},
        {"from": "image_input.outputs.images", "to": "object_detection.inputs.images"},
        {"from": "object_detection.outputs.images", "to": "image_output.inputs.images"},
        {"from": "object_detection.outputs.images", "to": "image_classification.inputs.images"},
        {"from": "image_classification.outputs.labels", "to": "json_output.inputs.input"},
        {"from": "image_classification.outputs.labels", "to": "end"},
        {"from": "obj_threshold.outputs.value", "to": "object_detection.params.infer_params.threshold"},
    ],
}

def run_workflow():
    """
    运行工作流测试
    """
    print("创建工作流...")
    workflow = create_workflow(config)
    print("工作流创建成功!")
    print("运行工作流...")
    input_data = "test/test.png"
    print("工作流运行完成，结果:")
    for result in workflow.predict(input=input_data):
        print(str(result))
        print("-----------------")

if __name__ == "__main__":
    run_workflow()
