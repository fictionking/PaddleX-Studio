from typing import Any, Optional
from .model import BaseModelNode

class ImageFeatureNode(BaseModelNode):
    """图像特征节点"""

    def process_output(self, result: Any, port: Optional[str] = None) -> Any:
        """
        处理图像特征模型输出结果

        Args:
            result (Any): 模型原始输出
            from_port (Optional[str], optional): 输出端口名称. Defaults to None.

        Returns:
            Any: 处理后的结果，类型取决于from_port参数
        """
        assert port=="features",f"输出端口必须是features，当前端口是{port}"
        if isinstance(result,list):
            ret=[]
            for index, item in enumerate(result):
                obj={
                    "index": index,
                    "feature": item["feature"].tolist()  # 将ndarray转换为列表，保持维度不变   
                }
                ret.append(obj)
            return ret
        else:
            return {
                "index":0,
                "feature": result["feature"].tolist()
            }