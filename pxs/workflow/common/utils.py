"""
Workflow 工具类，包含通用的工作流辅助函数
"""

def parse_port(port: str) -> tuple[str, str]:
    """
    解析端口字符串为端口类型和端口名称

    Args:
        port: 端口字符串，格式应为 'port_type.port_name'

    Returns:
        tuple: (port_type, port_name) 二元组

    Raises:
        ValueError: 当端口格式不正确时抛出
    """
    port_parts = port.split('.', 1)
    if len(port_parts) == 2:
        return port_parts[0], port_parts[1]
    else:
        raise ValueError(f"端口格式不正确: {port}，应为 'port_type.port_name' 格式")
