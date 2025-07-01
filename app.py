from flask import Flask, send_from_directory, jsonify,send_file
import os
from pxs.paddlexCfg import init as paddlexCfg_init
from pxs.VueSFCRender import get_cached_vue_component
import nvitop

# 初始化Flask应用
app = Flask(__name__, template_folder='templates')  # 明确模板目录
from pxs.defineMgr import define_bp,init as defineMgr_init
app.register_blueprint(define_bp)

from pxs.modelMgr import model_bp,init as modelMgr_init,get_queue_size
app.register_blueprint(model_bp)

from pxs.datasetMgr import dataset_bp,init as datasetMgr_init
app.register_blueprint(dataset_bp)

from pxs.doc import doc_bp,init as doc_init
app.register_blueprint(doc_bp)


@app.route('/')
def index():
    """首页路由，返回平台介绍信息"""
    return send_file('templates/index.html')  # 仅渲染模板

@app.route('/components/<path:filename>')
def send_components(filename):
    path = os.path.join('templates', 'components', filename)
    # 返回使用Vue编译后的JavaScript组件
    if filename.endswith('.vue'):
        # 直接返回render_vue_component生成的Response对象
        return get_cached_vue_component(path)
    else:
        # 其他文件直接返回，如CSS、图片等
        return send_from_directory('templates/components', filename)

@app.route('/assets/<path:filename>')
def send_assets(filename):
    filepath = os.path.join('templates', 'assets')
    return send_from_directory(filepath,filename)

@app.route('/libs/<path:filename>')
def send_libs(filename):
    filepath = os.path.join('templates', 'libs')
    return send_from_directory(filepath,filename)

@app.route('/system/usage')
def system_usage():
    """
    获取系统资源使用情况API
    返回CPU、RAM、GPU和VRAM的使用百分比
    """
    cpu_usage = nvitop.host.cpu_percent(interval=1)
    
    # 获取RAM使用率
    ram_usage = nvitop.host.memory_percent()
    
    # 获取GPU使用率和VRAM使用率
    gpus = nvitop.Device.all()
    if gpus:
        gpu_usage = gpus[0].gpu_percent()
        gpu_usage = gpu_usage if gpu_usage != nvitop.NA else 0
        vram_usage = gpus[0].memory_percent()
        vram_usage = vram_usage if vram_usage != nvitop.NA else 0
        temp_usage = gpus[0].temperature()
        if temp_usage == nvitop.NA:
            temp_usage= 0
        if temp_usage>100:
            temp_usage=100
    else:
        gpu_usage = 0
        vram_usage = 0
        temp_usage = 0
    queue_size = get_queue_size()
    return jsonify({
        'cpu': cpu_usage,
        'ram': ram_usage,
        'gpu': gpu_usage,
        'vram': vram_usage,
        'temp': temp_usage,
        'queue_size':queue_size
    })

def create_directories():
    # 检查并创建models、dataset、pretrained目录
    required_dirs = ['models', 'dataset', 'pretrained']
    for dir_name in required_dirs:
        # 获取当前文件所在目录的绝对路径，拼接目标目录路径
        dir_path = os.path.join(os.getcwd(), dir_name)
        if not os.path.exists(dir_path):
            # 创建目录（允许已存在时不报错）
            os.makedirs(dir_path, exist_ok=True)
            print(f'成功创建目录：{dir_path}')
        else:
            print(f'目录已存在：{dir_path}')

if __name__ == '__main__':
    # 启动时执行目录检查
    paddlexCfg_init()
    create_directories()
    defineMgr_init()
    modelMgr_init()
    datasetMgr_init()
    doc_init()
    app.run(host='0.0.0.0', port=5000,debug=True)