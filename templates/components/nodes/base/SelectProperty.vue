<template>
    <div class="property-item">
        <Handle
            v-if="handleId"
            type="target"
            :position="Position.Left"
            :id="handleId"
            :class="['left-handle-pos', 'params-port', handleClass]"
        />
        <span class="property-label">{{ label }}:</span>
        <el-select
            v-model="internalValue"
            class="property-value select nodrag"
            size="small"
            popper-class="select-property-dropdown"
            @change="updateValue"
        >
            <el-option
                v-for="option in options"
                :key="option.value"
                :label="option.label"
                :value="option.value"
            />
            <template #label="{ label }">
                <span style="font-size: 10px;">{{ label }}</span>
            </template>
        </el-select>
    </div>
</template>

<script>
import { Handle, Position } from '/libs/vue-flow/core/vue-flow-core.mjs';
import { ref, watch } from 'vue';

/**
 * 选择属性组件
 * 用于带有下拉选择框的属性项
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
            description: '选择框绑定的值'
        },
        options: {
            type: Array,
            required: true,
            description: '选项列表，格式为[{label: string, value: any}]'
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
        // 创建内部状态，避免直接修改props
        const internalValue = ref(props.modelValue);

        // 监听外部modelValue变化，同步到内部状态
        watch(
            () => props.modelValue,
            (newValue) => {
                internalValue.value = newValue;
            }
        );

        // 更新值的方法
        const updateValue = (value) => {
            internalValue.value = value;
            emit('update:modelValue', value);
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

.property-value {
    flex: 1;
    font-size: 10px;
    max-width: 100px;
    word-break: break-all;
    --el-input-text-color: var(--el-text-color-secondary);
    --el-input-bg-color: transparent;
    background-color: transparent;
    --el-fill-color-blank: transparent;
}

.property-value.select {
    --el-border-color: transparent;
}

.left-handle-pos {
    position: absolute;
    left: -10px;
}
.select-property-dropdown .el-select-dropdown__item {
    font-size: 10px !important;
    height: 24px !important;
    line-height: 24px !important;
    overflow: hidden;
    padding: 0 22px 0 10px !important;
}
</style>
