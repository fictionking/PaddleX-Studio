from typing import Any, Optional
from .model import BaseImageCVNode
import numpy as np

class ImageClassificationNode(BaseImageCVNode):
    """图像分类节点"""

    def process_output(self, result: Any, port: Optional[str] = None) -> Any:
        """
        处理图像分类模型输出结果

        Args:
            result (Any): 模型原始输出
            from_port (Optional[str], optional): 输出端口名称. Defaults to None.

        Returns:
            Any: 处理后的结果，类型取决于from_port参数
        """
        assert port=="labels",f"节点输出端口必须是labels，当前端口是{port}"
        if isinstance(result,list):
            ret=[]
            for item in result:
                obj={
                    "class_ids": item["class_ids"].tolist() if isinstance(item["class_ids"],np.ndarray) else item["class_ids"],  # 将ndarray转换为列表，保持维度不变
                    "scores": item["scores"].tolist() if isinstance(item["scores"],np.ndarray) else item["scores"],        # 将ndarray转换为列表，保持维度不变
                    "label_names": item["label_names"],
                }
                ret.append(obj)
            return ret
        else:
            return {
                "class_ids": result["class_ids"].tolist() if isinstance(result["class_ids"],np.ndarray) else result["class_ids"],
                "scores": result["scores"].tolist() if isinstance(result["scores"],np.ndarray) else result["scores"],
                "label_names": result["label_names"],
            }