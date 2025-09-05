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
 * 工作流节点类型定义
 * 定义了各种节点组件的映射关系
 */
export const nodeTypes = {
    request: markRaw(defineAsyncComponent(() => import(`/components/nodes/simple.vue`))),
    response: markRaw(defineAsyncComponent(() => import(`/components/nodes/simple.vue`))),
    model: markRaw(defineAsyncComponent(() => import(`/components/nodes/model.vue`))),
    save_image: markRaw(defineAsyncComponent(() => import(`/components/nodes/save_image.vue`))),
    load_image: markRaw(defineAsyncComponent(() => import(`/components/nodes/simple.vue`))),
    number_const: markRaw(defineAsyncComponent(() => import(`/components/nodes/const.vue`))),
    string_const: markRaw(defineAsyncComponent(() => import(`/components/nodes/const.vue`))),
    text_const: markRaw(defineAsyncComponent(() => import(`/components/nodes/const.vue`))),
    bool_const: markRaw(defineAsyncComponent(() => import(`/components/nodes/const.vue`))),
    note: markRaw(defineAsyncComponent(() => import(`/components/nodes/base/NoteNode.vue`))),
};
export const menuItems = [
    {
        label: '输入输出',
        children: [
            {
                label: '请求输入',
                type: 'request'
            },
            {
                label: '请求输出',
                type: 'response'
            },
            {
                label: '加载图像',
                type: 'load_image'
            },
            {
                label: '保存图像',
                type: 'save_image'
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
                label: '字符串常量',
                type: 'string_const'
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
    // 生成唯一ID
    const id = `${type}_${Date.now()}`;

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
        case 'request':
            newNode.data.name = '请求输入';
            newNode.data.fixName = true;
            newNode.data.outputs = ['input'];
            break;
        case 'response':
            newNode.data.name = '请求输出';
            newNode.data.fixName = true;
            newNode.data.inputs = ['output'];
            break;
        case 'load_image':
            newNode.data.name = '加载图像';
            newNode.data.inputs = ['files'];
            newNode.data.outputs = ['images', 'count'];
            break;
        case 'save_image':
            newNode.data.name = '保存图像';
            newNode.data.inputs = ['images'];
            newNode.data.outputs = ['files'];
            newNode.data.params = {
                format: 'png',
                path: 'output/images',
                filename: 'image'
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
        case 'string_const':
            newNode.data.name = '字符串常量';
            newNode.data.outputs = ['value'];
            newNode.data.params = {
                type: 'string',
                value: ''
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
                    model_params: data.params.model_params ? deepClone(data.params.model_params) : {},
                    infer_params: data.params.infer_params ? deepClone(data.params.infer_params) : {},
                },
                inputs: data.inputs,
                outputs: data.outputs
            };
            break;
    }

    return newNode;
}

// 默认导出
export default nodeTypes;
