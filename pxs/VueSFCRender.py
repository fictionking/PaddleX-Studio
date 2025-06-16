import re
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

    # 简化处理<script setup>为函数形式
    if is_setup:
        return f'__sfc_setup__: () => ({{ {script_content} }})', True, import_statements
    return script_content, False, import_statements


def _parse_styles(content: str) -> List[Tuple[str, dict]]:
    """
    解析<style>标签内容，提取样式和属性（如scoped）
    
    Args:
        content (str): Vue文件原始内容
    
    Returns:
        List[Tuple[str, dict]]: 样式内容列表（含属性字典）
    """
    style_pattern = re.compile(r'<style([^>]*)>([\s\S]*?)</style>', re.DOTALL)
    styles = []
    for match in style_pattern.finditer(content):
        attrs_str = match.group(1)
        style_content = match.group(2).strip()
        # 解析属性字符串为字典（简化处理key=value形式）
        attrs = {}
        if attrs_str:
            for attr in attrs_str.split(): 
                if '=' in attr:
                    k, v = attr.split('=', 1)
                    attrs[k.strip()] = v.strip().strip('"\'')
                else:
                    attrs[attr.strip()] = 'true'
        styles.append((style_content, attrs))
    return styles


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

    # 解析模板
    template_match = re.search(r'<template>([\s\S]*?)</template>', content, re.DOTALL)
    template = template_match.group(1).strip() if template_match else ''
    escaped_template = template.replace('\\', '\\\\').replace('`', '\\`')  # 转义反斜杠和反引号

    # 解析脚本（支持setup语法及import）
    script_content, is_setup, import_statements = _parse_script(content)

    # 解析样式（含属性）
    styles = _parse_styles(content)
    style_items = []
    for s, a in styles:
        # 处理内容中的单引号转义
        escaped_content = s.replace("'", "\\'")
        # 构造单个样式项字符串
        item_str = f'`{escaped_content}`'
        style_items.append(item_str)
    # 合并为最终样式字符串
    style_str = ',\n  '.join(style_items)
    import_str = '\n'.join(import_statements) + '\n' if import_statements else ''
    # 组合最终组件对象
    if is_setup:

        content = f'''{import_str}\n export default {{\n                template: `{escaped_template}`,\n                ...{script_content},\n                styles: [{style_str}]\n            }};'''
        return make_response(content, 200, {'Content-Type': 'application/javascript'})
    else:
        content = f'''{import_str}\n export default {{
            template: `{escaped_template}`,
            ...{script_content[len('export default'):].lstrip() if script_content.startswith('export default') else script_content},
            styles: [{style_str}]
        }};'''
        return make_response(content, 200, {'Content-Type': 'application/javascript'})