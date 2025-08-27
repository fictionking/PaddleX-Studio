<template>
    <WorkflowNode v-bind="$props">
        <template #properties>
        </template>
    </WorkflowNode>
</template>

<script>
import { WorkflowNode } from './base/WorkflowNode.mjs';

/**
 * 简单节点组件
 * 用于配置和展示只有输入输出点的节点
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
