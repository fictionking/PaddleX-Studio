from typing import Dict, Optional, Any
from .base_node import ComputeNode, NodeResult
import os
import cv2
import numpy as np

class LoadImageNode(ComputeNode):
    """加载图像节点

    用于读取图像文件并输出给后续处理节点
    """

    def _run_compute(self, port: str, data: Any) -> 'NodeResult':
        """
        运行加载图像节点，读取图像文件

        Args:
            port: 端口名称
            data: 输入数据

        Returns:
            NodeResult: 包含图像数据的结果对象
        """
        # 从params字典中读取图像访问路径
        image_path = self.params.get('path', None)

        # 确保图像路径有效
        if not image_path:
            raise ValueError(f"图像输入节点 {self.id} 未设置图像路径")

        images = []
        # 处理单张图像或多张图像列表
        if isinstance(image_path, str):
            if os.path.isdir(image_path):
                # 如果是目录，读取目录下所有图像
                for file_name in os.listdir(image_path):
                    file_path = os.path.join(image_path, file_name)
                    if self._is_image_file(file_path):
                        image = self._read_image(file_path)
                        images.append(image)
            elif self._is_image_file(image_path):
                # 如果是文件，直接读取
                image = self._read_image(image_path)
                images.append(image)
            else:
                raise ValueError(f"图像输入节点 {self.id} 路径无效: {image_path}")
        elif isinstance(image_path, list):
            # 如果是列表，读取每个路径的图像
            for path in image_path:
                if self._is_image_file(path):
                    image = self._read_image(path)
                    images.append(image)
        else:
            raise ValueError(f"图像输入节点 {self.id} 路径类型无效: {type(image_path)}")

        if not images:
            raise ValueError(f"图像输入节点 {self.id} 未找到有效图像")

        # 根据输出端口返回不同格式的结果
        result = {
            "images": images,
            "count": len(images)
        }

        return NodeResult(result, self)

    def process_output(self, result: Any, port: Optional[str] = None) -> Any:
        """
        处理输出结果

        Args:
            result (Any): 原始结果
            port (Optional[str], optional): 输出端口名称. Defaults to None.

        Returns:
            Any: 处理后的结果
        """
        if port == "images":
            return result["images"]
        elif port == "count":
            return result["count"]
        else:
            return result

    def _is_image_file(self, file_path: str) -> bool:
        """
        检查文件是否为图像文件

        Args:
            file_path (str): 文件路径

        Returns:
            bool: 是否为图像文件
        """
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
        return os.path.isfile(file_path) and os.path.splitext(file_path)[1].lower() in image_extensions

    def _read_image(self, file_path: str) -> np.ndarray:
        """
        读取图像文件，支持中文路径

        Args:
            file_path (str): 图像文件路径

        Returns:
            np.ndarray: 读取的图像数据

        Raises:
            RuntimeError: 当图像读取失败时抛出异常
        """
        try:
            # 使用numpy和cv2.imdecode读取图像，支持中文路径
            with open(file_path, 'rb') as f:
                img_data = f.read()
            # 将二进制数据转换为numpy数组
            img_array = np.frombuffer(img_data, np.uint8)
            # 解码图像
            image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            
            if image is None:
                raise RuntimeError(f"无法读取图像 {file_path}")
            
            # 转换为RGB格式
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            return image
        except Exception as e:
            raise RuntimeError(f"读取图像 {file_path} 失败: {str(e)}")