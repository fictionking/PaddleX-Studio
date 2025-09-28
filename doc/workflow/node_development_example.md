# 工作流节点开发完整示例

本文档通过一个完整的示例，展示如何从零开始开发一个 PaddleX Studio 工作流节点插件，包括前端组件和后端逻辑的实现。

## 示例节点概述

在本示例中，我们将开发一个名为 "图像滤镜" 的节点，该节点可以对输入图像应用不同的滤镜效果。这个示例将涵盖以下内容：

1. 创建后端节点类
2. 实现前端节点组件
3. 注册节点到系统中
4. 测试节点功能

## 后端节点实现

### 1. 创建后端节点文件

首先，在 `pxs/workflow/nodes/` 目录下创建一个名为 `image_filter.py` 的文件。

### 2. 实现后端节点类

```python
from typing import Dict, Optional, Any
from .base_node import ComputeNode, NodeResult
import cv2
import numpy as np

class ImageFilterNode(ComputeNode):
    """图像滤镜节点

    用于对输入图像应用各种滤镜效果
    """

    def _run_compute(self, port: str, data: Any) -> 'NodeResult':
        """
        运行图像滤镜节点，对图像应用滤镜效果

        Args:
            port: 输入端口名称
            data: 输入数据（图像或图像列表）

        Returns:
            NodeResult: 包含处理后图像的结果对象
        """
        # 从参数中获取滤镜类型和参数
        filter_type = self.params.get('filter_type', 'grayscale')
        intensity = self.params.get('intensity', 1.0)
        
        # 确保强度在有效范围内
        intensity = max(0.0, min(2.0, intensity))
        
        # 处理单张图像或多张图像
        if isinstance(data, np.ndarray):
            # 单张图像
            filtered_image = self._apply_filter(data, filter_type, intensity)
            result = {
                "image": filtered_image,
                "filter_type": filter_type,
                "intensity": intensity
            }
        elif isinstance(data, list) and all(isinstance(img, np.ndarray) for img in data):
            # 图像列表
            filtered_images = []
            for img in data:
                filtered = self._apply_filter(img, filter_type, intensity)
                filtered_images.append(filtered)
            result = {
                "images": filtered_images,
                "filter_type": filter_type,
                "intensity": intensity,
                "count": len(filtered_images)
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
        elif port == "filter_type":
            return result["filter_type"]
        elif port == "intensity":
            return result["intensity"]
        elif port == "count" and "count" in result:
            return result["count"]
        else:
            return result

    def _apply_filter(self, image: np.ndarray, filter_type: str, intensity: float) -> np.ndarray:
        """
        应用指定的滤镜效果

        Args:
            image: 输入图像
            filter_type: 滤镜类型
            intensity: 滤镜强度（0.0-2.0）

        Returns:
            np.ndarray: 应用滤镜后的图像
        """
        # 确保图像是RGB格式
        if len(image.shape) == 2:
            # 灰度图转换为RGB
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        elif len(image.shape) == 3 and image.shape[2] == 4:
            # RGBA转换为RGB
            image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
        
        # 创建输出图像副本
        output = image.copy()
        
        # 根据滤镜类型应用不同的效果
        if filter_type == 'grayscale':
            # 灰度滤镜
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            gray_rgb = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
            # 根据强度混合原图和灰度图
            output = cv2.addWeighted(image, 1 - intensity, gray_rgb, intensity, 0)
        
        elif filter_type == 'sepia':
            # 棕褐色滤镜
            # 棕褐色变换矩阵
            sepia_kernel = np.array([
                [0.393, 0.769, 0.189],
                [0.349, 0.686, 0.168],
                [0.272, 0.534, 0.131]
            ])
            # 应用变换并裁剪到0-255范围
            sepia = cv2.transform(image, sepia_kernel)
            sepia = np.clip(sepia, 0, 255).astype(np.uint8)
            # 根据强度混合原图和棕褐色图
            output = cv2.addWeighted(image, 1 - intensity, sepia, intensity, 0)
        
        elif filter_type == 'invert':
            # 反转颜色滤镜
            inverted = cv2.bitwise_not(image)
            # 根据强度混合原图和反转图
            output = cv2.addWeighted(image, 1 - intensity, inverted, intensity, 0)
        
        elif filter_type == 'brightness':
            # 亮度调整
            # 转换为浮点型以避免溢出
            float_image = image.astype(np.float32)
            # 调整亮度
            brightened = float_image * intensity
            # 裁剪到0-255范围
            output = np.clip(brightened, 0, 255).astype(np.uint8)
        
        elif filter_type == 'contrast':
            # 对比度调整
            # 转换为浮点型
            float_image = image.astype(np.float32)
            # 调整对比度：output = (input - 128) * contrast + 128
            contrast_adjusted = (float_image - 128) * intensity + 128
            # 裁剪到0-255范围
            output = np.clip(contrast_adjusted, 0, 255).astype(np.uint8)
        
        elif filter_type == 'blur':
            # 模糊滤镜
            # 根据强度确定模糊半径
            kernel_size = max(1, int(5 * intensity))
            # 确保kernel_size是奇数
            if kernel_size % 2 == 0:
                kernel_size += 1
            output = cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
        
        elif filter_type == 'sharpen':
            # 锐化滤镜
            # 锐化核
            sharpen_kernel = np.array([[-1, -1, -1],
                                       [-1, 9 + (intensity * 4), -1],
                                       [-1, -1, -1]])
            # 应用锐化
            sharpened = cv2.filter2D(image, -1, sharpen_kernel)
            # 裁剪到0-255范围
            output = np.clip(sharpened, 0, 255).astype(np.uint8)
        
        else:
            # 未知滤镜类型，返回原图
            pass
        
        return output
```

## 前端节点组件实现

### 1. 创建前端节点组件文件

在 `templates/components/nodes/` 目录下创建一个名为 `image_filter.vue` 的文件。

### 2. 实现前端节点组件

```vue
<template>
    <WorkflowNode v-bind="$props">
        <template #properties>
            <SelectProperty label="滤镜类型" v-model="data.params.filter_type" 
                :options="filterOptions" />
            <InputNumberProperty label="强度" v-model="data.params.intensity" 
                :min="0.0" :max="2.0" :step="0.1" />
            <div class="filter-preview" v-if="previewImage">
                <img :src="previewImage" alt="滤镜预览" />
            </div>
        </template>
    </WorkflowNode>
</template>

<script>
import { WorkflowNode, SelectProperty, InputNumberProperty } from './base/WorkflowNode.mjs';

/**
 * 图像滤镜节点组件
 * 用于配置和应用各种图像滤镜效果
 */
export default {
    components: {
        WorkflowNode,
        SelectProperty,
        InputNumberProperty
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
            // 滤镜选项列表
            filterOptions: [
                { value: 'grayscale', label: '灰度' },
                { value: 'sepia', label: '棕褐色' },
                { value: 'invert', label: '反转颜色' },
                { value: 'brightness', label: '亮度调整' },
                { value: 'contrast', label: '对比度调整' },
                { value: 'blur', label: '模糊' },
                { value: 'sharpen', label: '锐化' }
            ],
            // 预览图像
            previewImage: null
        }
    },
    watch: {
        // 监听参数变化，更新预览
        'data.params': {
            handler() {
                this.updatePreview();
            },
            deep: true,
            immediate: true
        }
    },
    methods: {
        /**
         * 更新滤镜预览
         */
        updatePreview() {
            // 创建一个简单的测试图像用于预览
            const canvas = document.createElement('canvas');
            canvas.width = 100;
            canvas.height = 100;
            const ctx = canvas.getContext('2d');
            
            // 绘制一个简单的测试图案
            ctx.fillStyle = '#3498db';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#e74c3c';
            ctx.beginPath();
            ctx.arc(canvas.width/2, canvas.height/2, 30, 0, Math.PI * 2);
            ctx.fill();
            
            // 获取滤镜参数
            const filterType = this.data.params.filter_type || 'grayscale';
            const intensity = this.data.params.intensity || 1.0;
            
            // 根据滤镜类型应用不同的CSS滤镜
            let cssFilter = '';
            
            switch(filterType) {
                case 'grayscale':
                    cssFilter = `grayscale(${intensity * 100}%)`;
                    break;
                case 'sepia':
                    cssFilter = `sepia(${intensity * 100}%)`;
                    break;
                case 'invert':
                    cssFilter = `invert(${intensity * 100}%)`;
                    break;
                case 'brightness':
                    cssFilter = `brightness(${intensity * 100}%)`;
                    break;
                case 'contrast':
                    cssFilter = `contrast(${intensity * 100}%)`;
                    break;
                case 'blur':
                    cssFilter = `blur(${intensity * 5}px)`;
                    break;
                case 'sharpen':
                    // CSS没有直接的锐化滤镜，可以通过对比度模拟
                    cssFilter = `contrast(${(1 + intensity) * 100}%)`;
                    break;
                default:
                    cssFilter = '';
            }
            
            // 应用滤镜并生成预览图像
            const img = new Image();
            img.onload = () => {
                const filteredCanvas = document.createElement('canvas');
                filteredCanvas.width = canvas.width;
                filteredCanvas.height = canvas.height;
                const filteredCtx = filteredCanvas.getContext('2d');
                
                // 应用CSS滤镜
                filteredCtx.filter = cssFilter;
                filteredCtx.drawImage(img, 0, 0);
                
                // 保存为DataURL
                this.previewImage = filteredCanvas.toDataURL('image/png');
            };
            
            // 设置图像源为原始画布
            img.src = canvas.toDataURL('image/png');
        }
    },
    beforeUnmount() {
        // 清理预览图像资源
        this.previewImage = null;
    }
};
</script>

<style scoped>
/* 滤镜预览样式 */
.filter-preview {
    margin-top: 8px;
    padding: 4px;
    background-color: rgba(255, 255, 255, 0.1);
    border-radius: 4px;
    text-align: center;
}

.filter-preview img {
    max-width: 100px;
    max-height: 100px;
    border-radius: 4px;
}

/* 节点样式定制 */
:deep(.custom-node.image_filter) {
    background-color: #2c3e50;
}

:deep(.node-header.image_filter) {
    background-color: #34495e;
}
</style>
```

## 注册节点

### 1. 注册前端节点组件

编辑 `templates/components/nodes/nodes.mjs` 文件，添加我们的新节点：

```javascript
export const nodeTypes = {
    // 已有的节点类型...
    image_filter: markRaw(defineAsyncComponent(() => import(`/components/nodes/image_filter.vue`))),
};

// 在menuItems中添加菜单项
export const menuItems = [
    // 已有的菜单项...
    {
        label: '图像增强',
        children: [
            {
                label: '图像滤镜',
                type: 'image_filter'
            },
        ]
    },
];
```

### 2. 后端节点注册

后端节点通常不需要显式注册，只要确保节点文件位于 `pxs/workflow/nodes/` 目录下并且能够被导入即可。系统会自动发现并注册这些节点。

如果需要显式注册，可以在 `pxs/workflowMgr.py` 或其他适当的位置添加导入语句：

```python
# 导入我们的新节点
from pxs.workflow.nodes.image_filter import ImageFilterNode
```

## 节点数据结构定义

为了确保我们的节点能够正确工作，我们需要定义节点的输入/输出端口和默认参数。这些信息通常在前端组件中设置，或者通过配置文件定义。

### 前端组件中的数据结构初始化

在实际使用中，当用户从菜单中拖放一个新节点到工作流画布上时，系统会创建一个节点实例并初始化其数据结构。我们需要确保我们的节点组件能够正确处理这些初始化数据。

以下是我们的 `ImageFilterNode` 节点的数据结构示例：

```javascript
{
    id: "image_filter_1",  // 自动生成的唯一ID
    type: "image_filter",  // 节点类型
    name: "图像滤镜",      // 节点显示名称
    data: {
        inputs: ["image"], // 输入端口
        outputs: ["image"], // 输出端口
        params: {
            filter_type: "grayscale", // 默认滤镜类型
            intensity: 1.0            // 默认强度
        },
        color: "hsl(200, 70%, 20%)" // 默认颜色
    },
    position: { x: 0, y: 0 } // 节点在画布中的位置
}
```

## 测试节点功能

### 1. 创建测试工作流

为了测试我们的新节点，我们可以创建一个简单的工作流：

1. 添加一个 "加载图像" 节点
2. 添加我们的 "图像滤镜" 节点，并连接到加载图像节点的输出
3. 添加一个 "保存图像" 节点，并连接到图像滤镜节点的输出

### 2. 配置节点参数

1. 对于 "加载图像" 节点，选择一个测试图像文件
2. 对于 "图像滤镜" 节点，选择不同的滤镜类型和强度值
3. 对于 "保存图像" 节点，设置输出文件路径

### 3. 运行工作流并验证结果

1. 点击工作流编辑器中的运行按钮
2. 检查输出目录中生成的图像文件
3. 验证滤镜效果是否符合预期

## 调试技巧

在开发过程中，以下调试技巧可能会有所帮助：

### 前端调试

1. 使用浏览器的开发者工具检查控制台输出和网络请求
2. 在组件中添加 `console.log` 语句输出调试信息
3. 使用 Vue DevTools 扩展来检查组件状态和属性

### 后端调试

1. 在节点代码中添加 `print` 语句输出调试信息
2. 使用 Python 的内置 `logging` 模块记录详细日志
3. 对于图像处理节点，可以将中间结果保存为图像文件进行检查

```python
# 示例：保存中间结果
cv2.imwrite('debug_intermediate.png', intermediate_result)
```

## 性能优化

对于图像处理节点，性能优化尤为重要。以下是一些优化建议：

1. 使用 OpenCV 的内置函数而不是自定义实现，因为 OpenCV 函数通常是高度优化的
2. 对于批量图像处理，考虑使用批处理操作
3. 对于大型图像，可以考虑先调整大小再进行处理
4. 对于计算密集型操作，可以考虑使用 GPU 加速

## 完整集成测试

在完成开发后，进行完整的集成测试是很重要的：

1. 测试各种输入图像格式和尺寸
2. 测试所有滤镜类型和不同的强度值
3. 测试节点在复杂工作流中的行为
4. 测试错误处理和边界情况

## 总结

通过这个示例，我们学习了如何：

1. 创建后端节点类，实现图像处理逻辑
2. 开发前端节点组件，提供参数配置界面
3. 注册节点到系统中
4. 测试和优化节点功能

这个图像滤镜节点只是一个简单的示例，但它展示了 PaddleX Studio 工作流节点开发的基本流程和最佳实践。开发者可以基于这个示例，开发更复杂和功能丰富的工作流节点。

---

希望这个示例文档能够帮助您快速上手 PaddleX Studio 工作流节点的开发。如果您有任何问题或需要进一步的帮助，请参考前面的 API 文档或联系我们的开发团队。