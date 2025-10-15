from typing import Any, Optional
from .model import BaseImageInputModelNode

class FormulaRecognitionNode(BaseImageInputModelNode):
    """公式识别节点"""

    def process_output(self, result: Any, port: Optional[str] = None) -> Any:
        """
        处理公式识别模型输出结果

        Args:
            result (Any): 模型原始输出
            port (Optional[str], optional): 输出端口名称. Defaults to None.

        Returns:
            Any: 处理后的结果，类型取决于port参数
        """
        assert port=="text",f"节点输出端口必须是text，当前端口是{port}" 
        if isinstance(result,list):
            ret=[]
            for item in result:
                txt=item["rec_formula"]
                ret.append(txt)
            return ret
        else:
            return [result["rec_formula"]]