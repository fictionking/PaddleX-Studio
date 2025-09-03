<template>
    <WorkflowNode v-bind="$props">
        <template #properties>
            <ValueProperty label="模型类别" :value="data.params.module_name" />
            <ValueProperty label="模型名称" :value="data.params.model_name" />
            <ValueProperty label="模型路径" :value="data.params.model_dir" />
            <GroupProperty label="模型参数" v-if="data.params?.model_params">
                <template v-for="(value, key) in data.params.model_params">
                    <InputNumberProperty v-if="value.type === 'number'" :label="key"
                        v-model="data.params.model_params[key].value"
                        v-bind="{
                          ...(value.min !== undefined && value.min !== null ? { min: value.min } : {}),
                          ...(value.max !== undefined && value.max !== null ? { max: value.max } : {}),
                          ...(value.step !== undefined && value.step !== null ? { step: value.step } : {})
                        }"
                        :handleId="`params.model_params.${key}`"
                        :handleClass="`model_params_${key}`" />
                    <SelectProperty v-else-if="value.type === 'enum' && value.enum" :label="key"
                        v-model="data.params.model_params[key].value" :options="value.enum"
                        :handleId="`params.model_params.${key}`" :handleClass="`model_params_${key}`" />
                    <TextProperty v-else-if="value.type === 'text'" :label="key"
                        v-model="data.params.model_params[key].value"
                        :handleId="`params.model_params.${key}`" :handleClass="`model_params_${key}`" />
                    <BoolProperty v-else-if="value.type === 'bool'" :label="key"
                        v-model="data.params.model_params[key].value"
                        v-bind="{
                          ...(value.trueLabel !== undefined && value.trueLabel !== null ? { trueLabel: value.trueLabel } : {}),
                          ...(value.falseLabel !== undefined && value.falseLabel !== null ? { falseLabel: value.falseLabel } : {})
                        }"
                        :handleId="`params.model_params.${key}`" :handleClass="`model_params_${key}`" />
                    <InputProperty v-else :label="key" v-model="data.params.model_params[key].value"
                        :handleId="`params.model_params.${key}`" :handleClass="`model_params_${key}`" />
                </template>
            </GroupProperty>
            <GroupProperty label="推理参数" v-if="data.params?.infer_params">
                <template v-for="(value, key) in data.params.infer_params">
                    <InputNumberProperty v-if="value.type === 'number'" :label="key"
                        v-model="data.params.infer_params[key].value"
                        v-bind="{
                          ...(value.min !== undefined && value.min !== null ? { min: value.min } : {}),
                          ...(value.max !== undefined && value.max !== null ? { max: value.max } : {}),
                          ...(value.step !== undefined && value.step !== null ? { step: value.step } : {})
                        }"
                        :handleId="`params.infer_params.${key}`"
                        :handleClass="`infer_params_${key}`" />
                    <SelectProperty v-else-if="value.type === 'enum' && value.enum" :label="key"
                        v-model="data.params.infer_params[key].value" :options="value.enum"
                        :handleId="`params.infer_params.${key}`" :handleClass="`infer_params_${key}`" />
                    <TextProperty v-else-if="value.type === 'text'" :label="key"
                        v-model="data.params.infer_params[key].value"
                        :handleId="`params.infer_params.${key}`" :handleClass="`infer_params_${key}`" />
                    <BoolProperty v-else-if="value.type === 'bool'" :label="key"
                        v-model="data.params.infer_params[key].value"
                        v-bind="{
                          ...(value.trueLabel !== undefined && value.trueLabel !== null ? { trueLabel: value.trueLabel } : {}),
                          ...(value.falseLabel !== undefined && value.falseLabel !== null ? { falseLabel: value.falseLabel } : {})
                        }"
                        :handleId="`params.infer_params.${key}`" :handleClass="`infer_params_${key}`" />
                    <InputProperty v-else :label="key" v-model="data.params.infer_params[key].value"
                        :handleId="`params.infer_params.${key}`" :handleClass="`infer_params_${key}`" />
                </template>
            </GroupProperty>
        </template>
    </WorkflowNode>
</template>

<script>
import { ValueProperty, InputProperty,InputNumberProperty,SelectProperty, GroupProperty, WorkflowNode,TextProperty,BoolProperty } from './base/WorkflowNode.mjs'

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
