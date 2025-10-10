from typing import Any, Dict, Optional, List
import numpy as np
import os
import json
from .base_node import ComputeNode, NodeResult

class FeatureMatchNode(ComputeNode):
    """特征匹配节点

    用于计算输入特征向量与特征库之间的相似度，支持多种相似度度量方法
    主要支持直接接收特征列表格式的输入: [{"index": 0, "feature": [...]}, ...]
    """

    def __init__(self, config: Dict, pipeline: Any) -> None:
        """
        初始化特征匹配节点

        Args:
            config (Dict): 节点配置
            pipeline (Any): 工作流管道实例
        """
        super().__init__(config, pipeline)
        # 设置默认参数
        self.params.setdefault("metric", "cosine")  # 相似度度量方法，默认为余弦相似度
        self.params.setdefault("threshold", 0.5)    # 匹配阈值，默认为0.5
        
        # 初始化特征向量库
        self.feature_library = {}
        if "path" in self.params:
            self._load_feature_library(self.params["path"])

    def _run_compute(self, port: str, data: Any) -> 'NodeResult':
        """
        运行特征匹配计算

        Args:
            port (str): 输入端口名称
            data (Any): 输入数据，可以是特征列表格式，或只包含一个特征向量的字典

        Returns:
            NodeResult: 节点运行结果封装对象
        """
        # 准备输入数据
        input_data = self.prepare_input(port, data)
        
        # 确定匹配模式
        if "feature" in input_data and self.feature_library:
            # 单个特征与特征库匹配模式
            result = self._match_with_library(input_data["feature"])
        elif "features" in input_data and self.feature_library:
            # 特征列表与特征库匹配模式
            result = []
            for feature_item in input_data["features"]:
                # 对每个输入特征与完整特征库进行匹配
                match_result = self._match_with_library(feature_item["feature"])
                
                # 构建输出格式: {index: 0, matchs: {}}
                # 每个特征都包含其原始索引和对应的完整匹配结果
                result.append({
                    "index": feature_item["index"],
                    "matchs": match_result
                })
        else:
            if not self.feature_library:
                raise ValueError("特征库为空，无法进行特征匹配")
            raise ValueError("输入数据格式不正确，需要包含'feature'（用于与特征库匹配），或'features'列表")
        
        return NodeResult(result, self)
    
    def _match_with_library(self, feature: np.ndarray) -> Dict:
        """
        与特征库中的所有特征进行匹配

        Args:
            feature (np.ndarray): 要匹配的特征向量

        Returns:
            Dict: 匹配结果，包含最佳匹配和所有匹配信息
        """
        if not self.feature_library:
            raise ValueError("特征库为空，无法进行匹配")
        
        # 存储满足匹配阈值的结果
        all_matches = []
        best_match_id = None
        best_similarity = -float('inf')
        
        # 与特征库中的每个特征进行匹配
        for feature_id, library_feature in self.feature_library.items():
            similarity = self._calculate_similarity(
                feature, 
                library_feature,
                self.params["metric"]
            )
            
            # 检查是否匹配
            is_matched = similarity >= self.params["threshold"]
            
            # 更新最佳匹配
            if similarity > best_similarity:
                best_similarity = similarity
                best_match_id = feature_id
                best_is_matched = is_matched
            
            # 只记录满足匹配阈值的结果
            if is_matched:
                all_matches.append({
                    "feature_id": feature_id,
                    "similarity": similarity,
                    "is_matched": is_matched
                })
        
        # 构建结果
        result = {
            "best_match": {
                "feature_id": best_match_id,
                "similarity": best_similarity,
                "is_matched": best_is_matched
            },
            "all_matches": all_matches,
            "matched_count": len(all_matches),
            "total_count": len(self.feature_library),
            "threshold": self.params["threshold"],
            "metric": self.params["metric"]
        }
        
        return result

    def prepare_input(self, port: str, data: Any) -> Any:
        """
        准备特征匹配输入数据

        Args:
            port (str): 输入端口名称
            data (Any): 输入数据，支持特征列表格式

        Returns:
            Any: 处理后的输入数据
        """
        # 初始化处理后的数据
        processed_data = {}
        
        # 检查是否是单个特征与特征库匹配的情况
        if isinstance(data, dict) and "feature" in data:
            # 处理特征向量
            processed_data = {
                "feature": self._process_feature(data["feature"])
            }
        # 检查是否是特征列表格式（直接传入列表）
        elif isinstance(data, list):
            # 处理特征列表
            processed_features = []
            for feature_item in data:
                if isinstance(feature_item, dict) and "index" in feature_item and "feature" in feature_item:
                    processed_features.append({
                        "index": feature_item["index"],
                        "feature": self._process_feature(feature_item["feature"])
                    })
                else:
                    raise ValueError("特征列表中的元素格式不正确，需要包含'index'和'feature'")
            
            processed_data = {
                "features": processed_features
            }
        else:
            # 数据格式不正确
            raise ValueError("输入数据格式不正确，需要是特征列表格式，或包含'feature'（用于与特征库匹配）的字典")
        
        return processed_data

    def _process_feature(self, feature: Any) -> np.ndarray:
        """
        处理特征向量，确保其为numpy数组

        Args:
            feature (Any): 特征向量，可以是列表或numpy数组

        Returns:
            np.ndarray: 处理后的特征向量
        """
        # 转换为numpy数组
        if isinstance(feature, list):
            feature = np.array(feature)
        elif not isinstance(feature, np.ndarray):
            raise TypeError(f"不支持的特征类型: {type(feature)}")
        
        # 确保特征是一维向量
        if len(feature.shape) > 1:
            feature = feature.flatten()
        
        return feature

    def _calculate_similarity(self, feature1: np.ndarray, feature2: np.ndarray, metric: str) -> float:
        """
        计算两个特征向量之间的相似度

        Args:
            feature1 (np.ndarray): 第一个特征向量
            feature2 (np.ndarray): 第二个特征向量
            metric (str): 相似度度量方法

        Returns:
            float: 相似度分数
        """
        if metric == "cosine":
            # 余弦相似度
            return self._cosine_similarity(feature1, feature2)
        elif metric == "euclidean":
            # 欧氏距离（转换为相似度）
            distance = np.linalg.norm(feature1 - feature2)
            # 转换为相似度：1/(1+distance)
            return 1.0 / (1.0 + distance)
        elif metric == "manhattan":
            # 曼哈顿距离（转换为相似度）
            distance = np.sum(np.abs(feature1 - feature2))
            # 转换为相似度：1/(1+distance)
            return 1.0 / (1.0 + distance)
        else:
            raise ValueError(f"不支持的相似度度量方法: {metric}")

    def _cosine_similarity(self, feature1: np.ndarray, feature2: np.ndarray) -> float:
        """
        计算两个特征向量之间的余弦相似度

        Args:
            feature1 (np.ndarray): 第一个特征向量
            feature2 (np.ndarray): 第二个特征向量

        Returns:
            float: 余弦相似度分数，范围[-1, 1]
        """
        # 计算点积
        dot_product = np.dot(feature1, feature2)
        
        # 计算模长
        norm1 = np.linalg.norm(feature1)
        norm2 = np.linalg.norm(feature2)
        
        # 避免除零错误
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        # 计算余弦相似度
        return dot_product / (norm1 * norm2)

    def _load_feature_library(self, path: str) -> None:
        """
        加载特征向量库

        Args:
            path (str): 特征文件或目录的路径
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"特征库路径不存在: {path}")
        
        if os.path.isfile(path):
            # 处理单个文件
            self._load_feature_file(path)
        elif os.path.isdir(path):
            # 处理目录下的所有文件
            for filename in os.listdir(path):
                file_path = os.path.join(path, filename)
                if os.path.isfile(file_path) and filename.endswith('.json'):
                    self._load_feature_file(file_path)
        
        print(f"特征向量库加载完成，共加载 {len(self.feature_library)} 个特征")
    
    def _load_feature_file(self, file_path: str) -> None:
        """
        加载单个特征文件

        Args:
            file_path (str): 特征文件的路径
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                features_data = json.load(f)
            
            # 获取文件名（不包含扩展名）
            file_name = os.path.splitext(os.path.basename(file_path))[0]
            
            # 处理特征数据
            if isinstance(features_data, list):
                for feature_item in features_data:
                    if isinstance(feature_item, dict) and 'index' in feature_item and 'feature' in feature_item:
                        # 创建特征ID：文件名+index
                        feature_id = f"{file_name}_{feature_item['index']}"
                        # 处理特征向量
                        feature_vector = np.array(feature_item['feature'])
                        # 添加到特征库
                        self.feature_library[feature_id] = feature_vector
            elif isinstance(features_data, dict) and 'feature' in features_data:
                # 单个特征的情况
                feature_id = f"{file_name}_0"
                feature_vector = np.array(features_data['feature'])
                self.feature_library[feature_id] = feature_vector
        except Exception as e:
            print(f"加载特征文件 {file_path} 失败: {str(e)}")
            # 继续加载其他文件，不中断整个过程

    def process_output(self, result: Any, port: Optional[str] = None) -> Any:
        """
        处理输出结果

        Args:
            result (Any): 原始结果
            port (Optional[str], optional): 输出端口名称. Defaults to None.

        Returns:
            Any: 处理后的结果
        """
        # 基础实现：直接返回原始结果
        # 可以根据不同的port实现特定的处理逻辑
        return result