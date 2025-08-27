<template>
    <div :class="['custom-node', 'node-color', type, { 'selected': selected }]">
        <div :class="['node-header', type]" >
            <span v-if="!nameEditing || fixName" @click="!fixName && startEditName()" :style="!fixName && { cursor: 'text' }">
            {{ data.name }}
            </span>
            <input 
                v-else 
                v-model="editingName" 
                @blur="finishEditName" 
                @keyup.enter="finishEditName"
                @click.stop
                class="name-input nodrag"
                ref="nameInput"
            />
        </div>
        <div :class="['node-content', type]">
            <div :class="['io-container', type]">
                <!-- 左侧输入连接点 -->
                <div :class="['node-inputs', type]">
                    <div v-for="input in data.inputs" :key="input" :class="['io-connection', type]">
                        <Handle :type="'target'" :position="Position.Left" :id="`inputs.${input}`"
                            :class="['left-handle-pos', 'io-port', input.toLowerCase(), type]" />
                        <span :class="['io-label', type]"> {{ input }} </span>
                    </div>
                </div>

                <!-- 右侧输出连接点 -->
                <div :class="['node-outputs', type]">
                    <div v-for="output in data.outputs" :key="output" :class="['io-connection', type]">
                        <Handle :type="'source'" :position="Position.Right" :id="`outputs.${output}`"
                            :class="['right-handle-pos', 'io-port', output.toLowerCase(), type]" />
                        <span :class="['io-label', type]"> {{ output }} </span>
                    </div>
                </div>
            </div>

            <!-- 节点中间内容 -->
            <div :class="['node-properties', type]">
                <slot name="properties"></slot>
            </div>

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
            fixName: this.data.fixName || false
        };
    },
    setup(props) {
        return {
            Position
        };
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
        }
    }
};

</script>

<style scoped>

.custom-node {
    min-width: 120px;
    max-width: 500px;
    width: fit-content;
    border: 2px solid rgba(0, 0, 0, 0.05);
    border-radius: 6px;
    overflow: hidden;
    box-shadow: var(--el-box-shadow);
    background-color: var(--el-fill-color-dark);
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

.node-content {
    font-size: var(--el-font-size-extra-small);
    padding-left: 20px;
    padding-right: 20px;
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
    background-color: transparent;
}

.property-value.input {
    --el-input-border: none;
    --el-input-border-color: transparent;
    border-width: 0;
}

.property-value.select {
    --el-border-color:transparent
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
    color: var(--el-text-color-regular);
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
</style>