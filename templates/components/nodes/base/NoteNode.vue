<template>
    <div :class="['custom-node', 'node-color', type, { 'selected': selected }]"
        :style="{ 'background-color': data.color, width: nodeWidth + 'px' }">
        <div :class="['node-header', type]">
            <div v-if="!nameEditing || fixName" class="name-bar">
                <span @click="!fixName && startEditName()" :style="!fixName && { cursor: 'text' }" class="node-name">
                    {{ data.name }}
                </span>
                <el-popover placement="right" width="320" trigger="hover" :show-after="500">
                    <template #reference>
                        <el-icon>
                            <PaletteIcon />
                        </el-icon>
                    </template>
                    <el-color-picker-panel v-model="data.color" :predefine="predefineColors" :border="false" />
                </el-popover>
            </div>

            <input v-else v-model="editingName" @blur="finishEditName" @keyup.enter="finishEditName" @click.stop
                class="name-input nodrag" ref="nameInput" />
        </div>
        <div :class="['node-content', type]">
            <el-input v-model="data.content" type="textarea" :autosize="{ minRows: 2, maxRows: 10 }" resize="none"
                class="content-input nodrag" :input-style="{ color: textColor }" />
        </div>
        <div class="node-footer nodrag" @mousedown="startResize" @touchstart="startResize">
        </div>
    </div>
</template>

<script>
import { Handle, Position } from '/libs/vue-flow/core/vue-flow-core.mjs';

export default {
    components: {
        Handle,
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
        },
        selected: {
            type: Boolean,
            default: false,
        },
    },
    data() {
        return {
            nameEditing: false,
            editingName: '',
            fixName: this.data.fixName || false,
            nodeWidth: 220, // 初始宽度
            isResizing: false,
            minWidth: 220,  // 最小宽度
            maxWidth: 500,  // 最大宽度
            predefineColors: [
                'hsl(0, 70%, 20%)',
                'hsl(36, 70%, 20%)',
                'hsl(72, 70%, 20%)',
                'hsl(108, 70%, 20%)',
                'hsl(144, 70%, 20%)',
                'hsl(180, 70%, 20%)',
                'hsl(216, 70%, 20%)',
                'hsl(252, 70%, 20%)',
                'hsl(288, 70%, 20%)',
                'hsl(324, 70%, 20%)',
                'hsl(0, 30%, 20%)',
                'hsl(36, 30%, 20%)',
                'hsl(72, 30%, 20%)',
                'hsl(108, 30%, 20%)',
                'hsl(144, 30%, 20%)',
                'hsl(180, 30%, 20%)',
                'hsl(216, 30%, 20%)',
                'hsl(252, 30%, 20%)',
                'hsl(288, 30%, 20%)',
                'hsl(324, 30%, 20%)',
            ]
        };
    },
    computed: {
        /**
         * 计算并返回根据背景色流明度确定的文本颜色
         */
        textColor() {
            return this.calculateTextColor(this.data.color);
        }
    },
    watch: {
        /**
         * 监听data.color变化，重新计算文本颜色
         */
        'data.color'() {
            // 当背景色变化时，computed属性textColor会自动重新计算
        }
    },
    setup(props) {
        return {
            Position
        };
    },
    mounted() {
        // 组件载入时，如果data中有保存的width，则使用该值
        if (this.data.width && typeof this.data.width === 'number') {
            // 确保宽度在允许的范围内
            this.nodeWidth = Math.max(this.minWidth, Math.min(this.maxWidth, this.data.width));
        }
    },

    methods: {
        /** 开始编辑节点名称 */
        startEditName() {
            // 如果名称固定则不能编辑
            if (this.fixName) {
                return;
            }
            this.nameEditing = true;
            this.editingName = this.data.name;
            // 在下一个 tick 中聚焦输入框
            this.$nextTick(() => {
                if (this.$refs.nameInput) {
                    this.$refs.nameInput.focus();
                    this.$refs.nameInput.select();
                }
            });
        },
        /** 完成编辑节点名称 */
        finishEditName() {
            if (this.editingName.trim() !== '') {
                // 通过事件通知父组件更新名称
                this.data.name = this.editingName.trim();
                this.$emit('update:name', this.editingName.trim());
            }
            this.nameEditing = false;
            this.editingName = '';
        },

        /** 开始调整节点宽度 */
        startResize(e) {
            e.preventDefault();
            e.stopPropagation();

            this.isResizing = true;
            const startX = e.clientX || e.touches[0].clientX;
            const startWidth = this.nodeWidth;

            // 添加鼠标/触摸移动和释放事件监听
            const handleMouseMove = (moveEvent) => {
                if (!this.isResizing) return;

                const currentX = moveEvent.clientX || moveEvent.touches[0].clientX;
                const widthDelta = currentX - startX;
                let newWidth = startWidth + widthDelta;

                // 限制宽度在最小和最大值之间
                newWidth = Math.max(this.minWidth, Math.min(this.maxWidth, newWidth));
                this.nodeWidth = newWidth;

                // 通知父组件宽度变化并保存到data中
                this.$emit('update:width', newWidth);
                // 保存宽度到data对象中
                this.data.width = newWidth;
            };

            const handleMouseUp = () => {
                this.isResizing = false;
                document.removeEventListener('mousemove', handleMouseMove);
                document.removeEventListener('mouseup', handleMouseUp);
                document.removeEventListener('touchmove', handleMouseMove);
                document.removeEventListener('touchend', handleMouseUp);
            };

            // 添加事件监听器
            document.addEventListener('mousemove', handleMouseMove);
            document.addEventListener('mouseup', handleMouseUp);
            document.addEventListener('touchmove', handleMouseMove);
            document.addEventListener('touchend', handleMouseUp);
        },

        /**
         * 计算相对亮度
         * @param {number} r - 红色值 (0-255)
         * @param {number} g - 绿色值 (0-255)
         * @param {number} b - 蓝色值 (0-255)
         * @returns {number} 相对亮度值 (0-1)
         */
        getRelativeLuminance(r, g, b) {
            [r, g, b] = [r, g, b].map(val => {
                val /= 255;
                return val <= 0.03928 ? val / 12.92 : Math.pow((val + 0.055) / 1.055, 2.4);
            });
            return 0.2126 * r + 0.7152 * g + 0.0722 * b;
        },

        /**
         * 根据背景色计算适合的文本颜色
         * @param {string} bgColor - 背景颜色（十六进制格式）
         * @returns {string} 文本颜色 ('#000000' 或 '#ffffff')
         */
        calculateTextColor(bgColor) {
            // 从十六进制颜色字符串中提取RGB值
            let r, g, b;

            // 检查是否为十六进制颜色格式
            if (bgColor && bgColor.startsWith('#')) {
                // 移除#号
                const hex = bgColor.slice(1);

                // 处理简写形式的十六进制颜色 (#RGB)
                if (hex.length === 3) {
                    r = parseInt(hex[0] + hex[0], 16);
                    g = parseInt(hex[1] + hex[1], 16);
                    b = parseInt(hex[2] + hex[2], 16);
                }
                // 处理完整形式的十六进制颜色 (#RRGGBB)
                else if (hex.length === 6) {
                    r = parseInt(hex.slice(0, 2), 16);
                    g = parseInt(hex.slice(2, 4), 16);
                    b = parseInt(hex.slice(4, 6), 16);
                }
            }

            // 如果无法提取有效的RGB值，默认使用黄色背景的RGB值
            if (r === undefined || g === undefined || b === undefined) {
                r = 255;
                g = 215;
                b = 0;
            }

            const luminance = this.getRelativeLuminance(r, g, b);
            return luminance > 0.5 ? '#000000' : '#ffffff';
        }
    }
};

</script>

<style scoped>
.custom-node {
    /* 设置为相对定位，作为绝对定位子元素的参考 */
    position: relative;
    border: 2px solid rgba(0, 0, 0, 0.9);
    border-radius: 6px;
    overflow: hidden;
    box-shadow: var(--el-box-shadow);
    background-color: #ffcf3d;
    /* content-box确保边框不包括在元素宽高内 */
    box-sizing: content-box;
}

.custom-node.selected {
    border: 2px solid rgb(224, 154, 2);
    box-sizing: content-box;
}

.node-header {
    padding: 8px 8px;
    font-weight: bold;
    font-size: var(--el-font-size-small);
    margin-bottom: 0px;
    display: flex;
    background-color: rgba(0, 0, 0, 0.5);
    color: white;
}

.name-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
}

.node-content {
    font-size: var(--el-font-size-extra-small);
    padding-left: 10px;
    padding-right: 10px;
    padding-top: 5px;
    margin-bottom: 20px;
    border-top: 2px dashed rgba(0, 0, 0, 0.5);
}



.name-input {
    background: transparent;
    border: none;
    color: inherit;
    font-weight: bold;
    font-size: var(--el-font-size-small);
    width: 100%;
    outline: none;
}

.content-input {
    --el-input-text-color: #000;
    --el-input-border: none;
    --el-input-hover-border: none;
    --el-input-focus-border: none;
    --el-input-transparent-border: 0 0 0 1px transparent inset;
    --el-input-border-color: transparent;
    --el-input-border-radius: var(--el-border-radius-base);
    --el-input-bg-color: transparent;
    --el-input-placeholder-color: transparent;
    --el-input-hover-border-color: transparent;
    --el-input-clear-hover-color: transparent;
    --el-input-focus-border-color: transparent;
    transition: color 0.2s ease;
}

/* 简化滚动条样式，移除上下箭头 */
.content-input::-webkit-scrollbar {
    width: 6px;
    /* 滚动条宽度 */
}

.content-input::-webkit-scrollbar-track {
    background: transparent;
    /* 滚动条轨道背景透明 */
}

.content-input::-webkit-scrollbar-thumb {
    background: rgba(0, 0, 0, 0.2);
    /* 滚动条滑块半透明黑色 */
    border-radius: 3px;
    /* 滑块圆角 */
}

.content-input::-webkit-scrollbar-thumb:hover {
    background: rgba(0, 0, 0, 0.3);
    /* 鼠标悬停时滑块颜色变深 */
}

/* Firefox 滚动条样式 */
.content-input {
    scrollbar-width: thin;
    /* 细滚动条 */
    scrollbar-color: rgba(0, 0, 0, 0.2) transparent;
    /* 滑块颜色和轨道颜色 */
}

.node-footer {
    position: absolute;
    bottom: 0;
    right: 0;
    width: 20px;
    height: 20px;
    cursor: ew-resize;
    z-index: 2;
    border-top-left-radius: 6px;
    border-bottom-right-radius: 6px;
    background: linear-gradient(-45deg,
            rgba(0, 0, 0, 0) 0%,
            rgba(0, 0, 0, 0.5) 50%,
            rgba(30, 0, 0, 0.6) 50%,
            rgba(30, 0, 0, 0.3) 70%,
            rgba(30, 0, 0, 0.1) 100%);
}
</style>