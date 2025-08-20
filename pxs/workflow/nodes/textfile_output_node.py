from typing import Any, Optional
from .base_node import ComputeNode, NodeResult
import os
import json
import yaml
import csv

try:
    import pandas as pd
    import numpy as np
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

class TextfileOutputNode(ComputeNode):
    """文本文件输出节点

    用于将输入数据写入文本文件
    """

    def _run_compute(self,port:str,data:Any) -> NodeResult:
        """
        运行节点，将输入数据写入文件

        Args:
            input_data (Any): 输入数据

        Returns:
            NodeResult: 包含输出文件路径的结果对象
        """
        # 写入文件
        output_path = self.params.get("path", "output/result.json")
        format_type = self.params.get("format", "json")

        try:
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            self._ensure_dir_exists(output_dir)

            match format_type.lower():
                case "json":
                    with open(output_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                case "json_lines":
                    with open(output_path, 'w', encoding='utf-8') as f:
                        for item in data:
                            json.dump(item, f, ensure_ascii=False)
                            f.write('\n')
                case "yaml":
                    with open(output_path, 'w', encoding='utf-8') as f:
                        yaml.dump(data, f, allow_unicode=True)
                case "csv":
                    with open(output_path, 'w', encoding='utf-8', newline='') as f:
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
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(str(data))
                case _:
                    raise ValueError(f"TextfileOutputNode only supports 'json', 'yaml', 'csv' and 'txt' format type, got {format_type}")
            return NodeResult(output_path, self)
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