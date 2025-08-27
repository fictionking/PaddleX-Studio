<template>
    <WorkflowNode v-bind="$props">
        <template #properties>
            <ValueProperty label="模块名称" :value="data.params.module_name" />
            <ValueProperty label="模型名称" :value="data.params.model_name" />
            <GroupProperty label="模型参数" v-if="data.params?.model_params">
                <InputProperty v-for="(value, key) in data.params.model_params" :label="key"
                    v-model="value.value" :type="value.type"
                    :min="value.min" :max="value.max"
                    :step="value.step" :handleId="`params.model_params.${key}`"
                    :handleClass="`model_params_${key}`" />
            </GroupProperty>
            <GroupProperty label="推理参数" v-if="data.params?.infer_params">
                <InputProperty v-for="(value, key) in data.params.infer_params" :label="key"
                    v-model="data.params.infer_params[key].value" :type="data.params.infer_params[key].type"
                    :min="data.params.infer_params[key].min" :max="data.params.infer_params[key].max"
                    :step="data.params.infer_params[key].step" :handleId="`params.infer_params.${key}`"
                    :handleClass="`infer_params_${key}`" />
            </GroupProperty>
        </template>
    </WorkflowNode>
</template>

<script>
import { ValueProperty, InputProperty, GroupProperty, WorkflowNode } from './base/WorkflowNode.mjs'

/**
 * 模型节点组件
 * 用于展示和配置模型相关参数
 */
export default {
    components: {
        WorkflowNode,
        ValueProperty,
        GroupProperty,
        InputProperty,
    },
    // mixins: [WorkflowNondes],
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
