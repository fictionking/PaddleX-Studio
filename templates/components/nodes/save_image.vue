<template>
    <WorkflowNode :id="id" :type="type" :data="data">
        <template #properties>
            <SelectProperty label="图片格式" v-model="data.params.format"
                :options="[{ label: 'png', value: 'png' }, { label: 'jpg', value: 'jpg' }]" handleId="params.format"
                handleClass="format" />
            <InputProperty label="输出目录" v-model="data.params.path" handleId="params.path" handleClass="path" />
            <InputProperty label="保存文件名" v-model="data.params.filename" handleId="params.filename"
                handleClass="filename" />
        </template>
    </WorkflowNode>
</template>

<script>
import { WorkflowNode,InputProperty,SelectProperty } from './base/WorkflowNode.mjs';

/**
 * 图像文件输出节点组件
 * 用于配置和展示图像输出相关参数
 */
export default {
    components: {
        WorkflowNode,
        InputProperty,
        SelectProperty
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
