<template>
    <div class="custom-node model-node">
        <div :class="['node-header', 'node-header-color', type]">
            <span>{{ data.name }}</span>
        </div>
        <div class="node-content">
            <div class="io-container">
                <!-- 左侧输入连接点 -->
                <div class="node-inputs">
                    <div v-for="input in data.inputs" :key="input" class="io-connection">
                        <Handle :type="'target'" :position="Position.Left" :id="`inputs.${input}`"
                            :class="['left-handle-pos', 'io-port', input.toLowerCase()]" />
                        <span class="io-label"> {{ input }} </span>
                    </div>
                </div>

                <!-- 右侧输出连接点 -->
                <div class="node-outputs">
                    <div v-for="output in data.outputs" :key="output" class="io-connection">
                        <Handle :type="'source'" :position="Position.Right" :id="`outputs.${output}`"
                            :class="['right-handle-pos', 'io-port', output.toLowerCase()]" />
                        <span class="io-label"> {{ output }} </span>
                    </div>
                </div>
            </div>

            <!-- 节点中间内容 -->
            <div class="node-properties">
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
        }
    },
    setup(props) {
        return {
            Position
        };
    },
};

</script>

<style scoped>

.custom-node {
    min-width: 120px;
    max-width: 500px;
    width: fit-content;
    border: 1px solid var(--el-border-color-dark);
    border-radius: 6px;
    overflow: hidden;
    background-color: var(--el-fill-color-dark);
    box-shadow: var(--el-box-shadow);
}

.node-header {
    padding: 8px 8px;
    font-weight: bold;
    font-size: var(--el-font-size-small);
    margin-bottom: 5px;
    display: flex;

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
</style>