import sys
import os
import json
from datetime import datetime

# 将项目根目录添加到Python路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from pxs.workflow import create_workflow

def run_workflow():
    """
    运行工作流测试，使用workflow.json作为配置输入
    """
    # 加载工作流配置
    config_path = os.path.join(os.path.dirname(__file__), 'workflow.json')
    print(f"从{config_path}加载工作流配置...")
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    print("工作流配置加载成功!")

    # 创建工作流
    print("创建工作流...")
    workflow = create_workflow(config)
    print("工作流创建成功!")

    # 运行工作流
    print("运行工作流...")

    # 运行工作流并输出状态信息
    for result in workflow.predict():
        print(f"状态: {result.get('status', '未知')}")
        print(f"已运行时间: {result.get('elapsed_time', 0):.4f}秒")
        
        # 输出当前节点和节点状态
        current_node = result.get('current_node')
        node_status = result.get('node_status')
        if current_node and node_status:
            print(f"当前节点: {current_node}, 节点状态: {node_status}")
        
        # 输出正在运行的节点
        ran_nodes = result.get('ran_nodes', [])
        if ran_nodes:
            print(f"已运行的节点: {', '.join(ran_nodes)}")
        
        # 输出完成状态时的结果
        if result.get('status') == '完成' and 'result' in result:
            print("工作流运行完成，最终结果:")
            print(result.get('result'))
        
        # 输出失败状态时的错误信息
        if result.get('status') == '失败' and 'error' in result:
            print("工作流运行失败:")
            print(result.get('error'))
        
        print("-----------------")

if __name__ == "__main__":
    run_workflow()
