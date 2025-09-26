from typing import Any, Dict, Optional
from pxs.workflow.nodes.base_node import StreamNode, NodeResult

class StreamExampleNode(StreamNode):
    """流式输出节点示例类

    这个节点演示如何实现一个流式输出节点，该节点能够逐步输出多条数据，
    每条数据都会立即传递给下游节点进行处理。
    """

    def __init__(self, config: Dict, pipeline: Any) -> None:
        """
        初始化流式示例节点

        Args:
            config (Dict): 节点配置
            pipeline (Any): 工作流管道实例
        """
        super().__init__(config, pipeline)
        # 可以在这里初始化一些参数
        self.batch_size = config.get('params', {}).get('batch_size', 1)

    def _run_compute(self, port: str, data: Any) -> 'NodeResult':
        """
        执行计算逻辑并返回完整结果

        注意：在新的流式处理机制中，这个方法主要用于非流式调用场景
        在工作流执行中，pipeline会直接调用_stream_output方法处理流式输出

        Args:
            port (str): 输入端口名称
            data (Any): 输入数据

        Returns:
            NodeResult: 节点运行结果
        """
        # 创建结果对象
        result = NodeResult()
        
        # 这里可以根据实际需求处理输入数据
        if isinstance(data, str):
            # 如果输入是字符串，按行分割处理
            lines = data.strip().split('\n')
            result.set('output', '\n'.join(lines))  # 设置完整结果
        elif isinstance(data, list):
            # 如果输入是列表，直接处理
            result.set('output', data)  # 设置完整结果
        else:
            # 其他类型数据，原样返回
            result.set('output', data)
        
        return result

    def _stream_output(self, port: str, data: Any):
        """
        流式输出的核心逻辑，每次yield一条数据

        在新的处理机制中，pipeline会直接调用此方法来处理流式节点的输出
        每条yield的数据都会被立即放入stream_results_queue并传递给下游节点

        Args:
            port (str): 输入端口名称
            data (Any): 输入数据
        
        Yields:
            NodeResult: 每条流式输出的结果
        """
        # 这里我们可以根据数据类型进行不同的流式处理
        if isinstance(data, str):
            # 如果输入是字符串，按行流式输出
            lines = data.strip().split('\n')
            for line in lines:
                result = NodeResult()
                result.set('output', line)
                yield result
        elif isinstance(data, list):
            # 如果输入是列表，逐个元素流式输出
            for item in data:
                result = NodeResult()
                result.set('output', item)
                yield result
        else:
            # 其他类型数据，作为单条流式结果输出
            result = NodeResult()
            result.set('output', data)
            yield result

    def process_output(self, port: str, data: Any) -> Any:
        """
        处理输出数据，根据端口类型返回不同的结果

        Args:
            port (str): 输出端口名称
            data (Any): 要处理的数据

        Returns:
            Any: 处理后的结果
        """
        # 这里可以根据不同的输出端口返回不同的处理结果
        if port == 'output':
            return data
        elif port == 'count':
            # 如果端口是count，返回数据的数量
            if isinstance(data, str):
                return len(data.strip().split('\n'))
            elif isinstance(data, list):
                return len(data)
            else:
                return 1
        else:
            # 未知端口，返回原始数据
            return data