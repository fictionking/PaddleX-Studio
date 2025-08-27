<template>
    <div class="property-item">
        <Handle v-if="handleId" type="target" :position="Position.Left" :id="handleId"
            :class="['left-handle-pos', 'params-port', handleClass]" />
        <span class="property-label">{{ label }}:</span>
        <el-input v-if="type === 'string'" v-model="internalValue" class="property-value input nodrag" size="small" @change="updateValue" />
        <el-input-number v-else v-model="internalValue" class="property-value input nodrag" size="small" @change="updateValue"
            :min="min" :max="max" :step="step">
            <template #decrease-icon>
                <el-icon>
                    <CaretLeft />
                </el-icon>
            </template>
            <template #increase-icon>
                <el-icon>
                    <CaretRight />
                </el-icon>
            </template>
        </el-input-number>
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
        Handle
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
        type: {
            type: String,
            default: 'string',
            description: '属性类型，支持字符串和数值类型'
        },
        min: {
            type: Number,
            default: 0,
            description: '数值类型的最小值'
        },
        max: {
            type: Number,
            default: 100,
            description: '数值类型的最大值'
        },
        step: {
            type: Number,
            default: 1,
            description: '数值类型的步长'
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
}

.property-value {
    flex: 1;
    font-size: 10px;
    max-width: 100px;
    word-break: break-all;
    --el-input-text-color: var(--el-text-color-secondary);
    --el-input-bg-color: transparent;
    background-color: transparent;
}

.property-value.input {
    --el-input-border: none;
    --el-input-border-color: transparent;
    border-width: 0;
}

.left-handle-pos {
    position: absolute;
    left: -10px;
}
</style>