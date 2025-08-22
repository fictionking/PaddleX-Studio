<template>
    <WorkflowNode :id="id" :data="data">
        <template #properties>
                <ValueProperty
                    label="模块名称"
                    :value="data.params.module_name"
                />
                <ValueProperty
                    label="模型名称"
                    :value="data.params.model_name"
                />
                <GroupProperty label="模型参数" v-if="data.params?.model_params">
                    <InputProperty
                        v-for="(value, key) in data.params.model_params"
                        :key="key"
                        :label="key"
                        v-model="data.params.model_params[key]"
                        :handleId="`params.model_params.${key}`"
                        :handleClass="`model_params_${key}`"
                    />
                </GroupProperty>
                <GroupProperty label="推理参数" v-if="data.params?.infer_params">
                    <InputProperty
                        v-for="(value, key) in data.params.infer_params"
                        :key="key"
                        :label="key"
                        v-model="data.params.infer_params[key]"
                        :handleId="`params.infer_params.${key}`"
                        :handleClass="`infer_params_${key}`"
                    />
                </GroupProperty>
                    </template>
    </WorkflowNode>
</template>

<script>

import WorkflowNode from './base/WorkflowNode.vue';
import ValueProperty from './base/ValueProperty.vue';
import GroupProperty from './base/GroupProperty.vue';
import InputProperty from './base/InputProperty.vue';


/**
 * 模型节点组件
 * 用于展示和配置模型相关参数
 */
export default {
    components: {
        WorkflowNode,
        ValueProperty,
        GroupProperty,
        InputProperty

    },
    props: {
        id: {
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
