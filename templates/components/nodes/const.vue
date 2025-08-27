<template>
    <WorkflowNode v-bind="$props">
        <template #properties>
            <InputProperty label="常量值" v-model="data.params.value" />
        </template>
    </WorkflowNode>
</template>

<script>
import { WorkflowNode, InputProperty } from './base/WorkflowNode.mjs';

/**
 * 常量节点组件
 * 用于配置和展示常量值
 */
export default {
    components: {
        WorkflowNode,
        InputProperty,
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
