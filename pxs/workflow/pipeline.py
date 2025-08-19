
from typing import Any, Dict, Optional, Union
import importlib

from paddlex.inference.utils.hpi import HPIConfig
from paddlex.inference.utils.pp_option import PaddlePredictorOption
from paddlex.inference.pipelines import BasePipeline
from pxs.workflow.nodes.base_node import ComputeNode, ConstantNode
from pxs.workflow.common.utils import parse_port

class WorkflowPipeline(BasePipeline):
    """Workflow Pipeline"""

    entities = "Workflow"

    def __init__(
        self,
        config: Dict,
        device: str = None,
        pp_option: PaddlePredictorOption = None,
        use_hpip: bool = False,
        hpi_config: Optional[Union[Dict[str, Any], HPIConfig]] = None,
    ) -> None:
        """
        初始化工作流管道

        Args:
            config (Dict): 包含各种设置的配置字典
            device (str, optional): 运行预测的设备. Defaults to None
            pp_option (PaddlePredictorOption, optional): PaddlePredictor选项. Defaults to None
            use_hpip (bool, optional): 是否使用高性能推理插件(HPIP). Defaults to False
            hpi_config (Optional[Union[Dict[str, Any], HPIConfig]], optional):
                高性能推理配置字典. Defaults to None
        """

        super().__init__(
            device=device, pp_option=pp_option, use_hpip=use_hpip, hpi_config=hpi_config
        )
        self.workflow_name = config["workflow_name"]
        self.config = config
        self.nodes = {}
        self.connections = {}
        self.initialize_nodes()
        self.initialize_connections()

    def initialize_nodes(self):
        """初始化工作流中的所有节点"""
        for node_config in self.config.get("nodes", []):
            node_id = node_config["id"]
            node_type = node_config["type"]

            # 根据节点类型动态导入节点类
            try:
                node_module = importlib.import_module(f"pxs.workflow.nodes.{node_type}_node")
                node_class = getattr(node_module, f"{''.join(word.capitalize() for word in node_type.split('_'))}Node")
                node = node_class(node_config, self)
                self.nodes[node_id] = node
            except (ImportError, AttributeError) as e:
                raise ValueError(f"Failed to initialize node {node_id}: {str(e)}")

    def initialize_connections(self):
        """初始化节点之间的连接"""
        for conn in self.config.get("connections", []):
            from_node = conn["from"].split(".")[0]
            from_port = ".".join(conn["from"].split(".")[1:])
            to_node = conn["to"].split(".")[0]
            to_port = ".".join(conn["to"].split(".")[1:])

            if from_node not in self.connections:
                self.connections[from_node] = []
            self.connections[from_node].append({
                "from_port": from_port,
                "to_node": to_node,
                "to_port": to_port
            })

    def _is_constant_node(self, node, error_msg):
        """
        检查节点是否为常量节点，如果是则抛出异常

        Args:
            node: 要检查的节点
            error_msg: 抛出的异常信息
        """
        if isinstance(node, ConstantNode):
            raise ValueError(error_msg)

    def predict(self, input: Any = None, **kwargs):
        """
        运行工作流预测

        Args:
            input_data (Any, optional): 输入数据. Defaults to None

        Yields:
            Any: 每当有节点连接到end时输出的结果
        """

        # 初始化执行队列，存储元组 (node_id, input_value, port)
        execution_queue = []

        # 首先处理所有常量节点
        for node_id, node in self.nodes.items():
            if isinstance(node, ConstantNode):
                # 检查kwargs中是否有与节点ID同名的输入参数
                if node_id in kwargs:
                    node.set_params("default_value", kwargs[node_id])
                node_result = node.run()
                
                # 传递常量节点结果到下一个节点
                if node_id in self.connections:
                    for conn in self.connections[node_id]:
                        from_port = conn["from_port"]
                        to_node = conn["to_node"]
                        to_port = conn["to_port"]
                        if to_node in self.nodes:
                            # 检查to_node是否为常量节点
                            self._is_constant_node(self.nodes[to_node], f"常量节点 {node_id} 不能连接到常量节点 {to_node}")
                            # 使用parse_port函数分解port
                            port_type, port_name = parse_port(to_port)
                            if port_type == 'params':
                                # 如果是params类型，立即调用set_params
                                self.nodes[to_node].set_params(port_name, node_result.get(from_port))
                            elif port_type == 'inputs':
                                # 常量节点不能给inputs类型赋值，抛出异常
                                raise ValueError(f"常量节点 {node_id} 不能连接到 inputs 类型端口 {to_port}")
                            else:
                                # 未知端口类型，抛出异常
                                raise ValueError(f"常量节点 {node_id} 连接到未知端口类型 {port_type}")

        # 设置输入数据到所有从start节点连接的节点，并加入执行队列
        if input is not None:
            for conn in self.connections.get("start", []):
                to_node = conn["to_node"]
                to_port = conn["to_port"]
                if to_node in self.nodes:
                    # 检查to_node是否为常量节点
                    self._is_constant_node(self.nodes[to_node], f"start节点不能连接到常量节点 {to_node}")
                    port_type, port_name = parse_port(to_port)
                    if port_type == 'params':
                        # start节点不能连接到params类型端口，抛出异常
                        raise ValueError(f"start节点不能连接到params类型端口 {to_port}")
                    elif port_type == 'inputs':
                        # 如果是inputs类型，加入执行队列
                        execution_queue.append((to_node, input, port_name))
                    else:
                        # 未知端口类型，抛出异常
                        raise ValueError(f"未知端口类型 {port_type}")

        # 记录节点被执行的次数，防止无限循环
        execution_count = {node_id: 0 for node_id, node in self.nodes.items() if isinstance(node, ComputeNode)}
        max_executions = 100  # 设置最大执行次数以防止无限循环

        # 执行队列中的节点
        while execution_queue:
            current_node_id, input_value, port = execution_queue.pop(0)
            current_node = self.nodes[current_node_id]

            # 检查是否超过最大执行次数
            if execution_count[current_node_id] >= max_executions:
                print(f"警告: 节点 {current_node_id} 已达到最大执行次数 {max_executions}，跳过执行。")
                continue

            # 直接执行节点，传入port_name和数据
            node_result = current_node.run(port, input_value)
            execution_count[current_node_id] += 1

            # 传递运算节点结果到下一个节点
            if current_node_id in self.connections:
                for conn in self.connections[current_node_id]:
                    from_port = conn["from_port"]
                    to_node = conn["to_node"]
                    to_port = conn["to_port"]

                    # 检查是否连接到end节点
                    if to_node == "end":
                        yield node_result.get(from_port)
                        continue

                    if to_node in self.nodes:
                        # 检查to_node是否为常量节点
                        self._is_constant_node(self.nodes[to_node], f"运算节点 {current_node_id} 不能连接到常量节点 {to_node}")
                        # 使用parse_port函数分解port
                        port_type, port_name = parse_port(to_port)
                        if port_type == 'params':
                            # 如果是params类型，立即调用set_params
                            self.nodes[to_node].set_params(port_name, node_result.get(from_port))
                        elif port_type == 'inputs':
                            # 如果是inputs类型，加入执行队列
                            execution_queue.append((to_node, node_result.get(from_port), port_name))
                        else:
                            # 未知端口类型，抛出异常
                            raise ValueError(f"未知端口类型 {port_type}")
