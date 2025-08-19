import sys
import os
import json
from datetime import datetime

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
            "type": "image_input",
            "params": {},
            "inputs": ["path"],
            "outputs": ["images"]

        },
        {
            "id": "object_detection",
            "name": "目标识别节点",
            "type": "model",
            "params": {
                "module_name": "object_detection",
                "model_name": "PicoDet-S",
                "model_dir": "weights\PicoDet-S\inference",
                "model_params": {
                    "threshold": 0.5
                },
                "infer_params": {
                    "threshold": 0.5
                }
            },
            "inputs": ["images"],
            "outputs": ["images", "boxes"]
        },
        # {
        #     "id": "image_classification",
        #     "name": "图像分类节点",
        #     "type": "model",
        #     "params": {
        #         "module_name": "image_classification",
        #         "model_name": "PP-LCNet_x1_0",
        #         "model_dir": "weights\PP-LCNet_x1_0\inference",
        #         "model_params": {
        #             "topk": 5
        #         },
        #         "infer_params": {
        #             "topk": 5
        #         }
        #     },
        #     "inputs": ["images"],  # 接收目标识别节点的输出
        #     "outputs": ["labels"]
        # },
        # {
        #     "id": "json_output",
        #     "name": "JSON输出节点",
        #     "type": "textfile_output",
        #     "params": {
        #         "format": "json",
        #         "path": f"output/json_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        #     },
        #     "inputs": ["object_input","string_input"],
        #     "outputs": ["files"]
        # },
        {
            "id": "image_output",
            "name": "图像输出节点",
            "type": "imagefile_output",
            "params": {
                "format": "png",
                "path": f"output/images_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            },
            "inputs": ["images"],
            "outputs": ["files"]
        },
        # {
        #     "id": "topk",
        #     "name": "topk节点",
        #     "type": "number_input",
        #     "params": {
        #         "default_value": 5
        #     },
        #     "inputs": [],
        #     "outputs": ["value"]
        # }
    ],
    "connections": [
        {"from": "start", "to": "image_input.inputs.path"},
        {"from": "image_input.outputs.images", "to": "object_detection.inputs.images"},
        {"from": "object_detection.outputs.images", "to": "image_output.inputs.images"},
        {"from": "image_output.outputs.files", "to": "end"},
        # {"from": "object_detection.outputs.images", "to": "image_classification.inputs.images"},
        # {"from": "json_output.outputs.files", "to": "end"}
        # {"from": "image_classification.outputs.labels", "to": "json_output.inputs.object_input"},
        # {"from": "topk.outputs.value", "to": "image_classification.params.infer_params.topk"},
        # {"from": "image_classification.outputs.labels", "to": "end"},
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
        print(result)
    return result

if __name__ == "__main__":
    run_workflow()
