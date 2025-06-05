import re
from typing import Tuple, List


def _parse_script(content: str) -> Tuple[str, bool]:
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
    is_setup = 'setup' in script_attrs

    # 简化处理<script setup>为函数形式
    if is_setup:
        return f'__sfc_setup__: () => ({{ {script_content} }})', True
    return script_content, False


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
                    attrs[attr.strip()] = True
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

    # 解析脚本（支持setup语法）
    script_content, is_setup = _parse_script(content)

    # 解析样式（含属性）
    styles = _parse_styles(content)
    style_str = ',\n  '.join([
        f'{{ content: `{s.replace("`","\\`")}`, attrs: {repr(a)} }}'
        for s, a in styles
    ])

    # 组合最终组件对象
    if is_setup:
        return f'''\
        export default {{
            template: `{escaped_template}`,
            {script_content},
            styles: [{style_str}]
        }};''' 
    else:
        return f'''\
        export default {{
            template: `{escaped_template}`,
            {script_content if script_content.startswith('export default') else f'...({{ {script_content} }})'},
            styles: [{style_str}]
        }};'''