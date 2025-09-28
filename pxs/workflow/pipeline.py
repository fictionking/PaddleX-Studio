
from typing import Any, Dict, Optional, Union, List, Set
import importlib
from collections import defaultdict
import threading
from queue import Queue, Empty
import time

from paddlex.inference.utils.hpi import HPIConfig
from paddlex.inference.utils.pp_option import PaddlePredictorOption
from paddlex.inference.pipelines import BasePipeline
from pxs.workflow.nodes.base_node import ComputeNode, ConstantNode, StreamNode
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
        max_executions: int = 0,
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
            max_executions (int, optional): 节点的最大执行次数，用于防止无限循环. Defaults to 0（不检查）
        """

        super().__init__(
            device=device, pp_option=pp_option, use_hpip=use_hpip, hpi_config=hpi_config
        )
        self.workflow_name = config.get("workflow_name", "Unnamed Workflow")
        self.config = config
        self.nodes = {}
        self.connections = {}
        self.max_executions = max_executions
        
        # 类成员变量，用于工作流执行
        self.execution_queue = []  # 执行队列，存储元组 (node_id, input_value, port)
        self.ran_nodes = []  # 已运行的节点列表
        self.run_nodes = []  # 正在运行的节点列表
        self.start_time = 0  # 开始时间
        self.execution_count = {}  # 节点执行次数记录
        # 流式节点相关成员变量
        self.stream_results_queue = Queue(maxsize=1000)  # 流式结果队列，设置最大容量为1000
        self.active_stream_nodes = set()  # 活动流式节点集合
        self.exception_queue = Queue()  # 线程间通信的异常队列
        self.stream_threads = []  # 流式节点线程集合

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
                node_module = importlib.import_module(f"pxs.workflow.nodes.{node_type}")
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
            from_port = edge["sourceHandle"]
            to_port = edge["targetHandle"]
            
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
        
    def _create_status_update(self, status, error=None):
        """
        创建状态更新对象

        Args:
            status: 当前状态
            error: 错误信息（可选）

        Returns:
            dict: 状态更新对象
        """
        elapsed_time = time.time() - self.start_time
        
        update = {
            'ran_nodes': self.ran_nodes,
            'run_nodes':self.run_nodes,
            'status': status,
            'elapsed_time': elapsed_time,
            'stream_queue_size': self.stream_results_queue.qsize()
        }
        if error is not None:
            update['error'] = error
        return update
        
    def _process_constant_nodes(self):
        """
        处理所有常量节点，并直接操作执行队列

        Yields:
            dict: 状态更新信息
        """
        for node_id, node in self.nodes.items():
            if isinstance(node, ConstantNode):
                try:
                    # 添加到正在运行的节点数组
                    self.run_nodes.append(node_id)
                    yield self._create_status_update('运行中')
                    
                    node_result = node.run()
                    self.execution_count[node_id] += 1
                    elapsed_time = time.time() - self.start_time
                    self.ran_nodes = [node_id for node_id, count in self.execution_count.items() if count > 0]
                    
                    # 传递常量节点结果到下一个节点
                    if node_id in self.connections:
                        for conn in self.connections[node_id]:
                            from_port = conn["from_port"]
                            to_node = conn["to_node"]
                            to_port = conn["to_port"]
                            
                            if to_node in self.nodes:
                                # 使用parse_port函数分解port
                                port_type, port_name = parse_port(to_port)
                                if port_type == 'params':
                                    # 如果是params类型，立即调用set_params
                                    self.nodes[to_node].set_params(port_name, node_result.get(from_port))
                                elif port_type == 'inputs':
                                    # 如果是inputs类型，直接添加到执行队列
                                    execution_queue_item = (to_node, node_result.get(from_port), port_name)
                                    self.execution_queue.append(execution_queue_item)
                                else:
                                    # 未知端口类型，返回错误
                                    yield self._create_status_update('失败', f"常量节点 {node_id} 连接到未知端口类型 {port_type}")
                                    return
                    
                    # 从正在运行的节点数组中移除
                    self.run_nodes.remove(node_id)
                    yield self._create_status_update('运行中')
                    
                except Exception as e:
                    # 如果出错，从正在运行的节点数组中移除
                    if node_id in self.run_nodes:
                        self.run_nodes.remove(node_id)
                    yield self._create_status_update('失败', f"处理常量节点 {node_id} 时发生错误: {str(e)}")
                    return
        
        return
        
    def _find_entry_nodes(self):
        """
        查找工作流的入口节点

        Returns:
            bool: 是否找到入口节点
        """
        # 获取所有有入边的节点
        nodes_with_incoming = set()
        for from_node, conns in self.connections.items():
            for conn in conns:
                if conn["to_node"] in self.nodes:
                    nodes_with_incoming.add(conn["to_node"])
                
        # 查找没有入边的节点作为入口
        for node_id, node in self.nodes.items():
            # 跳过常量节点
            if isinstance(node, ConstantNode):
                continue
            
            # 检查节点是否没有入边
            if node_id not in nodes_with_incoming:
                # 无需查找输入端口，直接设为None，因为入口节点无需输入值
                self.execution_queue.append((node_id, None, None))
        
        return len(self.execution_queue) > 0
        
    def _process_stream_result(self, items):
        """
        处理流式节点的结果

        设计说明：
        - 直接操作类成员变量execution_queue
        - yield只用于返回状态更新信息，不再返回队列项

        Args:
            items: 流式结果项

        Yields:
            dict: 状态更新信息
        """
        # 处理特殊的线程完成标记
        if len(items) == 3 and items[2] == 'thread_complete':
            node_id = items[0]
            # 从活动流式节点集合中移除
            self.active_stream_nodes.discard(node_id)
            # 从正在运行的节点数组中移除
            if node_id in self.run_nodes:
                self.run_nodes.remove(node_id)
            # 流式节点执行完成时设置execution_count，与非流式节点逻辑一致
            if node_id not in self.execution_count:
                self.execution_count[node_id] = 0
            if self.max_executions > 0:
                self.execution_count[node_id] += 1
            else:
                self.execution_count[node_id] = 1
            # 更新执行过的节点列表
            self.ran_nodes = [nid for nid, count in self.execution_count.items() if count > 0]
            # 输出状态更新 - 流式节点完成
            status_update = self._create_status_update('运行中')
            # 标记任务完成
            self.stream_results_queue.task_done()
            
            # 只yield状态更新信息
            yield status_update
            return
        
        stream_node_id, stream_result = items
        
        try:
            # 处理每条流式输出的连接
            if stream_node_id in self.connections:
                for conn in self.connections[stream_node_id]:
                    from_port = conn["from_port"]
                    to_node = conn["to_node"]
                    to_port = conn["to_port"]

                    if to_node in self.nodes:
                        port_type, port_name = parse_port(to_port)
                        if port_type == 'params':
                            # 如果是params类型，立即调用set_params
                            try:
                                self.nodes[to_node].set_params(port_name, stream_result.get(from_port))
                            except Exception as e:
                                # 从正在运行的节点数组中移除
                                if stream_node_id in self.run_nodes:
                                    self.run_nodes.remove(stream_node_id)
                                error_update = self._create_status_update('失败', f"设置节点 {to_node} 参数时发生错误: {str(e)}")
                                self.stream_results_queue.task_done()
                                yield error_update
                                return
                        elif port_type == 'inputs':
                            # 如果是inputs类型，直接操作execution_queue
                            queue_item = (to_node, stream_result.get(from_port), port_name)
                            self.execution_queue.append(queue_item)
                        else:
                            # 未知端口类型，返回错误
                            # 从正在运行的节点数组中移除
                            if stream_node_id in self.run_nodes:
                                self.run_nodes.remove(stream_node_id)
                            error_update = self._create_status_update('失败', f"未知端口类型 {port_type}")
                            self.stream_results_queue.task_done()
                            yield error_update
                            return
            
            # 标记任务完成
            self.stream_results_queue.task_done()
            
            # 输出状态更新 - 流式节点产生新结果
            self.ran_nodes = [node_id for node_id, count in self.execution_count.items() if count > 0]
            status_update = self._create_status_update('运行中')
            
            # 只yield状态更新信息
            yield status_update
            return
        except Exception as e:
            # 捕获异常并处理
            if stream_node_id in self.run_nodes:
                self.run_nodes.remove(stream_node_id)
            error_update = self._create_status_update('失败', f"处理流式节点 {stream_node_id} 结果时发生错误: {str(e)}")
            self.stream_results_queue.task_done()
            yield error_update
            return

    def _process_regular_node(self, current_node_id, input_value, port):
        """
        处理常规节点（非流式节点）的执行和结果处理

        Args:
            current_node_id: 当前执行的节点ID
            input_value: 输入值
            port: 输入端口

        Yields:
            dict: 状态更新信息
        """
        # 检查节点是否存在
        if current_node_id not in self.nodes:
            yield self._create_status_update('失败', f"节点 {current_node_id} 不存在于工作流中")
            return
        
        current_node = self.nodes[current_node_id]
        
        # 确保当前节点在execution_count中，初始化为0
        if current_node_id not in self.execution_count:
            self.execution_count[current_node_id] = 0
        
        # 输出运行中状态 - 节点开始执行
        # 添加到正在运行的节点数组
        self.run_nodes.append(current_node_id)
        yield self._create_status_update('运行中')

        # 检查是否超过最大执行次数（只有当max_executions > 0时才检查）
        if self.max_executions > 0 and self.execution_count[current_node_id] >= self.max_executions:
            print(f"警告: 节点 {current_node_id} 已达到最大执行次数 {self.max_executions}，跳过执行。")
            # 从正在运行的节点数组中移除
            self.run_nodes.remove(current_node_id)
            # 输出状态更新 - 节点跳过执行
            self.ran_nodes = [node_id for node_id, count in self.execution_count.items() if count > 0]
            yield self._create_status_update('运行中')
            return

        try:
            # 检查节点是否为流式节点
            if isinstance(current_node, StreamNode):
                # 标记为活动流式节点
                self.active_stream_nodes.add(current_node_id)
                # 创建并启动线程
                thread = threading.Thread(
                    target=self._stream_node_worker,  # 使用内部方法
                    args=(current_node_id, current_node, port, input_value),
                    daemon=True
                )
                self.stream_threads.append(thread)
                thread.start()
                return
            else:
                # 非流式节点，使用标准run方法
                node_result = current_node.run(port, input_value)
                # 用户指定的逻辑：max_executions>0时增加计数，max_executions=0时永远设为1
                if self.max_executions > 0:
                    self.execution_count[current_node_id] += 1
                else:
                    self.execution_count[current_node_id] = 1
                
                # 从正在运行的节点数组中移除
                self.run_nodes.remove(current_node_id)
                
                # 处理节点运行结果
                if node_result is not None:
                    # 输出状态更新 - 节点完成执行
                    self.ran_nodes = [node_id for node_id, count in self.execution_count.items() if count > 0]
                    yield self._create_status_update('运行中')
                    
                    # 处理节点的输出连接
                    if current_node_id in self.connections:
                        for conn in self.connections[current_node_id]:
                            from_port = conn["from_port"]
                            to_node = conn["to_node"]
                            to_port = conn["to_port"]

                            if to_node in self.nodes:
                                # 使用parse_port函数分解port
                                port_type, port_name = parse_port(to_port)
                                if port_type == 'params':
                                    # 如果是params类型，立即调用set_params
                                    try:
                                        self.nodes[to_node].set_params(port_name, node_result.get(from_port))
                                    except Exception as e:
                                        yield self._create_status_update('失败', f"设置节点 {to_node} 参数时发生错误: {str(e)}")
                                        return
                                elif port_type == 'inputs':
                                    # 如果是inputs类型，加入主执行队列
                                    self.execution_queue.append((to_node, node_result.get(from_port), port_name))
                                else:
                                    # 未知端口类型，返回错误
                                    yield self._create_status_update('失败', f"未知端口类型 {port_type}")
                                    return
                else:
                    # 节点没有返回结果
                    self.ran_nodes = [node_id for node_id, count in self.execution_count.items() if count > 0]
                    yield self._create_status_update('运行中')
                    return
        except Exception as e:
            # 节点执行错误
            # 从正在运行的节点数组中移除
            if current_node_id in self.run_nodes:
                self.run_nodes.remove(current_node_id)
            yield self._create_status_update('失败', f"节点 {current_node_id} 执行出错: {str(e)}")
            return

    def _stream_node_worker(self, node_id, node, port, input_value):
        """
        流式节点的工作线程函数

        Args:
            node_id: 节点ID
            node: 节点实例
            port: 输入端口
            input_value: 输入值
        """
        try:
            # 遍历流式输出的每条结果
            for stream_result in node._stream_output(port, input_value):
                # 将每条流式结果放入stream_results_queue
                self.stream_results_queue.put((node_id, stream_result))
            
            # 线程完成时，从run_nodes中移除节点（通过结果队列传递）
            self.stream_results_queue.put((node_id, None, 'thread_complete'))
        except Exception as e:
            # 将异常放入队列而不是直接抛出
            self.exception_queue.put((node_id, e))

    def predict(self, inputs: Dict = None):
        """
        执行工作流预测

        Args:
            inputs (Dict, optional): 工作流的输入参数. Defaults to None

        Yields:
            dict: 包含以下信息的状态更新对象:
                - ran_nodes: 已运行的节点ID清单
                - status: 当前流程运行状态(准备中, 运行中, 完成, 失败)
                - elapsed_time: 当前流程已运行耗时(秒)
                - result: 可选的工作流输出结果(仅在完成时返回)
                - error: 可选的错误信息(仅在失败时返回)
                - run_nodes: 正在运行的节点ID数组(运行中时返回)
        """
        # 重置执行相关的成员变量
        self.execution_queue = []
        self.ran_nodes = []
        self.run_nodes = []
        self.start_time = time.time()
        self.stream_results_queue = Queue(maxsize=1000)  # 流式结果队列，设置最大容量为1000
        self.active_stream_nodes = set()  # 活动流式节点集合
        self.exception_queue = Queue()  # 线程间通信的异常队列
        self.stream_threads = []  # 流式节点线程集合
        
        try:
            # 输出准备中状态
            yield self._create_status_update('准备中')
            
            self.initialize_nodes()
            self.initialize_connections()

            # 记录节点被执行的次数，防止无限循环
            self.execution_count = {node_id: 0 for node_id, node in self.nodes.items()}

            # 首先处理所有常量节点
            constant_processor = self._process_constant_nodes()
            for status_update in constant_processor:
                if isinstance(status_update, dict):
                    # 如果是状态更新对象，直接yield
                    yield status_update
                    # 如果发生错误，状态更新中包含错误信息，应该终止处理
                    if status_update.get('status') == '失败':
                        return

            # 查找启动入口
            if not self.execution_queue and not self._find_entry_nodes():
                yield self._create_status_update('失败', "无法确定工作流的入口节点，请确保工作流中包含没有入边的节点作为入口")
                return

            # 执行队列中的节点
            while self.execution_queue or not self.stream_results_queue.empty() or self.active_stream_nodes or self.stream_threads:
                # 检查异常队列
                while not self.exception_queue.empty():
                    node_id, error = self.exception_queue.get()
                    self.active_stream_nodes.discard(node_id)
                    # 从正在运行的节点数组中移除
                    if node_id in self.run_nodes:
                        self.run_nodes.remove(node_id)
                    yield self._create_status_update('失败', f"流式节点 {node_id} 执行出错: {str(error)}")
                    # 清理线程
                    for thread in self.stream_threads:
                        if thread.is_alive():
                            # 注意：这里不能强制终止线程，只能等待其自然结束
                            pass
                    return

                # 优先处理流式节点产生的结果
                # 修改为每次只处理一个流式结果，而不是循环处理所有结果
                if not self.stream_results_queue.empty():
                    try:
                        # 使用非阻塞方式获取队列元素，避免阻塞
                        items = self.stream_results_queue.get_nowait()
                        
                        # 处理流式结果
                        stream_processor = self._process_stream_result(items)
                        
                        # 处理流式结果处理器产生的状态更新
                        for status_update in stream_processor:
                            yield status_update
                            # 如果发生错误，状态更新中包含错误信息，应该终止处理
                            if isinstance(status_update, dict) and status_update.get('status') == '失败':
                                # 清理线程
                                for thread in self.stream_threads:
                                    if thread.is_alive():
                                        pass
                                # 标记任务完成后再返回
                                self.stream_results_queue.task_done()
                                return
                        
                        # 标记任务完成
                        self.stream_results_queue.task_done()
                    except Empty:
                        # 队列为空，跳过处理
                        pass
                
                # 清理已完成的线程
                self.stream_threads = [t for t in self.stream_threads if t.is_alive()]
                
                # 处理主执行队列
                if self.execution_queue:
                    current_node_id, input_value, port = self.execution_queue.pop(0)
                    
                    node_processor = self._process_regular_node(current_node_id, input_value, port)
                    
                    for status_update in node_processor:
                        # 状态更新
                        yield status_update
                        # 如果发生错误，状态更新中包含错误信息，应该终止处理
                        if status_update.get('status') == '失败':
                            return

            # 所有节点执行完毕，工作流完成，输出完成状态
            yield self._create_status_update('完成')
        except Exception as e:
            # 捕获所有其他异常
            yield self._create_status_update('失败', f"工作流执行时发生错误: {str(e)}")
            # 清理线程
            for thread in self.stream_threads:
                if thread.is_alive():
                    pass
        return
