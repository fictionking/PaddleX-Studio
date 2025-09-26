from pxs.workflow.nodes.base_node import StreamNode, NodeResult

class StreamExampleNode(StreamNode):
    """流式示例节点

    一个简单的流式节点示例，用于展示如何实现流式输出功能
    这个节点会将输入的文本按行分割，并逐行输出
    """

    def __init__(self, config: dict, pipeline: any) -> None:
        """
        初始化流式示例节点

        Args:
            config (dict): 节点配置
            pipeline (any): 工作流管道实例
        """
        super().__init__(config, pipeline)
        # 可以从配置中提取参数
        self.delay = self.params.get('delay', 0.5)  # 默认每输出一条数据延迟0.5秒

    def _run_compute(self, port: str, data: any) -> NodeResult:
        """
        非流式运行方法（通常不使用，主要使用_stream_output）

        Args:
            port (str): 输入端口名称
            data (any): 输入数据

        Returns:
            NodeResult: 节点运行结果
        """
        # 这里只是返回全部结果，实际流式处理在_stream_output中
        if isinstance(data, str):
            lines = data.split('\n')
            return NodeResult({'result': lines}, self)
        else:
            return NodeResult({'result': [str(data)]}, self)

    def _stream_output(self, port: str, data: any):
        """
        流式输出的核心逻辑

        Args:
            port (str): 输入端口名称
            data (any): 输入数据（通常是文本）

        Yields:
            NodeResult: 每行文本的处理结果
        """
        import time
        
        # 检查输入数据类型
        if isinstance(data, str):
            # 按换行符分割文本
            lines = data.split('\n')
            
            # 逐行输出处理结果
            for i, line in enumerate(lines):
                # 创建当前行的结果
                stream_result = NodeResult({
                    'line': line,
                    'line_number': i + 1,
                    'total_lines': len(lines),
                    'is_last': i == len(lines) - 1
                }, self)
                
                # 输出当前行的结果
                yield stream_result
                
                # 如果不是最后一行，添加延迟
                if i < len(lines) - 1:
                    time.sleep(self.delay)
        elif isinstance(data, list):
            # 如果输入是列表，逐元素输出
            for i, item in enumerate(data):
                stream_result = NodeResult({
                    'item': item,
                    'index': i,
                    'total_items': len(data),
                    'is_last': i == len(data) - 1
                }, self)
                
                yield stream_result
                
                if i < len(data) - 1:
                    time.sleep(self.delay)
        else:
            # 其他类型的数据直接输出
            stream_result = NodeResult({
                'data': data,
                'is_last': True
            }, self)
            yield stream_result

    def process_output(self, result: any, port: str = None) -> any:
        """
        处理输出结果

        Args:
            result (any): 原始结果
            port (str, optional): 输出端口名称. Defaults to None.

        Returns:
            any: 处理后的结果
        """
        # 根据端口名称返回不同的结果
        if port == 'line':
            return result.get('line', result.get('item', result.get('data')))
        elif port == 'metadata':
            return {
                'line_number': result.get('line_number'),
                'total_lines': result.get('total_lines'),
                'index': result.get('index'),
                'total_items': result.get('total_items'),
                'is_last': result.get('is_last', True)
            }
        else:
            # 默认返回完整结果
            return result