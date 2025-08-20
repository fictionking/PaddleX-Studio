from typing import Any, Dict

from .base_node import ConstantNode,NodeResult

class NumberConstNode(ConstantNode):
    """数字常量节点"""

    def set_value(self, value: Any) -> None:
        """
        设置节点常量值

        Args:
            value (Any): 常量值

        Returns:
            None
        """
        self.set_params("value",value)

    def _run_constant(self) -> NodeResult:
        """
        运行节点，返回数字值

        Returns:
            NodeResult: 节点运行结果封装对象
        """
        return NodeResult(self.params.get("value", 0),self)
