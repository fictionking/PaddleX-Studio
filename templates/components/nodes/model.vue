<template>
    <WorkflowNode v-bind="$props">
        <template #properties>
            <ValueProperty label="模型类别" :value="data.params.module_name" />
            <ValueProperty label="模型名称" :value="data.params.model_name" />
            <ValueProperty label="模型路径" :value="data.params.model_dir" />
            <GroupProperty label="模型参数" v-if="data.params?.model_params">
                <PropertyList :parameters="data.params.model_params" />
            </GroupProperty>
            <GroupProperty label="推理参数" v-if="data.params?.infer_params">
                <PropertyList :parameters="data.params.infer_params" :handle-prefix="'params.infer_params.'"
                    :handle-class-prefix="'infer_params_'" />
            </GroupProperty>
        </template>
    </WorkflowNode>
</template>

<script>
import { ValueProperty, InputProperty, InputNumberProperty, SelectProperty, GroupProperty, WorkflowNode, TextProperty, BoolProperty, PropertyList } from './base/WorkflowNode.mjs'

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
        InputNumberProperty,
        SelectProperty,
        TextProperty,
        BoolProperty,
        PropertyList
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
