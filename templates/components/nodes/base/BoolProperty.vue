<template>
    <div class="property-item">
        <Handle v-if="handleId" type="target" :position="Position.Left" :id="handleId"
            :class="['left-handle-pos', 'params-port', handleClass]" />
        <span class="property-label">{{ label }}:</span>
        <el-switch :active-text="trueLabel" :inactive-text="falseLabel" v-model="internalValue" class="property-value input nodrag"
            size="small" @change="updateValue" />
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
            type: Boolean,
            required: true,
            description: '开关绑定的值'
        },
        trueLabel: {
            type: String,
            default: 'True',
            description: '开关开启时的标签'
        },
        falseLabel: {
            type: String,
            default: 'False',
            description: '开关关闭时的标签'
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
    align-items: center;
}

.property-label {
    min-width: 50px;
    margin-right: 8px;
    line-height: 1;
}
:deep(.el-switch--small) {
    font-size: 10px;
    height: 16px;
    line-height: 16px;
}
:deep(.el-switch--small .el-switch__label) {
    font-size: 10px;
}
 
:deep(.el-switch--small .el-switch__label *) {
    font-size: 10px;
}
:deep(.el-switch__label) {
    color: var(--el-text-color-secondary);
}
.left-handle-pos {
    position: absolute;
    left: -10px;
}
</style>