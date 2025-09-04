<template>
    <div class="property-item">
        <Handle
            v-if="handleId"
            :type="'target'"
            :position="Position.Left"
            :id="handleId"
            :class="['left-handle-pos', 'params-port', handleClass]"
        />
        <span class="property-label">{{ label }}:</span>
        <span class="property-value">{{ value }}</span>
    </div>
</template>

<script>
import { Handle, Position } from '/libs/vue-flow/core/vue-flow-core.mjs';

/**
 * 值属性组件
 * 用于展示纯文本值的属性项
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
        value: {
            type: [String, Number, Boolean],
            required: true,
            description: '属性值'
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
    setup() {
        return {
            Position
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
    background-color: transparent;
}

.left-handle-pos {
    position: absolute;
    left: -10px;
}
</style>