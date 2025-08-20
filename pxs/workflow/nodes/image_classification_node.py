from typing import Any, Dict, Optional
from typing import Any, Dict, Optional
from .model_node import BaseModelNode
import cv2
import numpy as np

class ImageClassificationNode(BaseModelNode):
    """图像分类节点"""

    def prepare_input(self,port:str,data: Any) -> Any:
        """
        准备图像分类模型输入数据

        Args:
            port (str): 输入端口名称
            data (Any): 输入数据

        Returns:
            Any: 处理后的输入数据
        """

        # 获取原始输入数据
        assert port=="images",f"图像分类节点输入端口必须是images，当前端口是{port}"
        # 检查输入数据是否为空
        if not data:
            raise ValueError("输入数据不能为空")
        # 检查输入数据是否为图像
        if not isinstance(data, (np.ndarray, list)):
            raise TypeError(f"不支持的输入类型: {type(data)}")
        # 如果是列表，检查列表中的所有元素是否都是np.ndarray
        if isinstance(data, list) and not all(isinstance(item, np.ndarray) for item in data):
            raise TypeError("列表中的元素必须都是np.ndarray类型")
        return data

    def process_output(self, result: Any, port: Optional[str] = None) -> Any:
        """
        处理图像分类模型输出结果

        Args:
            result (Any): 模型原始输出
            from_port (Optional[str], optional): 输出端口名称. Defaults to None.

        Returns:
            Any: 处理后的结果，类型取决于from_port参数
        """
        assert port=="labels",f"图像分类节点输出端口必须是labels，当前端口是{port}"
        if isinstance(result,list):
            ret=[]
            for item in result:
                obj={
                    "class_ids": item["class_ids"].tolist(),  # 将ndarray转换为列表，保持维度不变
                    "scores": item["scores"].tolist(),        # 将ndarray转换为列表，保持维度不变
                    "label_names": item["label_names"],
                }
                ret.append(obj)
            return ret
        else:
            return {
                "class_ids": result["class_ids"].tolist(),
                "scores": result["scores"].tolist(),
                "label_names": result["label_names"],
            }