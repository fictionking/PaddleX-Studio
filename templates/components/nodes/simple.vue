<template>
    <WorkflowNode :id="id" :type="type" :data="data">
        <template #properties>
        </template>
    </WorkflowNode>
</template>

<script>
import { WorkflowNode } from './base/WorkflowNode.mjs';

/**
 * 图像文件输出节点组件
 * 用于配置和展示图像输出相关参数
 */
export default {
    components: {
        WorkflowNode,
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
    }
};
</script>
