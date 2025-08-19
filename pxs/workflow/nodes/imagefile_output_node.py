from typing import Any, Dict,Optional
from .base_node import ComputeNode, NodeResult
import os
import json
from PIL import Image
import numpy as np

class ImagefileOutputNode(ComputeNode):
    """图像文件输出节点

    用于将输入数据写入图像文件
    """

    def __init__(self, config: Dict, pipeline: Any) -> None:
        """
        初始化图像文件输出节点

        Args:
            config (Dict): 节点配置
            pipeline (Any): 工作流管道实例
        """
        super().__init__(config, pipeline)

        # 确保输出目录存在
        output_path = self.params.get("path", "output")
        self._ensure_dir_exists(output_path)

    def _run_compute(self, port: str, data: Any) -> NodeResult:
        """
        运行节点，将输入数据写入图像文件

        Args:
            port (str): 输入端口名称
            data (Any): 输入数据

        Returns:
            NodeResult: 包含输出文件路径的结果对象
        """
        assert port=="images",f"图像文件输出节点输入端口必须是images，当前端口是{port}"
        # 写入文件
        output_path = self.params.get("path", "output")
        format_type = self.params.get("format", "png")
        try:
            files=[]
            if isinstance(data, list):
                for i, data in enumerate(data):
                    if isinstance(data, np.ndarray):
                        image = Image.fromarray(data)
                        image.save(os.path.join(output_path, f"{self.id}_{i}.{format_type}"))
                        files.append(os.path.join(output_path, f"{self.id}_{i}.{format_type}"))
            else:
                if isinstance(data, np.ndarray):
                    image = Image.fromarray(data)
                    image.save(os.path.join(output_path, f"{self.id}.{format_type}"))
                    files.append(os.path.join(output_path, f"{self.id}.{format_type}"))
                else:
                    raise ValueError(f"图像文件输出节点 {self.id} 输入数据类型无效: {type(data)}")  
            # 返回文件路径
            return NodeResult(files, self)
        except Exception as e:
            raise RuntimeError(f"节点 {self.id} 写入文件失败: {str(e)}")

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