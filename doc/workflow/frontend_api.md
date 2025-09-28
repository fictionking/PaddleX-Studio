# 前端节点组件 API 参考

本文档提供 PaddleX Studio 工作流前端节点组件的详细 API 参考，帮助开发者更深入地理解和使用前端节点组件。

## 基础节点组件 (WorkflowNode)

`WorkflowNode` 是所有工作流节点的基类，提供了节点的基本结构和功能。

### 组件参数

| 参数名 | 类型 | 必填 | 描述 |
|-------|------|------|------|
| id | String | 是 | 节点唯一标识符 |
| type | String | 是 | 节点类型名称 |
| data | Object | 是 | 节点数据，包含名称、输入/输出端口和参数等 |
| selected | Boolean | 否 | 节点是否被选中，默认为 `false` |

### 数据结构

`data` 参数是一个包含以下字段的对象：

```javascript
{
    name: "节点名称",         // 节点显示名称
    inputs: ["input1", "input2"], // 输入端口列表
    outputs: ["output1"],     // 输出端口列表
    params: {},              // 节点参数对象
    color: "hsl(...)"        // 节点颜色
}
```

### 组件事件

| 事件名 | 描述 | 参数 |
|-------|------|------|
| update:name | 当节点名称被编辑并确认后触发 | `newName` - 新的节点名称 |

### 方法

| 方法名 | 描述 | 参数 |
|-------|------|------|
| startEditName() | 开始编辑节点名称 | 无 |
| finishEditName() | 完成编辑节点名称 | 无 |

### 插槽

| 插槽名 | 描述 |
|-------|------|
| properties | 用于放置节点的属性组件 |

## 属性组件

### InputProperty

文本输入框组件，用于接收文本类型的参数。

#### 组件参数

| 参数名 | 类型 | 必填 | 描述 |
|-------|------|------|------|
| label | String | 是 | 属性标签文本 |
| v-model | String | 是 | 绑定的参数值 |
| placeholder | String | 否 | 输入框占位符文本 |
| disabled | Boolean | 否 | 是否禁用输入，默认为 `false` |

### InputNumberProperty

数字输入框组件，用于接收数字类型的参数。

#### 组件参数

| 参数名 | 类型 | 必填 | 描述 |
|-------|------|------|------|
| label | String | 是 | 属性标签文本 |
| v-model | Number | 是 | 绑定的参数值 |
| min | Number | 否 | 最小值限制 |
| max | Number | 否 | 最大值限制 |
| step | Number | 否 | 步长，默认为 1 |
| disabled | Boolean | 否 | 是否禁用输入，默认为 `false` |

### SelectProperty

下拉选择框组件，用于从预定义选项中选择参数值。

#### 组件参数

| 参数名 | 类型 | 必填 | 描述 |
|-------|------|------|------|
| label | String | 是 | 属性标签文本 |
| v-model | Any | 是 | 绑定的参数值 |
| options | Array | 是 | 选项列表，每项包含 `value` 和 `label` 属性 |
| disabled | Boolean | 否 | 是否禁用选择，默认为 `false` |

### TextProperty

纯文本显示组件，用于显示只读的文本信息。

#### 组件参数

| 参数名 | 类型 | 必填 | 描述 |
|-------|------|------|------|
| label | String | 是 | 属性标签文本 |
| value | String | 是 | 要显示的文本值 |
| style | Object | 否 | 自定义样式对象 |

### ValueProperty

值显示组件，用于显示只读的参数值。

#### 组件参数

| 参数名 | 类型 | 必填 | 描述 |
|-------|------|------|------|
| label | String | 是 | 属性标签文本 |
| value | Any | 是 | 要显示的值 |
| format | Function | 否 | 格式化函数，用于自定义值的显示格式 |

### BoolProperty

布尔值选择组件，用于开关类型的参数。

#### 组件参数

| 参数名 | 类型 | 必填 | 描述 |
|-------|------|------|------|
| label | String | 是 | 属性标签文本 |
| v-model | Boolean | 是 | 绑定的布尔值 |
| disabled | Boolean | 否 | 是否禁用开关，默认为 `false` |

### InputWithButtonProperty

带按钮的输入框组件，用于需要用户交互选择的参数。

#### 组件参数

| 参数名 | 类型 | 必填 | 描述 |
|-------|------|------|------|
| label | String | 是 | 属性标签文本 |
| v-model | String | 是 | 绑定的参数值 |
| buttonText | String | 否 | 按钮文本 |
| buttonIcon | String | 否 | 按钮图标名称 |
| disabled | Boolean | 否 | 是否禁用组件，默认为 `false` |

#### 组件事件

| 事件名 | 描述 | 参数 |
|-------|------|------|
| buttonClick | 当按钮被点击时触发 | 无 |

### GroupProperty

属性分组组件，用于将一组相关的属性组织在一起。

#### 组件参数

| 参数名 | 类型 | 必填 | 描述 |
|-------|------|------|------|
| label | String | 是 | 分组标签文本 |
| collapsed | Boolean | 否 | 是否默认折叠，默认为 `false` |

#### 插槽

| 插槽名 | 描述 |
|-------|------|
| default | 用于放置分组内的属性组件 |

### PropertyList

动态属性列表组件，用于处理复杂的嵌套参数结构。

#### 组件参数

| 参数名 | 类型 | 必填 | 描述 |
|-------|------|------|------|
| parameters_def | Object | 是 | 参数定义对象，描述参数的类型和结构 |
| parameters_value | Object | 是 | 参数值对象，存储实际的参数值 |
| handle-prefix | String | 否 | 事件处理器前缀，用于区分不同的参数组 |
| handle-class-prefix | String | 否 | CSS类名前缀，用于样式定制 |

## 节点类型注册和管理

### 节点类型注册

在 `nodes.mjs` 文件中，使用 `defineAsyncComponent` 和 `markRaw` 函数注册节点组件：

```javascript
export const nodeTypes = {
    your_node_type: markRaw(defineAsyncComponent(() => import(`/components/nodes/your_node_file.vue`))),
    // 更多节点类型...
};
```

### 菜单项配置

在 `menuItems` 数组中配置节点在菜单中的显示位置：

```javascript
export const menuItems = [
    {
        label: '菜单项名称',
        children: [
            {
                label: '节点显示名称',
                type: 'node_type'
            },
            // 更多子菜单项...
        ]
    },
    // 更多菜单项...
];
```

### 工具函数

#### deepClone

用于深拷贝对象或数组：

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

#### initializeNodeCounters

初始化节点计数器，确保新生成的节点ID不会与现有节点ID冲突：

```javascript
/**
 * 初始化节点计数器
 * 在工作流加载时调用此函数，确保新生成的ID不会与现有节点ID冲突
 * @param {Array} nodes - 现有节点列表
 */
export function initializeNodeCounters(nodes) {
    // 清空现有计数器
    nodeTypeCounters.clear();
    // 遍历所有节点，更新对应的计数器
    if (nodes && Array.isArray(nodes)) {
        nodes.forEach(node => {
            if (node.id && node.type) {
                // 尝试从ID中提取计数器值
                const match = node.id.match(`^${node.type}_(\\d+)$`);
                if (match && match[1]) {
                    const counter = parseInt(match[1]);
                    // 更新该类型的最大计数器值
                    const currentMax = nodeTypeCounters.get(node.type) || 0;
                    if (counter > currentMax) {
                        nodeTypeCounters.set(node.type, counter);
                    }
                }
            }
        });
    }
}
```

## 组件生命周期钩子

在开发自定义节点组件时，可以利用 Vue 的生命周期钩子来实现特定的功能：

```javascript
export default {
    // ...
    created() {
        // 组件实例创建后立即调用
        // 可以在这里初始化数据或绑定事件
    },
    mounted() {
        // 组件挂载到DOM后调用
        // 可以在这里访问DOM元素或执行需要DOM的操作
    },
    updated() {
        // 组件数据更新并重新渲染后调用
        // 可以在这里执行数据更新后的逻辑
    },
    beforeUnmount() {
        // 组件卸载前调用
        // 可以在这里清理事件监听器或定时器等
    }
    // ...
}
```

## 依赖注入

在节点组件中，可以使用 Vue 的依赖注入功能获取父组件提供的数据：

```javascript
import { inject, computed } from 'vue'

export default {
    // ...
    setup(props) {
        // 注入父组件提供的数据
        const models = inject('models', [])
        const cachedModels = inject('cachedModels', [])
        
        // 使用计算属性处理注入的数据
        const currentModule = computed(() => {
            // 根据 props.data.params.module_name 查找对应的模块
            // ...
        })
        
        return {
            models,
            cachedModels,
            currentModule
        }
    }
    // ...
}
```

## 自定义样式

可以通过在组件的 `<style scoped>` 块中添加样式来自定义节点的外观：

```vue
<style scoped>
/* 自定义节点样式 */
:deep(.custom-node.your-node-type) {
    background-color: #4a5568;
}

:deep(.node-header.your-node-type) {
    background-color: #2d3748;
}

/* 自定义属性组件样式 */
.your-custom-class {
    margin: 8px 0;
    padding: 8px;
    background-color: #2d3748;
    border-radius: 4px;
}
</style>
```

## 表单验证

对于需要验证的表单字段，可以使用自定义验证逻辑或第三方验证库：

```javascript
methods: {
    validateForm() {
        // 验证逻辑
        if (!this.data.params.requiredField) {
            this.$message.error('请填写必填字段');
            return false;
        }
        
        if (this.data.params.numberField && this.data.params.numberField < 0) {
            this.$message.error('数值必须大于等于0');
            return false;
        }
        
        return true;
    },
    
    async submitForm() {
        if (this.validateForm()) {
            try {
                // 提交表单逻辑
                await this.submitData();
                this.$message.success('提交成功');
            } catch (error) {
                this.$message.error('提交失败：' + error.message);
            }
        }
    }
}
```

## 常见问题解决

### 1. 节点数据不更新

如果发现节点数据没有正确更新，可以检查以下几点：

- 确保使用了正确的 `v-model` 绑定
- 检查是否在子组件中直接修改了 props 数据（应该通过事件通知父组件更新）
- 对于复杂对象，确保正确使用了响应式数据

### 2. 组件加载失败

如果节点组件加载失败，可以检查以下几点：

- 确保在 `nodes.mjs` 中正确注册了节点类型
- 检查组件文件路径是否正确
- 检查组件代码是否有语法错误

### 3. 样式问题

如果节点样式不符合预期，可以尝试：

- 使用 `:deep()` 选择器穿透 scoped 样式
- 检查是否有 CSS 优先级问题
- 确保自定义样式不会覆盖基础节点样式的关键部分

---

通过本文档，您应该能够更好地理解和使用 PaddleX Studio 工作流的前端节点组件 API。如果您有任何问题或需要进一步的帮助，请参考 Vue 官方文档或联系我们的开发团队。