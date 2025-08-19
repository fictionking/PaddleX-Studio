from typing import Any, Dict, Optional, Union
from .base_node import ConstantNode,NodeResult

class NumberInputNode(ConstantNode):
    """数字输入节点"""

    def __init__(self, config: Dict, pipeline: Any) -> None:
        """
        初始化数字输入节点

        Args:
            config (Dict): 节点配置
            pipeline (Any): 工作流管道实例
        """
        super().__init__(config, pipeline)
        self.value = self.params.get("default_value", 5)  # 默认值

    def set_input(self, data: Any, port: Optional[str] = None) -> None:
        """
        设置节点输入值

        Args:
            data (Any): 输入数据
            port (Optional[str], optional): 输入端口. Defaults to None
        """
        if port == "value" or not port:
            try:
                self.value = float(data)
                # 如果是整数，转换为int类型
                if self.value.is_integer():
                    self.value = int(self.value)
            except (ValueError, TypeError) as e:
                raise ValueError(f"节点 {self.id} 输入值无效: {str(e)}")

    def prepare_input(self) -> Any:
        """
        准备节点输入值

        Returns:
            Any: 节点输入值
        """
        return self.value

    def _run_constant(self, input_data: Any) -> NodeResult:
        """
        运行节点，返回数字值

        Returns:
            Union[int, float]: 数字值
        """
        return NodeResult(input_data,self)
