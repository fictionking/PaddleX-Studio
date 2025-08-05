from flask import Blueprint, jsonify, render_template_string, send_file, request, render_template
import os
from markdown_it import MarkdownIt
import mimetypes
import requests
from flask import Blueprint, request, jsonify, render_template

# 初始化文档管理蓝图
doc_bp = Blueprint('doc_bp', __name__)

# # 解决跨域问题
# CORS(doc_bp)

def init():
    """
    初始化文档模块
    """
    # 空实现，不在启动时初始化文档
    return

@doc_bp.route('/docs/styles.css')
def serve_css():
    """提供文档样式表CSS文件"""
    css_path = os.path.join('doc', 'styles.css')
    if not os.path.exists(css_path):
        return jsonify({'error': 'CSS file not found'}), 404
    return send_file(css_path, mimetype='text/css')

# API代理，解决Swagger UI调试外部API时的跨域问题
@doc_bp.route('/proxy/pipeline/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def api_proxy(path):
    """
    代理外部API请求，解决跨域问题
    
    参数:
    - path: 代理的API路径
    """
    global 外部_api_spec
    if not 外部_api_spec:
        return jsonify({'error': '未找到外部API的OpenAPI规范文件'}), 404
    
    # 获取外部API的基础URL
    servers = 外部_api_spec.get('servers', [{}])
    base_url = servers[0].get('url', '') if servers else ''
    
    if not base_url:
        return jsonify({'error': '外部API的基础URL未在规范中定义'}), 400
    
    # 构建完整的请求URL
    url = f"{base_url}/{path}" if path else base_url
    
    try:
        # 转发请求
        response = requests.request(
            method=request.method,
            url=url,
            headers={key: value for key, value in request.headers if key != 'Host'},
            data=request.get_data(),
            params=request.args,
            allow_redirects=False
        )
        
        # 构建响应
        proxy_response = doc_bp.response_class(
            response=response.content,
            status=response.status_code,
            headers=dict(response.headers),
            mimetype=response.headers.get('content-type')
        )
        return proxy_response
    except Exception as e:
        return jsonify({'error': f'代理请求失败: {str(e)}'}), 500

@doc_bp.route('/docs/<doctype>/<docname>/')
@doc_bp.route('/docs/<doctype>/<docname>/<path:file_path>')
def handle_docs(doctype, docname, file_path=None):
    """
    处理文档请求，根据file_path参数决定返回内容
    - 当file_path为空时，默认读取index.md并转换为HTML
    - 当file_path为.md文件时，转换为HTML返回
    - 其他文件类型直接发送文件
    """
    # 确定文件路径
    if file_path is None:
        file_path = 'index.md'
    full_path = os.path.join('doc', doctype, docname, file_path)
    
    # 安全检查：确保文件路径在允许范围内
    base_dir = os.path.abspath(os.path.join('doc', doctype, docname))
    full_path_abs = os.path.abspath(full_path)
    if not full_path_abs.startswith(base_dir):
        return jsonify({'error': 'Access denied: Invalid path'}), 403
    
    # 检查文件是否存在
    if not os.path.exists(full_path):
        return jsonify({'error': 'file not found'}), 404
    
    # 处理Markdown文件
    if full_path.endswith('.md'):
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            html=render_markdown(content)
            return html, 200
        except Exception as e:
            return jsonify({'error': f'Failed to read or convert markdown file: {str(e)}'}), 500
    # 处理其他文件类型
    else:
        mime_type, _ = mimetypes.guess_type(full_path)
        try:
            return send_file(full_path, mimetype=mime_type)
        except Exception as e:
            return jsonify({'error': f'Failed to send file: {str(e)}'}), 500

def render_markdown(content):
    md = MarkdownIt("gfm-like",{"breaks": True})
    # 添加完整HTML结构和图片样式
    html = f'''<!DOCTYPE html>
    <html lang="zh-CN">
    <head>
    <title>PaddleX Studio 文档</title>
    <link rel="stylesheet" href="/docs/styles.css">
    </head>
    <body>
    <div class="doc-container">{md.render(content)}</div>
    </body>
    </html>'''
    return html