from typing import Any, Dict,Optional
from .base_node import ComputeNode, NodeResult
import os
import json
from PIL import Image
import numpy as np

class SaveImageNode(ComputeNode):
    """保存图像节点

    用于将输入数据写入图像文件
    """

    def __init__(self, config: Dict, pipeline: Any) -> None:
        """
        初始化保存图像节点

        Args:
            config (Dict): 节点配置
            pipeline (Any): 工作流管道实例
        """
        super().__init__(config, pipeline)
        # 初始化并存储配置参数
        self.output_path = self.params.get("path", "output")
        self.format_type = self.params.get("format", "png")
        # 是否在初始化时清空目标文件夹
        self.clear_dir = self.params.get("clear_dir", False)
        
        # 确保输出目录存在
        self._ensure_dir_exists(self.output_path)
        
        # 如果设置了清空目录，则在初始化时执行清空操作
        if self.clear_dir:
            self._clear_directory(self.output_path)
        # 初始化计数器，用于确保多次调用时文件名不冲突
        self.counter = 0

    def _run_compute(self, port: str, data: Any) -> NodeResult:
        """
        运行节点，将输入数据写入图像文件

        Args:
            port (str): 输入端口名称
            data (Any): 输入数据

        Returns:
            NodeResult: 包含输出文件路径的结果对象
        """

        # 如果filename为空，则直接设置为节点ID
        filename = self.params.get("filename", "") or str(self.id)
                
        assert port=="images",f"图像文件输出节点输入端口必须是images，当前端口是{port}"
        
        try:
            files=[]
            if isinstance(data, list):
                for i, image_data in enumerate(data):
                    if isinstance(image_data, np.ndarray):
                        # 生成文件名：直接使用已初始化好的filename加上计数器和索引
                        file_name = f"{filename}_{self.counter}_{i}.{self.format_type}"
                        file_path = os.path.join(self.output_path, file_name)
                        
                        image = Image.fromarray(image_data)
                        image.save(file_path)
                        files.append(file_path)
            else:
                if isinstance(data, np.ndarray):
                    # 生成文件名：直接使用已初始化好的filename加上计数器
                    file_name = f"{filename}_{self.counter}.{self.format_type}"
                    file_path = os.path.join(self.output_path, file_name)
                    
                    image = Image.fromarray(data)
                    image.save(file_path)
                    files.append(file_path)
                else:
                    raise ValueError(f"图像文件输出节点 {self.id} 输入数据类型无效: {type(data)}")  
            
            # 增加计数器，确保下次调用时文件名不冲突
            self.counter += 1
            
            # 返回文件路径
            return NodeResult(files, self)
        except Exception as e:
            raise RuntimeError(f"节点 {self.id} 写入文件失败: {str(e)}")

    def process_output(self, result: Any, port: Optional[str] = None) -> Any:
        """
        处理输出结果

        Args:
            result (Any): 原始结果
            port (Optional[str], optional): 输出端口名称. Defaults to None.

        Returns:
            Any: 处理后的结果
        """
        # result是输出文件路径
        return result
        
    def _clear_directory(self, directory_path: str) -> None:
        """
        清空指定目录下的所有文件

        Args:
            directory_path (str): 要清空的目录路径
        """
        if not os.path.exists(directory_path):
            return
        
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                # 记录错误但继续处理其他文件
                print(f"警告: 无法删除文件 {file_path}: {str(e)}")