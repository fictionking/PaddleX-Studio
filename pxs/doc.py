from flask import Blueprint, jsonify,send_file
import os
import markdown
import mimetypes
# 初始化数据集管理蓝图
doc_bp = Blueprint('doc_bp', __name__)

def init():
    return

@doc_bp.route('/docs/<doctype>/<docname>')
def renderMarkdown(doctype,docname):
    if not docname:
        return jsonify({'error': 'docname is required'}), 400
    file_path = os.path.join('doc', doctype, docname+'.md')
    if not os.path.exists(file_path):
        return jsonify({'error': 'file not found'}), 404
    #将markdown文件转换为html文件
    content=''
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    # 使用markdown库将markdown转换为html
    html = markdown.markdown(content)
    # 返回html文件
    return html, 200

@doc_bp.route('/docs/<doctype>/<docname>/<path:file_path>')  # 数据集接口
def getAttatch(doctype,docname,file_path):
    if not file_path:
        return jsonify({'error': 'file_path is required'}), 400
    file_path = os.path.join('doc',doctype, file_path)
    if not os.path.exists(file_path):
        return jsonify({'error': 'file not found'}), 404
    # 获取文件MIME类型
    mime_type, _ = mimetypes.guess_type(full_path)
    try:
        return send_file(full_path, mimetype=mime_type)
    except Exception as e:
        return jsonify({'error': f'Failed to send file: {str(e)}'}), 500

