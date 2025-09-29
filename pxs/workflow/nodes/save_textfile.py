from typing import Any, Dict, Optional
from .base_node import ComputeNode, NodeResult
import os
import json
import yaml
import csv

# 尝试导入 pandas 和 numpy
try:
    import pandas as pd
    import numpy as np
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

class SaveTextfileNode(ComputeNode):
    """保存文本文件节点
    
    用于将输入数据写入文本文件
    """

    def __init__(self, config: Dict, pipeline: Any) -> None:
        """
        初始化保存文本文件节点

        Args:
            config (Dict): 节点配置
            pipeline (Any): 工作流管道实例
        """
        super().__init__(config, pipeline)
        # 初始化并存储配置参数
        self.output_path = self.params.get("path", "")
        if not self.output_path:
            raise ValueError("保存文本文件节点输出路径不能为空")

        self.format_type = self.params.get("format", "json")
        # 初始化计数器，用于确保多次调用时文件名不冲突
        self.counter = 0

        # 确保输出目录存在
        self._ensure_dir_exists(self.output_path)
         # 如果设置了清空目录，则在初始化时执行清空操作
        self.clear_dir = self.params.get("clear_dir", False)
        if self.clear_dir:
            self._clear_directory(self.output_path)

    def _convert_numpy_types(self, data):
        """
        递归地将 NumPy 数据类型转换为 Python 原生类型
        
        Args:
            data: 需要转换的数据
            
        Returns:
            转换后的数据
        """
        if isinstance(data, np.ndarray):
            # 将 NumPy 数组转换为 Python 列表
            return data.tolist()
        elif isinstance(data, np.generic):
            # 处理 NumPy 标量类型（如 np.float32, np.int64 等）
            return data.item()
        elif isinstance(data, list):
            # 递归处理列表中的每个元素
            return [self._convert_numpy_types(item) for item in data]
        elif isinstance(data, dict):
            # 递归处理字典中的每个值
            return {key: self._convert_numpy_types(value) for key, value in data.items()}
        else:
            # 对于其他类型，原样返回
            return data
            
    def _run_compute(self, port: str, data: Any) -> NodeResult:
        """
        运行节点，将输入数据写入文件

        Args:
            port (str): 输入端口名称
            data (Any): 输入数据

        Returns:
            NodeResult: 包含输出文件路径的结果对象
        """
        try:
            # 如果filename为空，则直接设置为节点ID
            filename = self.params.get("filename", "") or str(self.id)
            
            # 获取格式类型
            format_type = self.format_type.lower()
            
            # 生成文件名：使用filename加上计数器和确定的文件后缀
            file_name = f"{filename}_{self.counter}.{format_type}"
            file_path = os.path.join(self.output_path, file_name)

            match format_type:
                case "json":
                    with open(file_path, 'w', encoding='utf-8') as f:
                        # 转换 NumPy 类型为 Python 原生类型后再序列化
                        converted_data = self._convert_numpy_types(data)
                        json.dump(converted_data, f, ensure_ascii=False, indent=2)
                case "jsonl":
                    with open(file_path, 'w', encoding='utf-8') as f:
                        # 转换 NumPy 类型为 Python 原生类型后再序列化
                        converted_data = self._convert_numpy_types(data)
                        for item in converted_data:
                            json.dump(item, f, ensure_ascii=False)
                            f.write('\n')
                case "yaml":
                    with open(file_path, 'w', encoding='utf-8') as f:
                        # 转换 NumPy 类型为 Python 原生类型后再序列化
                        converted_data = self._convert_numpy_types(data)
                        yaml.dump(converted_data, f, allow_unicode=True)
                case "csv":
                    with open(file_path, 'w', encoding='utf-8', newline='') as f:
                        if isinstance(data, str):
                            # 直接写入字符串
                            f.write(data)
                        elif PANDAS_AVAILABLE and isinstance(data, pd.DataFrame):
                            # 处理 DataFrame
                            data.to_csv(f, index=False, encoding='utf-8')
                        elif PANDAS_AVAILABLE and isinstance(data, pd.Series):
                            # 处理 Series
                            data.to_csv(f, index=False, encoding='utf-8')
                        elif PANDAS_AVAILABLE and isinstance(data, np.ndarray):
                            # 处理 numpy 数组
                            pd.DataFrame(data).to_csv(f, index=False, encoding='utf-8')
                        elif isinstance(data, list):
                            if len(data) > 0 and isinstance(data[0], list):
                                # 处理二维列表
                                writer = csv.writer(f)
                                writer.writerows(data)
                            elif len(data) > 0 and isinstance(data[0], dict):
                                # 处理字典列表
                                fieldnames = data[0].keys()
                                writer = csv.DictWriter(f, fieldnames=fieldnames)
                                writer.writeheader()
                                writer.writerows(data)
                            else:
                                # 处理一维列表
                                writer = csv.writer(f)
                                for item in data:
                                    writer.writerow([item])
                        else:
                            # 其他类型转换为字符串
                            f.write(str(data))
                case "txt":
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(str(data))
                case _:
                    raise ValueError(f"TextfileOutputNode only supports 'json', 'yaml', 'csv' and 'txt' format type, got {format_type}")
            
            # 增加计数器，确保下次调用时文件名不冲突
            self.counter += 1
            
            return NodeResult(file_path, self)
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