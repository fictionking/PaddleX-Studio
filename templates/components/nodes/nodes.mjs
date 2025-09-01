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

// 默认导出
export default nodeTypes;