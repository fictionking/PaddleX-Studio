from typing import Any, Dict, Optional,List
from pxs.workflow.nodes.base_node import NodeResult
from .model_node import BaseModelNode
import numpy as np

class ObjectDetectionNode(BaseModelNode):
    """目标检测节点"""

    def __init__(self, config: Dict, pipeline: Any) -> None:
        """
        初始化目标检测节点

        Args:
            config (Dict): 节点配置
            pipeline (Any): 工作流管道实例
        """
        super().__init__(config, pipeline)

    def prepare_input(self,port:str,data: Any) -> Any:
        """
        准备目标检测模型输入数据

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
        
    # def _run_compute(self, input_data: Any) -> NodeResult:
    #     # 运行模型推理
    #     try:
    #         results = []
    #         if isinstance(input_data, list):
    #             # 列表输入，每个元素都是np.ndarray,每个都执行一次推理并组成列表返回
    #             for item in input_data:
    #                 for result in self.model(item, **self.params.get("infer_params")):
    #                     results.append(result)
    #         else:
    #             # 单张图片输入，执行一次推理
    #             for result in self.model(input_data, **self.params.get("infer_params")):
    #                 results.append(result)
    #         return NodeResult(results,self)
    #     except Exception as e:
    #         raise RuntimeError(f"节点 {self.id} 运行失败: {str(e)}")

    def process_output(self, result: Any, port: Optional[str] = None) -> Any:
        """
        处理目标检测模型输出结果

        Args:
            result (Any): 模型原始输出
            from_port (Optional[str], optional): 输出端口名称. Defaults to None.

        Returns:
            Any: 处理后的结果，类型取决于from_port参数
        """
        if isinstance(result,list):
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
