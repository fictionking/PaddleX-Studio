import os
import json
import sys
# 定义PaddleX相关路径配置
paddlex_root = None
paddlex_main = None
pretrained_root = None
device = 'cpu'

def init():
    """从配置文件初始化PaddleX路径"""
    global paddlex_root, paddlex_main,device,pretrained_root
    # 获取当前文件所在目录的绝对路径，拼接配置文件路径
    config_path = os.path.join(os.getcwd(), 'config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    # 从配置文件读取根路径并处理
    paddlex_root = os.path.dirname(config['paddlex_root'])
    paddlex_main = os.path.join(paddlex_root, 'main.py')
    device = config['device']
    pretrained_root = config['pretrained_root']
    # 检查PaddleX主文件是否存在
    if not os.path.exists(paddlex_main):
        print(f"错误：PaddleX主文件不存在，路径：{paddlex_main}")
        sys.exit(1)