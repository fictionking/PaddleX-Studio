# 后端节点组件 API 参考

本文档提供 PaddleX Studio 工作流后端节点组件的详细 API 参考，帮助开发者更深入地理解和使用后端节点组件。

## 基础节点类 (BaseNode)

`BaseNode` 是所有工作流后端节点的抽象基类，定义了节点的基本接口和公共功能。

### 初始化方法

```python
def __init__(self, config: Dict, pipeline: Any) -> None:
    """
    初始化节点

    Args:
        config (Dict): 节点配置，包含 id、name、type 和 params 等
        pipeline (Any): 工作流管道实例，用于节点间通信
    """
    self.id = config["id"]
    self.name = config["name"]
    self.type = config["type"]
    self.params = config.get("params", {})
```

### 核心方法

#### set_params

```python
def set_params(self, port: str, data: Any) -> None:
    """
    设置节点参数

    Args:
        port (str): 参数端口路径，支持嵌套参数，如 "param.sub_param"
        data (Any): 参数数据
    """
    # 处理嵌套参数路径
    params_path = port.split(".")
    current = self.params
    for i, param in enumerate(params_path):
        if i == len(params_path) - 1:
            current[param] = data
        else:
            if param not in current:
                current[param] = {}
            current = current[param]
```

#### run (抽象方法)

```python
@abstractmethod
def run(self, port: str, data: Any) -> 'NodeResult':
    """
    运行节点的抽象方法，子类必须实现

    Args:
        port (str): 输入端口名称
        data (Any): 输入数据

    Returns:
        NodeResult: 节点运行结果封装对象
    """
    pass
```

#### process_output

```python
def process_output(self, result: Any, port: Optional[str] = None) -> Any:
    """
    处理输出结果

    Args:
        result (Any): 原始结果
        port (Optional[str], optional): 输出端口名称. Defaults to None.

    Returns:
        Any: 处理后的结果
    """
    # 基类实现简单返回原始结果
    return result
```

#### _ensure_dir_exists

```python
def _ensure_dir_exists(self, dir_path: str) -> None:
    """
    确保文件所在目录存在

    Args:
        dir_path (str): 目录路径
    """
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)
```

## 常量节点类 (ConstantNode)

`ConstantNode` 是常量节点的抽象基类，用于处理静态输入。常量节点在工作流启动时一次性处理并输出结果，在所有动态节点之前运行。

### 初始化方法

```python
def __init__(self, config: Dict, pipeline: Any) -> None:
    """
    初始化常量节点

    Args:
        config (Dict): 节点配置
        pipeline (Any): 工作流管道实例
    """
    super().__init__(config, pipeline)
    # 标记常量节点是否已运行
    self.has_run = False
    # 缓存常量节点的运行结果
    self.result_cache = None
```

### 核心方法

#### run

```python
def run(self, port: str = None, data: Any = None) -> 'NodeResult':
    """
    运行常量节点

    特点：只运行一次，结果会被缓存

    Args:
        port (str, optional): 输入端口名称. Defaults to None.
        data (Any, optional): 输入数据. Defaults to None.

    Returns:
        NodeResult: 节点运行结果封装对象
    """
    if not self.has_run:
        # 直接使用输入数据
        result = self._run_constant()
        # 缓存结果
        self.result_cache = result
        self.has_run = True
    return self.result_cache
```

#### set_value (抽象方法)

```python
@abstractmethod
def set_value(self, value: Any) -> None:
    """
    设置节点常量值

    Args:
        value (Any): 常量值

    Returns:
        None
    """
    pass
```

#### _run_constant (抽象方法)

```python
@abstractmethod
def _run_constant(self) -> 'NodeResult':
    """
    常量节点的具体运行逻辑

    Returns:
        NodeResult: 节点运行结果封装对象
    """
    pass
```

## 计算节点类 (ComputeNode)

`ComputeNode` 是计算节点的抽象基类，用于处理动态计算逻辑。计算节点根据输入变化实时计算输出，只有当输入端口有数据时才运行。

### 初始化方法

```python
def __init__(self, config: Dict, pipeline: Any) -> None:
    """
    初始化运算节点

    Args:
        config (Dict): 节点配置
        pipeline (Any): 工作流管道实例
    """
    super().__init__(config, pipeline)
```

### 核心方法

#### run

```python
def run(self, port: str, data: Any) -> 'NodeResult':
    """
    运行运算节点

    特点：只有当输入有数据时才运行

    Args:
        port (str): 输入端口名称
        data (Any): 输入数据

    Returns:
        NodeResult: 节点运行结果封装对象
    """
    # 直接使用输入数据
    return self._run_compute(port, data)
```

#### _run_compute (抽象方法)

```python
@abstractmethod
def _run_compute(self, port: str, data: Any) -> 'NodeResult':
    """
    运算节点的具体运行逻辑

    Args:
        port (str): 输入端口名称
        data (Any): 输入数据

    Returns:
        NodeResult: 节点运行结果封装对象
    """
    pass
```

## 流式节点类 (StreamNode)

`StreamNode` 是流式节点的抽象基类，用于处理流式数据。流式节点能够在运行过程中逐步输出多条数据，每条数据都能立即传递到下游节点进行处理。

### 初始化方法

```python
def __init__(self, config: Dict, pipeline: Any) -> None:
    """
    初始化流式节点

    Args:
        config (Dict): 节点配置
        pipeline (Any): 工作流管道实例
    """
    super().__init__(config, pipeline)
```

### 核心方法

#### run

```python
def run(self, port: str, data: Any) -> 'NodeResult':
    """
    运行流式节点（非流式调用方式）

    注意：在标准工作流执行中，此方法通常不会被直接调用，而是由WorkflowPipeline
    创建单独的线程并调用_stream_output方法来处理流式输出。
    这个方法主要用于非流式场景下获取完整结果，或作为流式处理的回退机制。

    Args:
        port (str): 输入端口名称
        data (Any): 输入数据

    Returns:
        NodeResult: 完整运行结果
    """
    pass
```

#### _stream_output (抽象方法)

```python
@abstractmethod
def _stream_output(self, port: str, data: Any):
    """
    流式输出的核心逻辑，每次yield一条数据
    
    在WorkflowPipeline中，这个方法会在单独的线程中被调用，产生的每条结果
    会通过队列传递回主线程，并立即发送到下游节点进行处理。

    Args:
        port (str): 输入端口名称
        data (Any): 输入数据
        
    Yields:
        NodeResult: 每条流式输出的结果
    """
    pass
```

## 节点结果类 (NodeResult)

`NodeResult` 类用于封装节点运行结果，并支持根据输出端口参数动态返回不同类型的值。

### 初始化方法

```python
def __init__(self, raw_result: Any, node: 'BaseNode') -> None:
    """
    初始化节点结果

    Args:
        raw_result (Any): 原始运行结果
        node (BaseNode): 节点实例
    """
    self.value = raw_result
    self.node = node
    self.processed_results: Dict[str, Any] = {}
```

### 核心方法

#### get

```python
def get(self, port: str) -> Any:
    """
    根据port参数获取对应类型的结果

    Args:
        port (str): 输出端口名称.

    Returns:
        Any: 对应端口的结果
    """
    port_type, port_name = parse_port(port)
    if port_type != "outputs":
        raise ValueError(f"get only supports 'outputs' port type, got {port}")
    return self.__getattr__(port_name)
```

#### __getattr__

```python
def __getattr__(self, name: str) -> Any:
    """
    支持通过属性访问结果

    Args:
        name (str): 属性名

    Returns:
        Any: 对应属性的结果
    """
    if name in self.processed_results:
        return self.processed_results[name]

    # 调用节点的process_output方法处理结果
    result = self.node.process_output(self.value, name)

    self.processed_results[name] = result
    return result
```

## 常用工具函数

### parse_port

`parse_port` 函数用于解析端口字符串，提取端口类型和端口名称。

```python
from pxs.workflow.common.utils import parse_port

# 使用示例
port_type, port_name = parse_port("outputs.image")
# port_type = "outputs", port_name = "image"
```

### 节点注册机制

后端节点通过类的定义和导入机制进行注册。在 `pxs/workflow/nodes/` 目录下创建节点文件后，系统会自动发现并注册这些节点。

## 节点开发示例

### 1. 计算节点开发示例

下面是一个简单的计算节点开发示例，实现一个图像缩放功能：

```python
from typing import Dict, Optional, Any
from .base_node import ComputeNode, NodeResult
import cv2
import numpy as np

class ImageResizeNode(ComputeNode):
    """图像缩放节点

    用于调整输入图像的大小
    """

    def _run_compute(self, port: str, data: Any) -> 'NodeResult':
        """
        运行图像缩放节点，调整图像大小

        Args:
            port: 输入端口名称
            data: 输入数据（图像或图像列表）

        Returns:
            NodeResult: 包含缩放后图像的结果对象
        """
        # 从参数中获取缩放参数
        width = self.params.get('width', 640)
        height = self.params.get('height', 480)
        interpolation = self.params.get('interpolation', 'bilinear')
        
        # 确定插值方法
        interp_methods = {
            'nearest': cv2.INTER_NEAREST,
            'bilinear': cv2.INTER_LINEAR,
            'bicubic': cv2.INTER_CUBIC,
            'lanczos': cv2.INTER_LANCZOS4
        }
        interp_method = interp_methods.get(interpolation.lower(), cv2.INTER_LINEAR)
        
        # 处理单张图像或多张图像
        if isinstance(data, np.ndarray):
            # 单张图像
            resized_image = cv2.resize(data, (width, height), interpolation=interp_method)
            result = {
                "image": resized_image,
                "count": 1
            }
        elif isinstance(data, list) and all(isinstance(img, np.ndarray) for img in data):
            # 图像列表
            resized_images = []
            for img in data:
                resized = cv2.resize(img, (width, height), interpolation=interp_method)
                resized_images.append(resized)
            result = {
                "images": resized_images,
                "count": len(resized_images)
            }
        else:
            raise ValueError(f"输入数据类型不支持: {type(data)}")

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
        if port == "image" and "image" in result:
            return result["image"]
        elif port == "images" and "images" in result:
            return result["images"]
        elif port == "count":
            return result["count"]
        else:
            return result
```

### 2. 流式节点开发示例

下面是一个流式节点开发示例，实现一个图像批量处理功能：

```python
from typing import Dict, Optional, Any, Generator
from .base_node import StreamNode, NodeResult
import cv2
import numpy as np
import time

class BatchImageProcessorNode(StreamNode):
    """批量图像处理器节点

    以流式方式处理图像批次
    """

    def __init__(self, config: Dict, pipeline: Any) -> None:
        """
        初始化批量图像处理器节点

        Args:
            config (Dict): 节点配置
            pipeline (Any): 工作流管道实例
        """
        super().__init__(config, pipeline)
        # 从配置中获取批次大小
        self.batch_size = self.params.get('batch_size', 8)

    def run(self, port: str, data: Any) -> 'NodeResult':
        """
        非流式调用方式，收集所有结果后返回

        Args:
            port (str): 输入端口名称
            data (Any): 输入数据

        Returns:
            NodeResult: 包含所有处理结果的对象
        """
        all_results = []
        # 收集所有流式结果
        for result in self._stream_output(port, data):
            all_results.append(result.value)
        
        # 返回完整结果
        return NodeResult({
            "all_results": all_results,
            "batch_count": len(all_results)
        }, self)

    def _stream_output(self, port: str, data: Any) -> Generator['NodeResult', None, None]:
        """
        流式输出的核心逻辑，批量处理图像并逐批返回结果

        Args:
            port (str): 输入端口名称
            data (Any): 输入数据（图像列表）

        Yields:
            NodeResult: 每批处理结果
        """
        if not isinstance(data, list):
            raise ValueError(f"输入数据必须是图像列表: {type(data)}")
        
        # 批量处理图像
        for i in range(0, len(data), self.batch_size):
            batch = data[i:i + self.batch_size]
            # 处理当前批次
            processed_batch = self._process_batch(batch)
            
            # 返回当前批次结果
            yield NodeResult({
                "batch": processed_batch,
                "batch_index": i // self.batch_size,
                "batch_size": len(batch)
            }, self)
            
            # 模拟处理延迟
            time.sleep(0.1)

    def _process_batch(self, batch: list) -> list:
        """
        处理单个批次的图像

        Args:
            batch (list): 图像批次

        Returns:
            list: 处理后的图像批次
        """
        processed_batch = []
        
        for image in batch:
            # 这里实现具体的图像处理逻辑
            # 例如转换为灰度图
            if len(image.shape) == 3 and image.shape[2] == 3:
                processed = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
                # 扩展维度以保持一致性
                processed = np.expand_dims(processed, axis=-1)
            else:
                processed = image
            
            processed_batch.append(processed)
        
        return processed_batch

    def process_output(self, result: Any, port: Optional[str] = None) -> Any:
        """
        处理输出结果

        Args:
            result (Any): 原始结果
            port (Optional[str], optional): 输出端口名称. Defaults to None.

        Returns:
            Any: 处理后的结果
        """
        if port == "batch" and "batch" in result:
            return result["batch"]
        elif port == "batch_index":
            return result["batch_index"]
        elif port == "batch_size":
            return result["batch_size"]
        elif port == "all_results" and "all_results" in result:
            return result["all_results"]
        elif port == "batch_count" and "batch_count" in result:
            return result["batch_count"]
        else:
            return result
```

## 节点异常处理

在开发节点时，良好的异常处理机制可以提高系统的稳定性和用户体验。以下是一些异常处理的最佳实践：

### 1. 参数验证

```python
def _run_compute(self, port: str, data: Any) -> 'NodeResult':
    # 参数验证
    if not self.params.get('required_param'):
        raise ValueError(f"节点 {self.id} 缺少必需参数 'required_param'")
    
    # 类型检查
    if 'numeric_param' in self.params and not isinstance(self.params['numeric_param'], (int, float)):
        raise TypeError(f"参数 'numeric_param' 必须是数字类型，当前类型: {type(self.params['numeric_param'])}")
    
    # 范围检查
    if 'bounded_param' in self.params and not (0 <= self.params['bounded_param'] <= 1):
        raise ValueError(f"参数 'bounded_param' 必须在 0 到 1 之间，当前值: {self.params['bounded_param']}")
    
    # 正常处理逻辑...
```

### 2. 输入数据验证

```python
def _run_compute(self, port: str, data: Any) -> 'NodeResult':
    # 输入数据验证
    if data is None:
        raise ValueError(f"节点 {self.id} 接收到空输入")
    
    # 检查数据类型
    if not isinstance(data, (np.ndarray, list)):
        raise TypeError(f"节点 {self.id} 不支持的数据类型: {type(data)}")
    
    # 对于图像数据，可以检查形状和通道数
    if isinstance(data, np.ndarray) and len(data.shape) not in [2, 3]:
        raise ValueError(f"节点 {self.id} 接收到无效的图像形状: {data.shape}")
    
    # 正常处理逻辑...
```

### 3. 资源释放

```python
def _run_compute(self, port: str, data: Any) -> 'NodeResult':
    resource = None
    try:
        # 获取资源
        resource = self._acquire_resource()
        # 使用资源进行处理
        result = self._process_with_resource(data, resource)
        return NodeResult(result, self)
    except Exception as e:
        # 记录异常
        print(f"节点 {self.id} 处理异常: {str(e)}")
        raise
    finally:
        # 确保资源被释放
        if resource is not None:
            self._release_resource(resource)
```

## 性能优化技巧

### 1. 使用 NumPy 向量化操作

对于图像处理和数值计算任务，尽量使用 NumPy 的向量化操作，避免使用 Python 循环：

```python
# 避免这样做
def slow_process(image):
    result = np.zeros_like(image)
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            result[i, j] = image[i, j] * 2
    return result

# 推荐这样做
def fast_process(image):
    # 向量化操作，性能更优
    return image * 2
```

### 2. 缓存中间结果

对于重复计算的场景，可以缓存中间结果：

```python
def __init__(self, config: Dict, pipeline: Any) -> None:
    super().__init__(config, pipeline)
    # 创建缓存字典
    self.cache = {}
    
def _run_compute(self, port: str, data: Any) -> 'NodeResult':
    # 生成缓存键
    cache_key = self._generate_cache_key(port, data)
    
    # 检查缓存
    if cache_key in self.cache:
        return self.cache[cache_key]
    
    # 计算结果
    result = self._compute_result(port, data)
    
    # 缓存结果
    self.cache[cache_key] = result
    
    return result
```

### 3. 批处理操作

对于独立的处理任务，可以实现批处理功能以提高效率：

```python
def _process_batch(self, images):
    # 一次性处理多张图像
    results = []
    for image in images:
        # 处理单张图像
        result = self._process_single_image(image)
        results.append(result)
    return results
```

## 常见问题解决

### 1. 内存使用过高

如果节点处理大量数据时内存使用过高，可以尝试：

- 使用流式处理（StreamNode）逐步处理数据
- 分批加载和处理数据
- 及时释放不再需要的中间数据
- 使用更高效的数据格式

### 2. 处理速度慢

如果节点处理速度较慢，可以尝试：
- 优化算法复杂度
- 使用向量化操作代替循环
- 考虑使用并行处理
- 对于图像处理任务，尝试使用 GPU 加速

### 3. 节点间数据传递问题

如果在节点间传递数据时遇到问题，可以检查：
- 确保数据格式一致
- 检查数据类型和形状是否符合预期
- 确保数据大小在系统限制范围内
- 对于大文件，考虑使用文件路径引用而非直接传递数据

---

通过本文档，您应该能够更好地理解和使用 PaddleX Studio 工作流的后端节点组件 API。如果您有任何问题或需要进一步的帮助，请参考 Python 官方文档或联系我们的开发团队。