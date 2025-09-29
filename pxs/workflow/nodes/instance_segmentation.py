from typing import Any, Optional
from .model import BaseImageCVNode
from pxs.workflow.common.utils import sub_image_with_mask


class InstanceSegmentationNode(BaseImageCVNode):
    """实例分割节点"""

    def process_output(self, result: Any, port: Optional[str] = None) -> Any:
        """
        处理实例分割模型输出结果

        Args:
            result (Any): 模型原始输出
            from_port (Optional[str], optional): 输出端口名称. Defaults to None.

        Returns:
            Any: 处理后的结果，类型取决于from_port参数
        """
        assert port=="images" or port=="boxes" or port=="count",f"节点输出端口必须是images或boxes或count，当前端口是{port}"
        if isinstance(result,list):
            if port=="count":
                return len(result)
            ret=[]
            for item in result:
                boxes = item["boxes"]
                if not boxes:
                    continue
                match port:
                    case "images":
                        image=item["input_img"]
                        masks = item["masks"]
                        ret.extend(sub_image_with_mask(image,boxes,masks))
                    case "boxes":
                        ret.append(boxes)
            if ret:
                return ret
            return None
        else:
            if not result or not isinstance(result,dict):
                return None
            boxes = result["boxes"]
            if not boxes:
                return None
            match port:
                case "images":
                    image=result["input_img"]
                    masks = result["masks"]
                    return sub_image_with_mask(image,boxes,masks)
                case "boxes":
                    return boxes
                case "count":
                    return 1
