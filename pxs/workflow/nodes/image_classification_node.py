from typing import Any, Dict, Optional
from typing import Any, Dict, Optional
from .model_node import BaseModelNode
import cv2
import numpy as np

class ImageClassificationNode(BaseModelNode):
    """图像分类节点"""

    def __init__(self, config: Dict, pipeline: Any) -> None:
        """
        初始化图像分类节点

        Args:
            config (Dict): 节点配置
            pipeline (Any): 工作流管道实例
        """
        super().__init__(config, pipeline)
        # 加载类别映射（如果有）
        self.category_map = self.params.get("category_map", {})

    def prepare_input(self) -> Any:
        """
        准备图像分类模型输入数据

        Returns:
            Any: 处理后的输入数据
        """
        # 获取原始输入数据
        input_data = super().prepare_input()

        # 图像分类模型需要图像数据
        if isinstance(input_data, str):
            # 如果输入是文件路径，读取图像
            image = cv2.imread(input_data)
            if image is None:
                raise ValueError(f"无法读取图像文件: {input_data}")
            # 转换为RGB格式
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            return image
        elif isinstance(input_data, np.ndarray):
            # 如果输入是numpy数组，检查通道顺序
            if input_data.shape[-1] == 3:
                # 假设是BGR格式，转换为RGB
                image = cv2.cvtColor(input_data, cv2.COLOR_BGR2RGB)
                return image
            elif input_data.shape[-1] == 1:
                # 单通道图像，转换为RGB
                image = cv2.cvtColor(input_data, cv2.COLOR_GRAY2RGB)
                return image
            return input_data
        else:
            raise TypeError(f"不支持的输入类型: {type(input_data)}")

    def process_output(self, result: Any, port: Optional[str] = None) -> Any:
        """
        处理图像分类模型输出结果

        Args:
            result (Any): 模型原始输出
            from_port (Optional[str], optional): 输出端口名称. Defaults to None.

        Returns:
            Any: 处理后的结果，类型取决于from_port参数
        """
        # 图像分类结果通常包含类别和置信度
        processed_result = {
            "predictions": [],
            "top_prediction": None
        }

        class_ids = []
        class_names = []
        scores = []

        if "class_ids" in result and "scores" in result:
            for class_id, score in zip(result["class_ids"], result["scores"]):
                # 获取类别名称（如果有映射）
                class_name = self.category_map.get(str(class_id), f"class_{class_id}")
                processed_result["predictions"].append({
                    "class_id": int(class_id),
                    "class_name": class_name,
                    "score": float(score)
                })
                class_ids.append(int(class_id))
                class_names.append(class_name)
                scores.append(float(score))

            # 找到置信度最高的预测
            if processed_result["predictions"]:
                processed_result["top_prediction"] = max(
                    processed_result["predictions"],
                    key=lambda x: x["score"]
                )

        # 根据from_port返回不同类型的结果
        if port == "class_ids":
            return class_ids
        elif port == "class_names":
            return class_names
        elif port == "scores":
            return scores
        elif port == "predictions":
            return processed_result["predictions"]
        elif port == "top_prediction":
            return processed_result["top_prediction"]
        else:
            # 默认返回完整结果
            return processed_result