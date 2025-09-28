const { defineAsyncComponent, markRaw } = Vue;
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
/**
 * 为每种节点类型维护一个计数器
 */
const nodeTypeCounters = new Map();

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

/**
 * 工作流节点类型定义
 * 定义了各种节点组件的映射关系
 */
export const nodeTypes = {
    model: markRaw(defineAsyncComponent(() => import(`/components/nodes/model.vue`))),
    save_image: markRaw(defineAsyncComponent(() => import(`/components/nodes/save_image.vue`))),
    load_image: markRaw(defineAsyncComponent(() => import(`/components/nodes/load_image.vue`))),
    load_image_stream: markRaw(defineAsyncComponent(() => import(`/components/nodes/load_image.vue`))),
    number_const: markRaw(defineAsyncComponent(() => import(`/components/nodes/const.vue`))),
    text_const: markRaw(defineAsyncComponent(() => import(`/components/nodes/const.vue`))),
    bool_const: markRaw(defineAsyncComponent(() => import(`/components/nodes/const.vue`))),
    note: markRaw(defineAsyncComponent(() => import(`/components/nodes/base/NoteNode.vue`))),
    save_textfile: markRaw(defineAsyncComponent(() => import(`/components/nodes/save_textfile.vue`))),
};
export const menuItems = [
    {
        label: '输入输出',
        children: [
            {
                label: '加载图像',
                type: 'load_image'
            },
            {
                label: '加载图像(流式)',
                type: 'load_image_stream'
            },
            {
                label: '保存图像',
                type: 'save_image'
            },
            {
                label: '保存文本文件',
                type: 'save_textfile'
            },
        ]
    },
    {
        label: '常量',
        children: [
            {
                label: '数值常量',
                type: 'number_const'
            },
            {
                label: '文本常量',
                type: 'text_const'
            },
            {
                label: '布尔常量',
                type: 'bool_const'
            }
        ]
    },
]

/**
 * 创建节点数据
 * @param {string} type - 节点类型
 * @param {string} subtype - 节点子类型（可选）
 * @returns {object} 节点数据对象
 */
export function createNodeData(type, data = {}) {
    // 生成唯一ID - 使用类型前缀+递增计数器的方式，更短但能保证唯一性
    if (!nodeTypeCounters.has(type)) {
        nodeTypeCounters.set(type, 0);
    }
    const counter = nodeTypeCounters.get(type) + 1;
    nodeTypeCounters.set(type, counter);
    const id = `${type}_${counter}`;

    // 根据节点类型创建不同的节点数据
    let newNode = {
        id: id,
        type: type,
        position: { x: 300, y: 200 },
        data: {
            name: '',
            params: {},
            inputs: [],
            outputs: []
        }
    };

    // 根据节点类型设置特定属性
    switch (type) {
        case 'note':
            newNode.data.name = '备注';
            newNode.data.content = '';
            break;
        case 'load_image':
            newNode.data.name = '加载图像';
            newNode.data.outputs = ['images', 'count'];
            newNode.data.params = {
                path: ''
            };
            break;
        case 'load_image_stream':
            newNode.data.name = '加载图像(流式)';
            newNode.data.outputs = ['images'];
            newNode.data.params = {
                path: ''
            };
            break;
        case 'save_image':
            newNode.data.name = '保存图像';
            newNode.data.inputs = ['images'];
            newNode.data.outputs = ['paths'];
            newNode.data.params = {
                format: 'png',
                path: '',
                filename: 'image',
                clear_dir: false
            };
            break;
        case 'number_const':
            newNode.data.name = '数值常量';
            newNode.data.outputs = ['value'];
            newNode.data.params = {
                type: 'number',
                value: 0
            };
            break;
        case 'text_const':
            newNode.data.name = '文本常量';
            newNode.data.outputs = ['value'];
            newNode.data.params = {
                type: 'text',
                value: ''
            };
            break;
        case 'bool_const':
            newNode.data.name = '布尔常量';
            newNode.data.outputs = ['value'];
            newNode.data.params = {
                type: 'bool',
                value: false
            };
            break;
        case 'model':
            // 添加防御性检查，确保必要的属性存在
            newNode.data = {
                name: data.name,
                params: {
                    module_name: data.params.module_name,
                    model_name: data.params.model_name,
                    model_dir: data.params.model_dir,
                    model_params_def: data.params.model_params ? deepClone(data.params.model_params) : {},
                    infer_params_def: data.params.infer_params ? deepClone(data.params.infer_params) : {},
                    model_params:{},
                    infer_params:{},
                },
                inputs: data.inputs,
                outputs: data.outputs
            };
            break;
        case 'save_textfile':
            newNode.data.name = '保存文本文件';
            newNode.data.inputs = ['object'];
            newNode.data.outputs = ['paths'];
            newNode.data.params = {
                format: 'json',
                path: '',
                filename: 'file',
                clear_dir: false
            };
            break;
    }

    return newNode;
}

// 默认导出
export default nodeTypes;
