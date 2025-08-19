from typing import Any, Dict, Optional
from .base_node import ComputeNode, NodeResult
import importlib
from  paddlex import create_model

class BaseModelNode(ComputeNode):
    """模型节点基类"""

    def __init__(self, config: Dict, pipeline: Any) -> None:
        """
        初始化模型节点

        Args:
            config (Dict): 节点配置
            pipeline (Any): 工作流管道实例
        """
        super().__init__(config, pipeline)
        self.model = None
        self.initialize_model()

    def initialize_model(self) -> None:
        """
        初始化模型
        """
        if "module_name" in self.params and "model_name" in self.params:
            try:
                # 构建模型配置
                config = {
                    "model_name": self.params.get("model_name"),
                    "model_dir": self.params.get("model_dir")
                }
                model_params = self.params.get("model_params", {})

                # 创建模型实例
                self.model = self.pipeline.create_model(config, **model_params)
                print(f"模型 {self.params['model_name']} 初始化成功")
            except Exception as e:
                raise ValueError(f"创建模型 {self.params.get('model_name')} 失败: {str(e)}")
        else:
            raise ValueError(f"节点 {self.id} 缺少必要的模型配置")

    def _run_compute(self, port: str, data: Any) -> 'NodeResult':
        """
        运行模型推理计算

        Args:
            port (str): 输入端口名称
            input_data (Any): 输入数据

        Returns:
            NodeResult: 节点运行结果封装对象
        """
        try:
            input_data=self.prepare_input(port,data)
            results=[]
            for item in self.model(input_data, **self.params.get("infer_params", {})):
                results.append(item)
            return NodeResult(results, self)
        except Exception as e:
            raise RuntimeError(f"节点 {self.id} 运行失败: {str(e)}")

    def prepare_input(self,port:str,data: Any) -> Any:
        """
        准备模型输入数据
        Args:
            port (str): 输入端口名称
            data (Any): 输入数据
        Returns:
            Any: 处理后的输入数据
        """
        return data

    def process_output(self, result: Any, port: Optional[str] = None) -> Any:
        """
        处理模型输出结果

        Args:
            result (Any): 原始结果
            port (Optional[str], optional): 输出端口名称. Defaults to None.

        Returns:
            Any: 处理后的结果
        """
        # 基础实现：直接返回原始结果
        # 子类应根据不同的port实现特定的处理逻辑
        return result

def ModelNode(config:Dict,pipeline:Any)->BaseModelNode:
    """
    代理创建模型节点

    Args:
        config (Dict): 节点配置
        pipeline (Any): 工作流管道实例

    Returns:
        BaseModelNode: 模型节点实例
    """
    try:
        # 获取模型类型
        params=config.get("params", {})
        module_name = params["module_name"]
        class_name = f"{''.join(word.capitalize() for word in module_name.split('_'))}Node"

        # 动态导入模块
        module = importlib.import_module(f".{module_name}_node", package="pxs.workflow.nodes")

        # 获取模型节点类
        model_node_class = getattr(module, class_name, None)

        # 确保模型节点类存在
        assert model_node_class is not None, f"未找到模型节点类 {class_name}"

        # 创建模型节点实例
        return model_node_class(config, pipeline)
    except Exception as e:
        raise ValueError(f"创建模型节点失败: {str(e)}")
