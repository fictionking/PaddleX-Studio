from typing import Any, Dict,Optional
from .base_node import ComputeNode, NodeResult
import os
import json

class TextfileOutputNode(ComputeNode):
    """文本文件输出节点

    用于将输入数据写入文本文件
    """

    def __init__(self, config: Dict, pipeline: Any) -> None:
        """
        初始化文本文件输出节点

        Args:
            config (Dict): 节点配置
            pipeline (Any): 工作流管道实例
        """
        super().__init__(config, pipeline)

        # 确保输出目录存在
        output_path = self.params.get("path", "output/result.json")
        self._ensure_dir_exists(output_path)

    def _run_compute(self, input_data: Any) -> NodeResult:
        """
        运行节点，将输入数据写入文件

        Args:
            input_data (Any): 输入数据

        Returns:
            NodeResult: 包含输出文件路径的结果对象
        """
        # 写入文件
        output_path = self.params.get("path", "output/result.json")
        format_type = self.params.get("format", "json")

        try:
            if format_type.lower() == "json":
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(input_data, f, ensure_ascii=False, indent=2)
            else:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(str(input_data))
            return NodeResult(output_path, self)
        except Exception as e:
            raise RuntimeError(f"节点 {self.id} 写入文件失败: {str(e)}")

    def prepare_input(self) -> Any:
        """
        准备输入数据

        Returns:
            Any: 处理后的输入数据
        """
        # 如果有多个输入端口，将所有输入数据整合为一个字典
        if self.inputs and len(self.inputs) > 0:
            result = {}
            for port in self.inputs:
                if port in self.input_data:
                    result[port] = self.input_data[port]
            return result if result else self.input_data.get(self.inputs[0])
        return self.input_data.get("default")

    def process_output(self, result: Any, port: Optional[str] = None) -> Any:
        """
        处理输出结果

        Args:
            result (Any): 原始结果
            port (Optional[str], optional): 输出端口名称. Defaults to None.

        Returns:
            Any: 处理后的结果
        """
        # result是输出文件路径
        return result