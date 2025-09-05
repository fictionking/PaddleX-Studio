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
            <el-input v-model="data.content" type="textarea" :autosize="{ minRows: 2, maxRows: 10 }" resize="none" class="content-input nodrag"/>
        </div>
        <div class="node-footer">
            <div 
                class="resize-handle nodrag"
                @mousedown="startResize"
                @touchstart="startResize"
            ></div>
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
        }
    }
};

</script>

<style scoped>
.custom-node {
    border: 0px solid rgba(0, 0, 0, 0.0);
    border-radius: 6px;
    overflow: hidden;
    box-shadow: var(--el-box-shadow);
    background-color: #ffd500;
}

.custom-node.selected {
    border: 2px solid rgb(224, 154, 2);
}

.node-header {
    padding: 8px 8px;
    font-weight: bold;
    font-size: var(--el-font-size-small);
    margin-bottom: 5px;
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
    margin-bottom: 20px;
}

.node-inputs {
    min-width: 30px;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    margin-bottom: 5px;
}

.node-outputs {
    min-width: 30px;
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    margin-bottom: 5px;
}

.node-properties {
    width: 100%;
    min-width: 0;
    margin-bottom: 10px;
}

.io-connection {
    position: relative;
    margin-bottom: 5px;
    display: flex;
    align-items: center;
}

.io-label {
    font-weight: bold;
    white-space: nowrap;
    color: #ffffff;
    line-height: 1;
}

.io-container {
    display: flex;
    justify-content: space-between;
    width: 100%;
}

.property-group {
    margin-top: 0px;
}

.group-label {
    font-weight: bold;
    margin-bottom: 5px;
    color: #42b983;
}

.left-handle-pos {
    position: absolute;
    left: -10px;
}

.right-handle-pos {
    position: absolute;
    right: -10px;
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
.content-input{
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
}

/* 简化滚动条样式，移除上下箭头 */
.content-input::-webkit-scrollbar {
    width: 6px; /* 滚动条宽度 */
}

.content-input::-webkit-scrollbar-track {
    background: transparent; /* 滚动条轨道背景透明 */
}

.content-input::-webkit-scrollbar-thumb {
    background: rgba(0, 0, 0, 0.2); /* 滚动条滑块半透明黑色 */
    border-radius: 3px; /* 滑块圆角 */
}

.content-input::-webkit-scrollbar-thumb:hover {
    background: rgba(0, 0, 0, 0.3); /* 鼠标悬停时滑块颜色变深 */
}

/* Firefox 滚动条样式 */
.content-input {
    scrollbar-width: thin; /* 细滚动条 */
    scrollbar-color: rgba(0, 0, 0, 0.2) transparent; /* 滑块颜色和轨道颜色 */
}

.node-footer {
    position: relative;
    height: 20px;
}

.node-footer::before {
    content: '';
    position: absolute;
    bottom: 0;
    right: 0;
    width: 0;
    height: 0;
    border-style: solid;
    border-width: 20px 20px 0 0;
    border-color: rgba(0, 0, 0, 0.3) transparent transparent transparent;
    border-top-left-radius: 6px;
    z-index: 1;
}

/* 调整大小的句柄样式 */
.resize-handle {
    position: absolute;
    bottom: 0;
    right: 0;
    width: 20px;
    height: 20px;
    cursor: ew-resize;
    z-index: 2;
    /* 让拖拽区域覆盖整个折角 */
}
</style>