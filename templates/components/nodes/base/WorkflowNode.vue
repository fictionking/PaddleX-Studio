<template>
    <div :class="['custom-node', 'node-color', type, { 'selected': selected }]"
        :style="{ 'background-color': data.color }">
        <div :class="['node-header', type]">
            <div v-if="!nameEditing || fixName" class="name-bar">
                <span @click="!fixName && startEditName()" :style="!fixName && { cursor: 'text' }" class="node-name">
                    {{ data.name }}
                </span>
                <el-popover placement="right" width="320" trigger="hover">
                    <template #reference>
                        <el-icon>
                            <svg xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg"
                                viewBox="0 0 256 256">
                                    <defs>
                                        <linearGradient gradientUnits="userSpaceOnUse" x1="114.7" id="g1" x2="917.19"
                                            y2="491.24" y1="491.24">
                                            <stop stop-color="#fff" offset="0"></stop>
                                            <stop stop-opacity="0" stop-color="#fff" offset="1"></stop>
                                        </linearGradient>
                                    </defs>
                                    <g transform="matrix(0.31212232,0,0,0.31212232,-31.806642,-31.808307)">
                                        <g>
                                            <path style="fill: #f4ce8c; stroke: #5a2714; stroke-linecap: round; stroke-linejoin: round; stroke-width: 10px;"
                                                d="M896.33,406.6C840.66,235.27,621.7,152.86,407.26,222.53s-343.15,265-287.48,436.38a268.49,268.49,0,0,0,61.51,102.52,8.69,8.69,0,0,0,13.79-1.68c10.55-18,25.75-35.62,44.91-50.77,55.75-44.07,123.92-50.74,152.25-14.9s6.1,100.62-49.65,144.7l-.14.11a8.71,8.71,0,0,0,3.19,15.3c79.94,20.55,172,18.43,263.21-11.21C823.29,773.31,952,577.93,896.33,406.6ZM478.18,648.44c-45.68,0-82.72-27.33-82.72-61s37-61,82.72-61,82.73,27.32,82.73,61S523.87,648.44,478.18,648.44Z">
                                            </path>
                                            <path style="fill: url(#g1); stroke: #5a2714; stroke-linecap: round; stroke-linejoin: round; stroke-width: 10px;"
                                                d="M904.22,365.08C848.55,193.75,629.59,111.34,415.15,181S72,446.06,127.67,617.39a268.49,268.49,0,0,0,61.51,102.52A8.69,8.69,0,0,0,203,718.23c10.55-18,25.75-35.62,44.91-50.77,55.75-44.07,123.92-50.74,152.25-14.9s6.1,100.62-49.65,144.7l-.14.11a8.71,8.71,0,0,0,3.19,15.3c79.94,20.55,172,18.43,263.21-11.21C831.18,731.79,959.89,536.41,904.22,365.08ZM486.07,606.92c-45.68,0-82.72-27.33-82.72-61s37-61,82.72-61,82.73,27.32,82.73,61S531.76,606.92,486.07,606.92Z">
                                            </path>
                                            <circle style="fill: #ed7373; stroke: #5a2714; stroke-linecap: round; stroke-linejoin: round; stroke-width: 10px;" cx="233.08" cy="507.35" r="68.94"></circle>
                                            <ellipse style="fill: #5dc5f0; stroke: #5a2714; stroke-linecap: round; stroke-linejoin: round; stroke-width: 10px;" rx="89.23" cx="442.56" ry="68.94" cy="356.33"></ellipse>
                                            <ellipse style="fill: #5dc5f0; stroke: #5a2714; stroke-linecap: round; stroke-linejoin: round; stroke-width: 10px;" rx="72.38" cx="738.22" ry="55.92" cy="594.29"></ellipse>
                                            <ellipse style="fill: #5dc5f0; stroke: #5a2714; stroke-linecap: round; stroke-linejoin: round; stroke-width: 10px;" rx="42.51" cx="650.14" ry="32.84" cy="319.26"></ellipse>
                                            <path style="fill: #ed7373; stroke: #5a2714; stroke-linecap: round; stroke-linejoin: round; stroke-width: 10px;"
                                                d="M786.12,438.39c0,.31,0,.61,0,.91a41.38,41.38,0,0,1-82.75-.89,41.09,41.09,0,0,1,3.17-15.9,86.72,86.72,0,0,0,5.77-43,53,53,0,0,1-.33-5.94,54.22,54.22,0,1,1,85,44.51A24.79,24.79,0,0,0,786.12,438.39Z">
                                            </path>
                                        </g>
                                    </g>
                                </svg>
                        </el-icon>
                    </template>
                    <el-color-picker-panel v-model="data.color" :predefine="predefineColors" :border="false" />
                </el-popover>
            </div>

            <input v-else v-model="editingName" @blur="finishEditName" @keyup.enter="finishEditName" @click.stop
                class="name-input nodrag" ref="nameInput" />
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
            fixName: this.data.fixName || false,
            predefineColors: [
                'hsl(0, 100%, 20%)',
                'hsl(17, 50%, 20%)',
                'hsl(38, 100%, 20%)',
                'hsl(51, 100%, 15%)',
                'hsl(68, 100%, 15%)',
                'hsl(120, 50%, 15%)',
                'hsl(180, 100%, 15%)',
                'hsl(210, 100%, 20%)',
                'hsl(265, 100%, 20%)',
                'hsl(327, 100%, 20%)',
            ]
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

.name-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
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

.io-connection {
    position: relative;
    margin-bottom: 5px;
    display: flex;
    align-items: center;
}

.io-label {
    font-weight: bold;
    white-space: nowrap;
    color: #fff;
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
</style>