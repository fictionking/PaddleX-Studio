from flask import Blueprint, jsonify, render_template_string, send_file, request, render_template
import os
from markdown_it import MarkdownIt
import mimetypes
import requests
from flask import Blueprint, request, jsonify, render_template

# 初始化文档管理蓝图
doc_bp = Blueprint('doc_bp', __name__)

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