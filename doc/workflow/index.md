# PaddleX Studio 工作流节点插件开发文档

本文档介绍如何在 PaddleX Studio 中开发自定义的工作流节点插件，包括前端节点组件和后端节点组件的开发指南。

## 目录结构

PaddleX Studio 的工作流节点分为前端组件和后端处理逻辑两部分，分别位于以下目录：

- **前端节点组件**：`/templates/components/nodes/`
- **后端节点组件**：`/pxs/workflow/nodes/`

## 前端节点组件开发

### 1. 前端节点组件基础结构

前端节点组件是基于 Vue 开发的，所有节点组件都应该继承自基础的 `WorkflowNode` 组件。

#### 基础节点组件模板

下面是一个基本的前端节点组件模板：

```vue
<template>
    <WorkflowNode v-bind="$props">
        <template #properties>
            <!-- 在这里定义节点的属性组件 -->
            <InputProperty label="参数名称" v-model="data.params.param_name" />
            <!-- 可以添加更多的属性组件 -->
        </template>
    </WorkflowNode>
</template>

<script>
import { WorkflowNode, InputProperty } from './base/WorkflowNode.mjs';

/**
 * 节点组件描述
 */
export default {
    components: {
        WorkflowNode,
        InputProperty
    },
    props: {
        id: {
            type: String,
            required: true,
        },
        type: {
            type: String,
            required: true,
        },
        data: {
            type: Object,
            required: true,
        }
    },
    data() {
        return {
            // 组件内部状态
        }
    },
    methods: {
        // 自定义方法
    }
};
</script>
```

### 2. 属性组件类型

PaddleX Studio 提供了多种内置的属性组件，可以用于构建节点的参数界面：

| 组件名称 | 组件类名 | 用途 |
|---------|---------|------|
| 输入框 | InputProperty | 文本输入 |
| 数字输入 | InputNumberProperty | 数字输入 |
| 选择器 | SelectProperty | 下拉选择 |
| 文本显示 | TextProperty | 只读文本显示 |
| 值显示 | ValueProperty | 只读值显示 |
| 布尔选择 | BoolProperty | 布尔值选择（开关） |
| 带按钮的输入框 | InputWithButtonProperty | 带按钮的输入框 |
| 属性组 | GroupProperty | 一组相关属性的分组 |
| 属性列表 | PropertyList | 动态属性列表 |

### 3. 节点类型注册

开发完成的前端节点组件需要在 `nodes.mjs` 文件中注册，以便在工作流编辑器中显示和使用：

```javascript
export const nodeTypes = {
    // 已有的节点类型...
    your_node_type: markRaw(defineAsyncComponent(() => import(`/components/nodes/your_node_file.vue`))),
};

// 同时在 menuItems 中添加菜单项
```

### 4. 示例：load_image 节点组件

以下是 `load_image` 节点组件的示例代码：

```vue
<template>
    <WorkflowNode v-bind="$props">
        <template #properties>
            <InputWithButtonProperty label="目录或文件" v-model="data.params.path" 
                buttonIcon="Files" @buttonClick="handleClick" />
            <el-dialog v-model="dialogShow" title="选择数据集中的目录或文件" width="500" append-to-body>
                <div class="file-tree">
                    <el-tree accordion highlight-current :expand-on-click-node="false" :props="props" :load="loadNode"
                        lazy @node-click="handleNodeClick" />
                </div>
            </el-dialog>
        </template>
    </WorkflowNode>
</template>

<script>
import { WorkflowNode, InputWithButtonProperty } from './base/WorkflowNode.mjs';

/**
 * 图像文件输出节点组件
 * 用于配置和展示图像输出相关参数
 */
export default {
    components: {
        WorkflowNode,
        InputWithButtonProperty
    },
    props: {
        id: { type: String, required: true },
        type: { type: String, required: true },
        data: { type: Object, required: true }
    },
    data() {
        return {
            dialogShow: false,
            props: { children: 'children', label: 'name', isLeaf: 'leaf' }
        }
    },
    methods: {
        // 加载数据集和文件的方法
        async loadDatasets() { /* ... */ },
        async loadPath(datasetId) { /* ... */ },
        recursivelyUpdatePaths(data, datasetId) { /* ... */ },
        handleClick() { /* ... */ },
        loadNode(node, resolve) { /* ... */ },
        handleNodeClick(data) { /* ... */ }
    }
};
</script>
```

## 后端节点组件开发

### 1. 后端节点基础类

PaddleX Studio 的后端节点组件有几个核心的基础类：

- `BaseNode`：所有节点的基类，定义了节点的基本接口
- `ConstantNode`：常量节点基类，用于处理静态输入
- `ComputeNode`：计算节点基类，用于处理动态计算逻辑
- `StreamNode`：流式节点基类，用于处理流式数据

### 2. 节点类的基本结构

下面是一个基本的后端节点类模板：

```python
from typing import Dict, Optional, Any
from .base_node import ComputeNode, NodeResult

class YourNodeName(ComputeNode):
    """节点功能描述

    详细说明节点的用途和工作原理
    """

    def _run_compute(self, port: str, data: Any) -> 'NodeResult':
        """
        运行节点，处理输入数据并返回结果

        Args:
            port: 输入端口名称
            data: 输入数据

        Returns:
            NodeResult: 包含处理结果的结果对象
        """
        # 从参数中获取配置
        param_value = self.params.get('param_name', default_value)
        
        # 处理逻辑
        result_data = self._process_data(data, param_value)
        
        # 构造结果对象
        result = {
            "output_key": result_data,
            # 可以包含多个输出
        }

        return NodeResult(result, self)

    def process_output(self, result: Any, port: Optional[str] = None) -> Any:
        """
        根据输出端口返回不同的结果

        Args:
            result: 原始结果
            port: 输出端口名称

        Returns:
            处理后的结果
        """
        if port == "output_key":
            return result["output_key"]
        # 可以添加更多的端口处理逻辑
        else:
            return result
    
    def _process_data(self, data: Any, param_value: Any) -> Any:
        """辅助方法，实际的业务逻辑处理"""
        # 实现具体的处理逻辑
        pass
```

### 3. 节点类型说明

#### 3.1 常量节点 (ConstantNode)

常量节点是在工作流启动时一次性处理并输出的节点，它在所有动态节点之前运行。常量节点需要实现以下方法：

- `set_value(value)`：设置节点的常量值
- `_run_constant()`：常量节点的具体运行逻辑

#### 3.2 计算节点 (ComputeNode)

计算节点是根据输入变化实时计算输出的节点，只有当输入端口有数据时才运行。计算节点需要实现：

- `_run_compute(port, data)`：计算节点的具体运行逻辑

#### 3.3 流式节点 (StreamNode)

流式节点能够在运行过程中逐步输出多条数据，每条数据都能立即传递到下游节点进行处理。流式节点需要实现：

- `_stream_output(port, data)`：流式输出的核心逻辑，使用yield逐步返回结果

### 4. 节点结果封装

所有节点的返回值都应该封装在 `NodeResult` 对象中，这个对象提供了以下功能：

- 封装原始运行结果
- 支持根据输出端口名称动态返回不同类型的结果
- 缓存处理过的结果

### 5. 示例：LoadImageNode 节点

以下是 `LoadImageNode` 节点的示例代码：

```python
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
        # 其他情况处理...

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

    # 辅助方法
    def _is_image_file(self, file_path: str) -> bool: """"" # 省略具体实现
    def _read_image(self, file_path: str) -> np.ndarray: """"" # 省略具体实现
```

## 工作流节点的注册和使用

### 1. 后端节点的注册

后端节点需要在工作流管理器中注册后才能被使用。通常，这是通过在 `pxs/workflow/nodes/` 目录下创建节点文件并确保它们被导入到系统中实现的。

### 2. 前后端节点的关联

前端节点组件和后端节点组件通过节点类型名称（`type`）进行关联。前端组件中定义的节点类型名称必须与后端节点类在系统中的注册名称一致。

### 3. 节点数据结构

工作流中的每个节点都有以下基本数据结构：

```javascript
{
    id: "node_id",          // 节点唯一标识
    type: "node_type",      // 节点类型
    name: "节点名称",       // 节点显示名称
    data: {
        inputs: ["input1"], // 输入端口列表
        outputs: ["output1"], // 输出端口列表
        params: {},         // 节点参数
        color: "hsl(...)"   // 节点颜色
    },
    position: { x: 0, y: 0 } // 节点在画布中的位置
}
```

## 高级开发技巧

### 1. 动态属性配置

对于复杂节点，可以使用 `PropertyList` 组件来实现动态属性配置：

```vue
<GroupProperty label="参数组">
    <PropertyList :parameters_def="data.params.params_def"
        :parameters_value="data.params.params_value" 
        :handle-prefix="'params.params_value.'" />
</GroupProperty>
```

### 2. 数据流处理

在处理复杂数据流时，可以利用节点的 `process_output` 方法根据不同的输出端口返回不同格式的数据：

```python
def process_output(self, result: Any, port: Optional[str] = None) -> Any:
    if port == "images":
        # 返回图像数据
        return result["images"]
    elif port == "metadata":
        # 返回元数据
        return result["metadata"]
    else:
        # 返回完整结果
        return result
```

### 3. 异步处理

对于耗时操作，可以考虑使用流式节点（`StreamNode`）来避免阻塞工作流执行：

```python
def _stream_output(self, port: str, data: Any):
    # 逐批处理数据
    for batch in self._process_in_batches(data):
        # 使用yield返回每批结果
        yield NodeResult(batch, self)
```

## 最佳实践

1. **命名规范**：节点类型名称应使用小写字母和下划线组合，避免使用特殊字符
2. **参数验证**：在节点运行前验证输入参数的有效性
3. **错误处理**：提供清晰的错误信息和异常处理机制
4. **文档完善**：为节点添加详细的文档字符串，说明其功能、参数和返回值
5. **代码复用**：抽取通用逻辑为辅助方法或工具函数
6. **性能优化**：对于处理大量数据的节点，考虑分批处理和流式输出

## 调试技巧

1. 使用浏览器的开发者工具调试前端节点组件
2. 在后端节点中添加日志输出，以便跟踪节点执行过程
3. 使用简单的测试工作流验证节点功能
4. 对于复杂节点，考虑先实现基本功能，然后逐步添加高级特性

## 附录：常用工具函数

### 前端工具函数

```javascript
/**
 * 深拷贝
 * @param {any} value - 要拷贝的值
 * @returns {any} 拷贝后的值
 */
const deepClone = function (value) {
    if (value === null || typeof value !== 'object') return value;
    
    if (Array.isArray(value)) {
        return value.map(item => deepClone(item));
    } else {
        const cloned = {};
        for (const key in value) {
            if (Object.prototype.hasOwnProperty.call(value, key)) {
                cloned[key] = deepClone(value[key]);
            }
        }
        return cloned;
    }
}
```

### 后端工具函数

```python
from pxs.workflow.common.utils import parse_port

# 使用示例
def some_method(self, port):
    port_type, port_name = parse_port(port)
    if port_type == "outputs":
        # 处理输出端口
        pass
    elif port_type == "inputs":
        # 处理输入端口
        pass
```

---

希望本文档能够帮助您快速上手 PaddleX Studio 工作流节点插件的开发。如有任何问题或建议，请随时联系我们的开发团队。