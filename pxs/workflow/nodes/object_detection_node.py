from typing import Any, Dict, Optional,List
from pxs.workflow.nodes.base_node import NodeResult
from .model_node import BaseModelNode
import numpy as np

class ObjectDetectionNode(BaseModelNode):
    """目标检测节点"""

    def prepare_input(self,port:str,data: Any) -> Any:
        """
        准备目标检测模型输入数据

        Args:
            port (str): 输入端口名称
            data (Any): 输入数据

        Returns:
            Any: 处理后的输入数据
        """
        # 获取原始输入数据
        assert port=="images",f"目标检测节点输入端口必须是images，当前端口是{port}"
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
        处理目标检测模型输出结果

        Args:
            result (Any): 模型原始输出
            from_port (Optional[str], optional): 输出端口名称. Defaults to None.

        Returns:
            Any: 处理后的结果，类型取决于from_port参数
        """
        assert port=="images" or port=="boxes" or port=="count",f"目标检测节点输出端口必须是images或boxes或count，当前端口是{port}"
        if isinstance(result,list):
            if port=="count":
                return len(result)
            ret=[]
            for item in result:
                boxes = item["boxes"]
                match port:
                    case "images":
                        image=item["input_img"]
                        ret.extend(sub_image(image,boxes))
                    case "boxes":
                        ret.append(boxes)
            return ret
        else:
            boxes = result["boxes"]
            match port:
                case "images":
                    image=result["input_img"]
                    return sub_image(image,boxes)
                case "boxes":
                    return boxes
                case "count":
                    return 1

def sub_image(image,boxes):
    images=[]
    for box in boxes:
        bbox=box["coordinate"]
        if len(bbox) == 4:
            xmin, ymin, xmax, ymax = bbox
        elif len(bbox) == 8:
            x1, y1, x2, y2, x3, y3, x4, y4 = bbox
            xmin, ymin, xmax, ymax = min(x1, x2, x3, x4), min(y1, y2, y3, y4), max(x1, x2, x3, x4), max(y1, y2, y3, y4)
        roi=image[int(ymin):int(ymax),int(xmin):int(xmax)]
        images.append(roi)
    return images
