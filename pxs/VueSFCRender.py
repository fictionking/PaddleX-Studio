import re
import os
import time
from typing import Tuple

# 缓存存储结构: {文件路径: {内容, 文件修改时间, 缓存时间}}
_vue_render_cache = {
    "entries": {},
    "max_size": 5,  # 最大缓存数量
    "max_age": 600   # 最大缓存时间(秒)
}


def _cleanup_cache():
    """
    清理过期或超出数量限制的缓存项
    时间条件: 超过max_age的缓存项
    数量条件: 超过max_size时删除最旧的缓存项
    """
    current_time = time.time()
    entries = _vue_render_cache["entries"]
    max_age = _vue_render_cache["max_age"]
    max_size = _vue_render_cache["max_size"]

    # 清理过期缓存
    expired_keys = [
        key for key, entry in entries.items()
        if current_time - entry["cache_time"] > max_age
    ]
    for key in expired_keys:
        del entries[key]

    # 清理超出数量限制的缓存（保留最新的）
    if len(entries) > max_size:
        # 按缓存时间排序，删除最旧的
        sorted_keys = sorted(entries.keys(), key=lambda k: entries[k]["cache_time"])
        for key in sorted_keys[:-max_size]:
            del entries[key]


def get_cached_vue_component(vue_file_path: str) -> str:
    """
    获取Vue组件的渲染结果，使用内存缓存优化性能
    当文件内容变化、缓存过期或超出数量限制时会重新渲染

    参数:
        vue_file_path: Vue文件的绝对路径

    返回:
        渲染后的HTML字符串
    """
    # 获取当前文件修改时间
    try:
        current_mtime = os.path.getmtime(vue_file_path)
    except OSError:
        # 文件不存在或无法访问，直接渲染并不缓存
        return render_vue_component(vue_file_path)

    current_time = time.time()
    entries = _vue_render_cache["entries"]

    # 先执行缓存清理
    _cleanup_cache()

    # 检查缓存是否有效
    if vue_file_path in entries:
        entry = entries[vue_file_path]
        # 文件未修改且缓存未过期
        if entry["mtime"] == current_mtime:
            return entry["content"]

    # 缓存无效，重新渲染并更新缓存
    rendered_content = render_vue_component(vue_file_path)
    entries[vue_file_path] = {
        "content": rendered_content,
        "mtime": current_mtime,
        "cache_time": current_time
    }

    return rendered_content

def insert_into_lifecycle(script_content, lifecycle_name, inject_code):
    """
    在Vue组件的指定生命周期函数末尾插入代码
    支持处理嵌套花括号结构，确保原代码完整保留
    
    Args:
        script_content: Vue组件的脚本内容
        lifecycle_name: 生命周期函数名，如'mounted'、'beforeUnmount'等
        inject_code: 要插入的代码字符串
    """
    # 查找指定生命周期函数的位置
    # 原代码已使用了正确的正则表达式来匹配生命周期函数，推测无需修改，这里直接保留原代码
    start_pattern = re.compile(rf'{re.escape(lifecycle_name)}\s*\(\s*\)\s*{{')
    match = start_pattern.search(script_content)
    if not match:
        return script_content
    
    start_pos = match.end() - 1  # '{'的位置
    balance = 1
    pos = start_pos + 1
    length = len(script_content)
    
    while pos < length:
        char = script_content[pos]
        if char == '{':
            balance += 1
        elif char == '}':
            balance -= 1
            if balance == 0:
                # 在结束花括号前插入代码
                return script_content[:pos] + '\n' + inject_code + '\n' + script_content[pos:]
        pos += 1
    
    # 如果没有找到匹配的结束花括号，返回原内容
    return script_content
import hashlib
from typing import Tuple, List
from flask import make_response


def _parse_script(content: str) -> Tuple[str, bool, list]:
    """
    解析<script>标签内容，处理<script setup>语法及import语句
    
    Args:
        content (str): Vue文件原始内容
    
    Returns:
        Tuple[str, bool, list]: 解析后的脚本内容，是否为setup语法，import语句列表
    """
    """
    解析<script>标签内容，处理<script setup>语法
    
    Args:
        content (str): Vue文件原始内容
    
    Returns:
        Tuple[str, bool]: 解析后的脚本内容，是否为setup语法
    """
    script_pattern = re.compile(r'<script([^>]*)>([\s\S]*?)</script>', re.DOTALL)
    script_match = script_pattern.search(content)
    if not script_match:
        return '', False

    script_attrs = script_match.group(1)
    script_content = script_match.group(2).strip()
    # 提取import语句
    import_pattern = re.compile(r'^import .*$', re.MULTILINE)
    import_statements = import_pattern.findall(script_content)
    # 从脚本内容中移除import语句
    script_content = import_pattern.sub('', script_content).strip()
    is_setup = 'setup' in script_attrs
    #移除“export default”
    script_content = script_content.replace('export default', '').strip() 
    # 简化处理<script setup>为函数形式
    if is_setup:
        return f'__sfc_setup__: () => ({{ {script_content} }})', True, import_statements
    return script_content, False, import_statements


def _parse_styles(content: str) -> Tuple[str, bool]:
    """
    解析<style>标签内容，提取样式和scoped属性
    
    Args:
        content (str): Vue文件原始内容
    
    Returns:
        Tuple[str, bool]: 样式内容，是否为scoped样式
    """
    style_pattern = re.compile(r'<style([^>]*)>([\s\S]*?)</style>', re.DOTALL)
    styles = []
    is_scoped = False
    
    for match in style_pattern.finditer(content):
        style_attrs = match.group(1)
        style_content = match.group(2).strip()
        styles.append(style_content)
        
        # 检查是否包含scoped属性
        if 'scoped' in style_attrs:
            is_scoped = True
    
    return '\n'.join(styles).strip(), is_scoped


def render_vue_component(vue_file_path: str) -> str:
    """
    将Vue单文件组件（.vue）编译为可直接使用的JavaScript组件字符串
    支持：<script setup>语法、带属性的<style>标签（如scoped）、基础异常处理
    
    Args:
        vue_file_path (str): Vue组件文件的绝对路径
    
    Returns:
        str: 编译后的JavaScript组件字符串
    
    Raises:
        FileNotFoundError: 指定文件不存在
        PermissionError: 无权限读取文件
    """
    # 异常处理：文件读取
    try:
        with open(vue_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f'文件不存在: {vue_file_path}')
    except PermissionError:
        raise PermissionError(f'无权限读取文件: {vue_file_path}')

    # 生成组件唯一标识 (基于文件路径的哈希)
    scope_id = f'data-v-{hashlib.md5(vue_file_path.encode()).hexdigest()[:8]}'
 
    # 解析样式（含scoped属性）
    styles, is_scoped = _parse_styles(content)
    
    # 处理scoped样式：为选择器添加scope_id属性选择器
    if is_scoped and styles:
        # 简单选择器处理（实际场景可能需要更复杂的CSS解析）
        lines = styles.split('\n')
        processed_lines = []
        for line in lines:
            # 跳过空行和注释
            if not line.strip() or line.strip().startswith('/*'):
                processed_lines.append(line)
                continue
            # 为选择器添加scope_id
            selector_pattern = re.compile(r'([^\{]+)\{')
            def add_scope(match):
                selector = match.group(1).strip()
                # 跳过@keyframes等特殊规则
                if selector.startswith('@'):
                    return match.group(0)
                # 处理:deep()选择器
                deep_pattern = re.compile(r':deep\(([^)]+)\)')
                if deep_pattern.search(selector):
                    # 替换:deep(selector)为[data-v-xxx] selector
                    return deep_pattern.sub(f'[{scope_id}] \g<1>', selector) + ' {'
                # 为普通选择器添加scope_id
                return selector + f'[{scope_id}] ' + '{'
            processed_line = selector_pattern.sub(add_scope, line)
            processed_lines.append(processed_line)
        styles = '\n'.join(processed_lines)
    
    style_str = styles.replace("'", "\\'")   
    # 解析模板
    template_match = re.search(r'<template>([\s\S]*?)</template>', content, re.DOTALL)
    template = template_match.group(1).strip() if template_match else ''
    
    # 如果是scoped样式，为所有元素添加scope_id属性
    if template and is_scoped:
        # 为所有元素添加scope_id属性
        template = re.sub(r'<([a-zA-Z0-9-]+)(\s|>)', f'<\\1 {scope_id} \\2', template)
    
    escaped_template = template.replace('\\', '\\\\').replace('`', '\\`')  # 转义反斜杠和反引号

    # 解析脚本（支持setup语法及import）
    script_content, is_setup, import_statements = _parse_script(content)

    import_str = '\n'.join(import_statements) + '\n' if import_statements else ''
    
    # 生成样式注入和清理的代码
    style_code = ''
    if styles:
        # 样式注入代码
        inject_code = f'''
            // 注入组件样式
            this.__styleElement = document.createElement('style');
            this.__styleElement.textContent = `{style_str}`;
            document.head.appendChild(this.__styleElement);
        '''
        # 样式清理代码
        cleanup_code = f'''
            // 清理组件样式
            if (this.__styleElement) {{
                this.__styleElement.remove();
                this.__styleElement = null;
            }}
        '''
        
        # 合并mounted钩子
        if is_setup:
            # setup模式下直接添加mounted和beforeUnmount
            style_code = f''',
                mounted() {{
                    {inject_code}
                }},
                beforeUnmount() {{
                    {cleanup_code}
                }}
            '''
        else:
            # 非setup模式需要合并原有钩子
            # 处理mounted钩子
            if re.search(r'mounted\s*\(\s*\)\s*\{', script_content):
                # 在现有mounted函数末尾添加注入代码
                script_content = insert_into_lifecycle(script_content, 'mounted', inject_code)
            else:
                # 添加新的mounted函数
                style_code += f''',
                    mounted() {{
                        {inject_code}
                    }}
                '''
            
            # 处理beforeUnmount钩子
            if re.search(r'beforeUnmount\s*\(\s*\)\s*\{', script_content):
                # 在现有beforeUnmount函数末尾添加清理代码
                script_content = insert_into_lifecycle(script_content, 'beforeUnmount', cleanup_code)
            else:
                # 添加新的beforeUnmount函数
                style_code += f''',
                    beforeUnmount() {{
                        {cleanup_code}
                    }}
                '''
    
    # 组合最终组件对象
    if is_setup:
        content = f'''{import_str}
export default {{
                template: `{escaped_template}`,
                ...{script_content}
                {style_code}
            }};'''
    else:
        content = f'''{import_str}
export default {{
                template: `{escaped_template}`,
                ...{script_content}
                {style_code}
            }};'''
    
    return make_response(content, 200, {'Content-Type': 'application/javascript'})
