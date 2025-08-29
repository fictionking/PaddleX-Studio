<template>
    <WorkflowNode v-bind="$props">
        <template #properties>
            <!-- 基本值属性 -->
            <InputNumberProperty v-if="data.params.type === 'number'" label="值" v-model="data.params.value"
                :min="data.params.min" :max="data.params.max" :step="data.params.step" />
            <SelectProperty v-else-if="data.params.type === 'select' && data.params.options" label="值"
                v-model="data.params.value" :options="data.params.options" />
            <TextProperty v-else-if="data.params.type === 'text'" label="值" v-model="data.params.value" />
            <BoolProperty v-else-if="data.params.type === 'bool'" label="值" v-model="data.params.value"
                :trueLabel="data.params.trueLabel" :falseLabel="data.params.falseLabel" />
            <InputProperty v-else label="值" v-model="data.params.value" />
        </template>
    </WorkflowNode>
</template>

<script>
import { WorkflowNode, InputProperty, InputNumberProperty, SelectProperty, TextProperty, BoolProperty } from './base/WorkflowNode.mjs';

/**
 * 常量节点组件
 * 用于配置和展示常量值
 */
export default {
    components: {
        WorkflowNode,
        InputProperty,
        InputNumberProperty,
        SelectProperty,
        TextProperty,
        BoolProperty
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
