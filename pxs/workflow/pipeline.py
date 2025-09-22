
from typing import Any, Dict, Optional, Union, List, Set
import importlib
from collections import defaultdict

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
        self.workflow_name = config.get("workflow_name", "Unnamed Workflow")
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
            node_data = node_config["data"]
            node_name = node_data.get("name", node_id)  # 如果没有name，使用id作为name
            node_params = node_data.get("params", {})
            node_config = {
                "id":node_id,
                "type":node_type,
                "name":node_name,
                "params":node_params
            }

            # 根据节点类型动态导入节点类
            try:
                node_module = importlib.import_module(f"pxs.workflow.nodes.{node_type}_node")
                node_class = getattr(node_module, f"{''.join(word.capitalize() for word in node_type.split('_'))}Node")
                node = node_class(node_config, self)
                self.nodes[node_id] = node
            except (ImportError, AttributeError) as e:
                # 如果是备注类型节点，可以跳过导入
                if node_type == "note":
                    continue
                raise ValueError(f"Failed to initialize node {node_id}: {str(e)}")

    def initialize_connections(self):
        """初始化节点之间的连接"""
        # 从edges初始化连接
        edges = self.config.get("edges", [])
        
        # 处理edges格式
        for edge in edges:
            from_node = edge["source"]
            to_node = edge["target"]
            from_port = edge["sourceHandle"].split(".")[1] if "." in edge["sourceHandle"] else edge["sourceHandle"]
            to_port = edge["targetHandle"].split(".")[1] if "." in edge["targetHandle"] else edge["targetHandle"]
            
            if from_node not in self.connections:
                self.connections[from_node] = []
            self.connections[from_node].append({
                "from_port": from_port,
                "to_node": to_node,
                "to_port": to_port
            })

    def _is_constant_node(self, node, error_msg):
        """
        检查节点是否为常量节点

        Args:
            node: 要检查的节点
            error_msg: 错误信息

        Returns:
            bool: 如果是常量节点返回True，否则返回False
        """
        return isinstance(node, ConstantNode)

    def predict(self, input=None, **kwargs):
        """
        运行工作流预测并输出运行状态信息，所有异常都会封装成标准输出结构输出
        
        注：此方法的输入参数结构主要是为了实现基类接口要求，
        实际逻辑主要使用kwargs中的参数，input参数在实际逻辑中不会使用。

        Args:
            input: 为了实现基类接口要求而保留，实际逻辑中不会使用
            **kwargs: 其他参数，可包含:
                - input_node_id: 输入节点ID
                - input_port: 输入端口名
                - output_node_id: 输出节点ID
                - output_port: 输出端口名
                - 以及其他覆盖常量节点的值的参数

        Yields:
            dict: 包含工作流运行状态信息，包括:
                - running_nodes: 正在运行的节点ID清单
                - status: 当前流程运行状态（准备中、运行中、完成、失败）
                - elapsed_time: 当前流程已运行耗时（秒）
                - result: 可选的工作流输出结果（仅在完成时返回）
                - error: 可选的错误信息（仅在失败时返回）
                - current_node: 当前处理的节点ID（运行中时返回）
                - node_status: 当前节点的状态（运行中时返回）
        """
        import time

        # 从kwargs中提取参数
        input_node_id = kwargs.pop('input_node_id', None)
        input_port = kwargs.pop('input_port', None)
        output_node_id = kwargs.pop('output_node_id', None)
        output_port = kwargs.pop('output_port', None)

        # 初始化执行队列，存储元组 (node_id, input_value, port)
        execution_queue = []
        # 记录正在运行的节点
        running_nodes = []
        # 记录开始时间
        start_time = time.time()
        
        try:
            # 输出准备中状态
            elapsed_time = time.time() - start_time
            yield {
                'running_nodes': running_nodes,
                'status': '准备中',
                'elapsed_time': elapsed_time
            }

            # 首先处理所有常量节点
            for node_id, node in self.nodes.items():
                if isinstance(node, ConstantNode):
                    try:
                        # 检查kwargs中是否有与节点ID同名的输入参数
                        if node_id in kwargs:
                            node.set_value(kwargs[node_id])
                        node_result = node.run()
                        
                        # 传递常量节点结果到下一个节点
                        if node_id in self.connections:
                            for conn in self.connections[node_id]:
                                from_port = conn["from_port"]
                                to_node = conn["to_node"]
                                to_port = conn["to_port"]
                                
                                if to_node in self.nodes:
                                    # 检查to_node是否为常量节点
                                    if self._is_constant_node(self.nodes[to_node], f"常量节点 {node_id} 不能连接到常量节点 {to_node}"):
                                        elapsed_time = time.time() - start_time
                                        yield {
                                            'running_nodes': running_nodes,
                                            'status': '失败',
                                            'elapsed_time': elapsed_time,
                                            'error': f"常量节点 {node_id} 不能连接到常量节点 {to_node}"
                                        }
                                        return
                                        
                                    # 使用parse_port函数分解port
                                    port_type, port_name = parse_port(to_port)
                                    if port_type == 'params':
                                        # 如果是params类型，立即调用set_params
                                        self.nodes[to_node].set_params(port_name, node_result.get(from_port))
                                    elif port_type == 'inputs':
                                        # 常量节点不能给inputs类型赋值，返回错误
                                        elapsed_time = time.time() - start_time
                                        yield {
                                            'running_nodes': running_nodes,
                                            'status': '失败',
                                            'elapsed_time': elapsed_time,
                                            'error': f"常量节点 {node_id} 不能连接到 inputs 类型端口 {to_port}"
                                        }
                                        return
                                    else:
                                        # 未知端口类型，返回错误
                                        elapsed_time = time.time() - start_time
                                        yield {
                                            'running_nodes': running_nodes,
                                            'status': '失败',
                                            'elapsed_time': elapsed_time,
                                            'error': f"常量节点 {node_id} 连接到未知端口类型 {port_type}"
                                        }
                                        return
                    except Exception as e:
                        elapsed_time = time.time() - start_time
                        yield {
                            'running_nodes': running_nodes,
                            'status': '失败',
                            'elapsed_time': elapsed_time,
                            'error': f"处理常量节点 {node_id} 时发生错误: {str(e)}"
                        }
                        return

                # 如果指定了输入节点和端口，添加到执行队列
                if input_node_id and input_port and node_id == input_node_id:
                    execution_queue.append((node_id, input, input_port))

            # 如果没有通过input_node_id指定入口节点，则查找默认入口
            if not execution_queue:
                # 获取所有有入边的节点
                nodes_with_incoming = set()
                for from_node, conns in self.connections.items():
                    for conn in conns:
                        if conn["to_node"] in self.nodes:
                            nodes_with_incoming.add(conn["to_node"])
                        
                # 查找有输入端口但没有入边的节点作为入口
                for node_id, node in self.nodes.items():
                    # 跳过常量节点
                    if isinstance(node, ConstantNode):
                        continue
                    
                    # 检查节点是否有输入端口
                    if hasattr(node, 'data') and 'inputs' in node.data and len(node.data['inputs']) > 0:
                        # 检查节点是否没有入边
                        if node_id not in nodes_with_incoming:
                            # 使用第一个输入端口
                            first_input_port = node.data['inputs'][0]
                            execution_queue.append((node_id, input, first_input_port))
                            break  # 只使用第一个找到的入口节点
                        
                # 如果没有找到合适的入口节点，返回错误
                if not execution_queue:
                    elapsed_time = time.time() - start_time
                    yield {
                        'running_nodes': running_nodes,
                        'status': '失败',
                        'elapsed_time': elapsed_time,
                        'error': "无法确定工作流的入口节点，请明确指定 input_node_id 和 input_port 参数"
                    }
                    return

            # 记录节点被执行的次数，防止无限循环
            execution_count = {node_id: 0 for node_id, node in self.nodes.items() if isinstance(node, ComputeNode)}
            max_executions = 100  # 设置最大执行次数以防止无限循环

            # 存储最终结果
            final_results = []

            # 执行队列中的节点
            while execution_queue:
                current_node_id, input_value, port = execution_queue.pop(0)
                
                # 检查节点是否存在
                if current_node_id not in self.nodes:
                    elapsed_time = time.time() - start_time
                    yield {
                        'running_nodes': running_nodes,
                        'status': '失败',
                        'elapsed_time': elapsed_time,
                        'error': f"节点 {current_node_id} 不存在于工作流中"
                    }
                    return
                
                current_node = self.nodes[current_node_id]
                
                # 更新正在运行的节点列表
                running_nodes = [node_id for node_id, count in execution_count.items() if count > 0] + [current_node_id]
                # 输出运行中状态 - 节点开始执行
                elapsed_time = time.time() - start_time
                yield {
                    'running_nodes': running_nodes,
                    'status': '运行中',
                    'elapsed_time': elapsed_time,
                    'current_node': current_node_id,
                    'node_status': '开始执行'
                }

                # 检查是否超过最大执行次数
                if execution_count[current_node_id] >= max_executions:
                    print(f"警告: 节点 {current_node_id} 已达到最大执行次数 {max_executions}，跳过执行。")
                    # 输出状态更新 - 节点跳过执行
                    elapsed_time = time.time() - start_time
                    running_nodes = [node_id for node_id, count in execution_count.items() if count > 0]
                    yield {
                        'running_nodes': running_nodes,
                        'status': '运行中',
                        'elapsed_time': elapsed_time,
                        'current_node': current_node_id,
                        'node_status': '跳过执行'
                    }
                    continue

                try:
                    # 直接执行节点，传入port_name和数据
                    node_result = current_node.run(port, input_value)
                    execution_count[current_node_id] += 1
                    
                    # 输出状态更新 - 节点执行完成
                    elapsed_time = time.time() - start_time
                    running_nodes = [node_id for node_id, count in execution_count.items() if count > 0]
                    yield {
                        'running_nodes': running_nodes,
                        'status': '运行中',
                        'elapsed_time': elapsed_time,
                        'current_node': current_node_id,
                        'node_status': '执行完成'
                    }

                    # 处理输出
                    # 如果指定了输出节点和端口
                    if output_node_id and output_port and current_node_id == output_node_id:
                        if output_port in node_result:
                            final_results.append(node_result[output_port])
                            # 输出状态更新 - 结果已收集
                            elapsed_time = time.time() - start_time
                            yield {
                                'running_nodes': running_nodes,
                                'status': '运行中',
                                'elapsed_time': elapsed_time,
                                'current_node': current_node_id,
                                'node_status': '结果收集'
                            }
                    # 处理节点之间的连接
                    elif current_node_id in self.connections:
                        # 输出状态更新 - 开始处理连接
                        elapsed_time = time.time() - start_time
                        yield {
                            'running_nodes': running_nodes,
                            'status': '运行中',
                            'elapsed_time': elapsed_time,
                            'current_node': current_node_id,
                            'node_status': '处理连接'
                        }
                        
                        for conn in self.connections[current_node_id]:
                            from_port = conn["from_port"]
                            to_node = conn["to_node"]
                            to_port = conn["to_port"]

                            if to_node in self.nodes:
                                # 检查to_node是否为常量节点
                                if self._is_constant_node(self.nodes[to_node], f"运算节点 {current_node_id} 不能连接到常量节点 {to_node}"):
                                    elapsed_time = time.time() - start_time
                                    yield {
                                        'running_nodes': running_nodes,
                                        'status': '失败',
                                        'elapsed_time': elapsed_time,
                                        'error': f"运算节点 {current_node_id} 不能连接到常量节点 {to_node}",
                                        'current_node': current_node_id
                                    }
                                    return
                                    
                                # 使用parse_port函数分解port
                                try:
                                    port_type, port_name = parse_port(to_port)
                                except Exception as e:
                                    elapsed_time = time.time() - start_time
                                    yield {
                                        'running_nodes': running_nodes,
                                        'status': '失败',
                                        'elapsed_time': elapsed_time,
                                        'error': f"解析端口 {to_port} 时发生错误: {str(e)}",
                                        'current_node': current_node_id
                                    }
                                    return
                                    
                                if port_type == 'params':
                                    # 如果是params类型，立即调用set_params
                                    try:
                                        self.nodes[to_node].set_params(port_name, node_result.get(from_port))
                                    except Exception as e:
                                        elapsed_time = time.time() - start_time
                                        yield {
                                            'running_nodes': running_nodes,
                                            'status': '失败',
                                            'elapsed_time': elapsed_time,
                                            'error': f"设置节点 {to_node} 参数时发生错误: {str(e)}",
                                            'current_node': current_node_id
                                        }
                                        return
                                elif port_type == 'inputs':
                                    # 如果是inputs类型，加入执行队列
                                    execution_queue.append((to_node, node_result.get(from_port), port_name))
                                else:
                                    # 未知端口类型，返回错误
                                    elapsed_time = time.time() - start_time
                                    yield {
                                        'running_nodes': running_nodes,
                                        'status': '失败',
                                        'elapsed_time': elapsed_time,
                                        'error': f"未知端口类型 {port_type}",
                                        'current_node': current_node_id
                                    }
                                    return
                    # 如果未指定输出节点，但节点没有出边（可能是终点）
                    elif not output_node_id and current_node_id not in self.connections:
                        # 输出状态更新 - 开始收集结果
                        elapsed_time = time.time() - start_time
                        yield {
                            'running_nodes': running_nodes,
                            'status': '运行中',
                            'elapsed_time': elapsed_time,
                            'current_node': current_node_id,
                            'node_status': '收集结果'
                        }
                        # 收集所有端口的值
                        for port_name, value in node_result.items():
                            final_results.append(value)
                except Exception as e:
                    elapsed_time = time.time() - start_time
                    yield {
                        'running_nodes': running_nodes,
                        'status': '失败',
                        'elapsed_time': elapsed_time,
                        'error': f"执行节点 {current_node_id} 时发生错误: {str(e)}",
                        'current_node': current_node_id
                    }
                    return
        
            # 工作流执行完成
            elapsed_time = time.time() - start_time
            yield {
                'running_nodes': [],
                'status': '完成',
                'elapsed_time': elapsed_time,
                'result': final_results if final_results else None
            }
        except Exception as e:
            # 捕获所有未被前面捕获的异常
            elapsed_time = time.time() - start_time
            yield {
                'running_nodes': running_nodes,
                'status': '失败',
                'elapsed_time': elapsed_time,
                'error': f"工作流执行过程中发生未预期的错误: {str(e)}"
            }
            return
