from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union, List
import os
from pxs.workflow.common.utils import parse_port

class NodeResult:
    """节点运行结果类

    用于封装节点运行结果，并支持根据fromPort参数动态返回不同类型的值
    """

    def __init__(self, raw_result: Any, node: 'BaseNode') -> None:
        """
        初始化节点结果

        Args:
            raw_result (Any): 原始运行结果
            node (BaseNode): 节点实例
        """
        self.value = raw_result
        self.node = node
        self.processed_results: Dict[str, Any] = {}

    def get(self, port: str) -> Any:
        """
        根据port参数获取对应类型的结果

        Args:
            port (str): 输出端口名称.

        Returns:
            Any: 对应端口的结果
        """
        port_type, port_name=parse_port(port)
        if port_type != "outputs":
            raise ValueError(f"get only supports 'outputs' port type, got {port}")
        return self.__getattr__(port_name)

    def __getattr__(self, name: str) -> Any:
        """
        支持通过属性访问结果

        Args:
            name (str): 属性名

        Returns:
            Any: 对应属性的结果
        """
        if name in self.processed_results:
            return self.processed_results[name]

        # 调用节点的process_output方法处理结果
        result = self.node.process_output(self.value, name)

        self.processed_results[name] = result
        return result


class BaseNode(ABC):
    """节点抽象基类

    所有工作流节点都应继承自此类，提供统一的接口和公共功能
    """

    def __init__(self, config: Dict, pipeline: Any) -> None:
        """
        初始化节点

        Args:
            config (Dict): 节点配置
            pipeline (Any): 工作流管道实例
        """
        self.id = config["id"]
        self.name = config["name"]
        self.type = config["type"]
        self.params = config.get("params", {})
        pass

    def set_params(self, port: str, data: Any) -> None:
        """
        设置节点参数

        Args:
            port (str): 参数端口（必需）
            data (Any): 参数数据
        """
        params_path=port.split(".")
        # 处理嵌套参数路径
        current = self.params
        for i, param in enumerate(params_path):
            if i == len(params_path) - 1:
                current[param] = data
            else:
                if param not in current:
                    current[param] = {}
                current = current[param]

    @abstractmethod
    def run(self, port: str, data: Any) -> 'NodeResult':
        """
        运行节点

        Args:
            port (str): 输入端口名称
            data (Any): 输入数据

        Returns:
            NodeResult: 节点运行结果封装对象
        """
        pass
    
    def process_output(self, result: Any, port: Optional[str] = None) -> Any:
        """
        处理输出结果

        Args:
            result (Any): 原始结果
            from_port (Optional[str], optional): 输出端口名称. Defaults to None.

        Returns:
            Any: 处理后的结果
        """
        # 基类实现简单返回原始结果
        return result

    def _ensure_dir_exists(self, dir_path: str) -> None:
        """
        确保文件所在目录存在

        Args:
            dir_path (str): 目录路径
        """
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
            
class ConstantNode(BaseNode):
    """常量节点抽象类

    常量节点是在启动时一次性处理并输出的，它在所有动态节点之前运行
    """

    def __init__(self, config: Dict, pipeline: Any) -> None:
        """
        初始化常量节点

        Args:
            config (Dict): 节点配置
            pipeline (Any): 工作流管道实例
        """
        super().__init__(config, pipeline) 
        # 标记常量节点是否已运行
        self.has_run = False
        # 缓存常量节点的运行结果
        self.result_cache = None

    def run(self, port: str = None, data: Any = None) -> 'NodeResult':
        """
        运行常量节点

        特点：只运行一次，结果会被缓存

        Args:
            port (str, optional): 输入端口名称. Defaults to None.
            data (Any, optional): 输入数据. Defaults to None.

        Returns:
            NodeResult: 节点运行结果封装对象
        """
        if not self.has_run:
            # 直接使用输入数据
            result = self._run_constant()
            # 缓存结果
            self.result_cache = result
            self.has_run = True
        return self.result_cache

    @abstractmethod
    def set_value(self, value: Any) -> None:
        """
        设置节点常量值

        Args:
            value (Any): 常量值

        Returns:
            None
        """
        pass

    @abstractmethod
    def _run_constant(self) -> 'NodeResult':
        """
        常量节点的具体运行逻辑

        Returns:
            NodeResult: 节点运行结果封装对象
        """
        pass


class ComputeNode(BaseNode):
    """运算节点抽象类

    运算节点是根据输入变化实时计算输出的，只有当input有数据时才运行
    """

    def __init__(self, config: Dict, pipeline: Any) -> None:
        """
        初始化运算节点

        Args:
            config (Dict): 节点配置
            pipeline (Any): 工作流管道实例
        """
        super().__init__(config, pipeline)

    def run(self, port: str, data: Any) -> 'NodeResult':
        """
        运行运算节点

        特点：只有当输入有数据时才运行

        Args:
            port (str): 输入端口名称
            data (Any): 输入数据

        Returns:
            NodeResult: 节点运行结果封装对象
        """
        # 直接使用输入数据
        return self._run_compute(port,data)

    @abstractmethod
    def _run_compute(self,port: str, data: Any) -> 'NodeResult':
        """
        运算节点的具体运行逻辑

        Args:
            port (str): 输入端口名称
            data (Any): 输入数据

        Returns:
            NodeResult: 节点运行结果封装对象
        """
        pass


class StreamNode(ComputeNode):
    """流式输出节点抽象类

    流式输出节点能够在运行过程中逐步输出多条数据，每条数据都能立即传递到下游节点进行处理
    在WorkflowPipeline中，流式节点会在单独的线程中运行，避免阻塞主执行队列
    """

    def __init__(self, config: Dict, pipeline: Any) -> None:
        """
        初始化流式节点

        Args:
            config (Dict): 节点配置
            pipeline (Any): 工作流管道实例
        """
        super().__init__(config, pipeline)

    def run(self, port: str, data: Any) -> 'NodeResult':
        """
        运行流式节点（非流式调用方式）

        注意：在标准工作流执行中，此方法通常不会被直接调用，而是由WorkflowPipeline
        创建单独的线程并调用_stream_output方法来处理流式输出。
        这个方法主要用于非流式场景下获取完整结果，或作为流式处理的回退机制。

        Args:
            port (str): 输入端口名称
            data (Any): 输入数据

        Returns:
            NodeResult: 完整运行结果
        """
        # 调用计算方法获取完整结果
        return self._run_compute(port, data)
        
    @abstractmethod
    def _stream_output(self, port: str, data: Any):
        """
        流式输出的核心逻辑，每次yield一条数据
        
        在WorkflowPipeline中，这个方法会在单独的线程中被调用，产生的每条结果
        会通过队列传递回主线程，并立即发送到下游节点进行处理。

        Args:
            port (str): 输入端口名称
            data (Any): 输入数据
            
        Yields:
            NodeResult: 每条流式输出的结果
        """
        pass
