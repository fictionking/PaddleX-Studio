<template>
    <div class="property-item">
        <div class="label-row">
            <Handle v-if="handleId" type="target" :position="Position.Left" :id="handleId"
                :class="['handle-inline', 'params-port', handleClass]" />
            <span class="property-label">{{ label }}:</span>
        </div>
        <el-input type="textarea" v-model="internalValue" class="property-value input nodrag"
            :autosize="{ minRows: 1, maxRows: 20 }" resize="none" size="small" @change="updateValue" />
    </div>
</template>

<script>
import { Handle, Position } from '/libs/vue-flow/core/vue-flow-core.mjs';
import { ref, watch } from 'vue';

/**
 * 输入属性组件
 * 用于带有输入框的属性项
 */
export default {
    components: {
        Handle,
    },
    props: {
        label: {
            type: String,
            required: true,
            description: '属性标签'
        },
        modelValue: {
            type: [String, Number],
            required: true,
            description: '输入框绑定的值，支持字符串和数值类型'
        },
        handleId: {
            type: String,
            default: '',
            description: '连接点ID，为空则不显示连接点'
        },
        handleClass: {
            type: String,
            default: '',
            description: '连接点额外样式类'
        }
    },
    emits: ['update:modelValue'],
    setup(props, { emit }) {
        // 创建内部状态以避免直接修改props
        const internalValue = ref(props.modelValue);

        // 监听外部modelValue变化，同步到内部状态
        watch(() => props.modelValue, (newValue) => {
            internalValue.value = newValue;
        });

        // 更新值的方法
        const updateValue = () => {
            emit('update:modelValue', internalValue.value);
        };

        return {
            Position,
            internalValue,
            updateValue
        };
    }
};
</script>

<style scoped>
.property-item {
    color: var(--el-text-color-secondary);
    position: relative;
    margin-bottom: 5px;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
}

.label-row {
    display: flex;
    align-items: center;
    margin-bottom: 5px;
}

.property-label {
    min-width: 50px;
    margin-bottom: 5px;
    line-height: 1;
}

.property-value {
    width: 100%;
    font-size: 10px;
    min-width: 150px;
    word-break: break-all;
    --el-input-text-color: var(--el-text-color-secondary);
    --el-input-bg-color: var(--el-fill-color-lighter);
    background-color: transparent;
}

.property-value.input {
    --el-input-border: none;
    --el-input-border-color: transparent;
    border-width: 0;
}

.handle-inline {
    position: absolute;
    top: 10px;
    left: -10px;
}

/* 自定义textarea滚动条样式 - WebKit浏览器 */
:deep(.el-textarea__inner) {

    /* 滚动条整体样式 */
    &::-webkit-scrollbar {
        width: 8px;
        /* 垂直滚动条宽度 */
        height: 8px;
        /* 水平滚动条高度 */
    }

    /* 滚动条轨道 */
    &::-webkit-scrollbar-track {
        background: var(--el-fill-color-lighter);
        border-radius: 4px;
    }

    /* 滚动条滑块 */
    &::-webkit-scrollbar-thumb {
        background: var(--el-border-color);
        border-radius: 4px;
        transition: background-color 0.2s;
    }

    /* 滚动条滑块悬停效果 */
    &::-webkit-scrollbar-thumb:hover {
        background: var(--el-border-color-light);
    }

    /* 滚动条角落 */
    &::-webkit-scrollbar-corner {
        background: var(--el-fill-color-lighter);
    }
}

/* Firefox浏览器自定义滚动条 */
:deep(.el-textarea__inner) {
    scrollbar-width: thin;
    /* 滚动条宽度类型：auto、thin、none */
    scrollbar-color: var(--el-border-color) var(--el-fill-color-lighter);
    /* 滑块颜色 轨道颜色 */
}
</style>