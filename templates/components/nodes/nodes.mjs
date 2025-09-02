const { defineAsyncComponent, markRaw } = Vue;

/**
 * 工作流节点类型定义
 * 定义了各种节点组件的映射关系
 */
export const nodeTypes = {
    start: markRaw(defineAsyncComponent(() => import(`/components/nodes/simple.vue`))),
    end: markRaw(defineAsyncComponent(() => import(`/components/nodes/simple.vue`))),
    model: markRaw(defineAsyncComponent(() => import(`/components/nodes/model.vue`))),
    save_image: markRaw(defineAsyncComponent(() => import(`/components/nodes/save_image.vue`))),
    load_image: markRaw(defineAsyncComponent(() => import(`/components/nodes/simple.vue`))),
    number_const: markRaw(defineAsyncComponent(() => import(`/components/nodes/const.vue`))),
    string_const: markRaw(defineAsyncComponent(() => import(`/components/nodes/const.vue`))),
};

/**
 * 创建节点数据
 * @param {string} type - 节点类型
 * @param {string} subtype - 节点子类型（可选）
 * @returns {object} 节点数据对象
 */
export function createNodeData(type, subtype = '',params = {}) {
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
        case 'start':
            newNode.data.name = '开始';
            newNode.data.fixName = true;
            newNode.data.outputs = ['input'];
            break;
        case 'end':
            newNode.data.name = '结束';
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
                value: 0
            };
            break;
        case 'string_const':
            newNode.data.name = '字符串常量';
            newNode.data.outputs = ['value'];
            newNode.data.params = {
                value: ''
            };
            break;
        case 'model':
            if (subtype === 'object_detection') {
                newNode.data.name = '目标识别';
                newNode.data.params = {...params};
                newNode.data.inputs = ['images'];
                newNode.data.outputs = ['images', 'boxes', 'count'];
            } else if (subtype === 'image_classification') {
                newNode.data.name = '图像分类';
                newNode.data.params = {...params};
                newNode.data.inputs = ['images'];
                newNode.data.outputs = ['labels'];
            }
            break;
    }

    return newNode;
}

// 默认导出
export default nodeTypes;
                        