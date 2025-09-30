from typing import Any, Optional
from .model import BaseImageCVNode
from pxs.workflow.common.utils import sub_image_with_pred


class SemanticSegmentationNode(BaseImageCVNode):
    """语义分割节点"""

    def process_output(self, result: Any, port: Optional[str] = None) -> Any:
        """
        处理语义分割模型输出结果

        Args:
            result (Any): 模型原始输出
            from_port (Optional[str], optional): 输出端口名称. Defaults to None.

        Returns:
            Any: 处理后的结果，类型取决于from_port参数
        """
        import numpy as np
        assert port=="images" or port=="pred" or port=="count",f"节点输出端口必须是images或pred或count，当前端口是{port}"
        if isinstance(result,list):
            if port=="count":
                return len(result)
            ret=[]
            for item in result:
                pred = item["pred"]
                # 处理numpy数组的特殊情况
                if isinstance(pred, np.ndarray):
                    if not pred.any():
                        continue
                elif not pred[0].any():
                    continue
                pred = pred[0]
                match port:
                    case "images":
                        image=item["input_img"]
                        ret.extend(sub_image_with_pred(image,pred))
                    case "pred":
                        ret.append(pred)
            if ret:
                return ret
            return None
        else:
            if not result or not isinstance(result,dict):
                return None
            pred = result["pred"]
            # 处理numpy数组的特殊情况
            if isinstance(pred, np.ndarray):
                if not pred.any():
                    return None
            elif not pred[0].any():
                return None
            pred = pred[0]
            match port:
                case "images":
                    image=result["input_img"]
                    return sub_image_with_pred(image,pred)
                case "pred":
                    return pred 
                case "count":
                    return 1
