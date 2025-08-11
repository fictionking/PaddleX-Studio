import os
import json
import sys
import logging
# 定义PaddleX相关路径配置
paddlex_root = None
paddlex_main = None
train_root = None
datasets_root = None
weights_root = None
app_root = None
device = 'cpu'
studio_root = None
def init():
    """从配置文件初始化PaddleX路径"""
    global paddlex_root, paddlex_main,device,weights_root,train_root,datasets_root,app_root,studio_root
    # 获取当前文件所在目录的绝对路径，拼接配置文件路径
    studio_root = os.getcwd()
    config_path = os.path.join(os.getcwd(), 'config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    # 从配置文件读取根路径并处理
    paddlex_root = os.path.dirname(config['paddlex_root'])
    paddlex_main = os.path.join(paddlex_root, 'main.py')
    device = config['device']
    weights_root = config['weights_root']
    if weights_root.startswith('.\\') or weights_root.startswith('./') or weights_root.startswith('..\\') or weights_root.startswith('../'):
        weights_root = os.path.abspath(os.path.join(studio_root, weights_root))
    train_root = config['train_root']
    if train_root.startswith('.\\') or train_root.startswith('./') or train_root.startswith('..\\') or train_root.startswith('../'):
        train_root = os.path.abspath(os.path.join(studio_root, train_root))
    datasets_root = config['datasets_root']
    if datasets_root.startswith('.\\') or datasets_root.startswith('./') or datasets_root.startswith('..\\') or datasets_root.startswith('../'):
        datasets_root = os.path.abspath(os.path.join(studio_root, datasets_root))
    app_root = config['app_root']
    if app_root.startswith('.\\') or app_root.startswith('./') or app_root.startswith('..\\') or app_root.startswith('../'):
        app_root = os.path.abspath(os.path.join(studio_root, app_root))
    # 检查PaddleX主文件是否存在
    if not os.path.exists(paddlex_main):
        logging.error(f"错误：PaddleX主文件不存在，路径：{paddlex_main}")
        sys.exit(1)