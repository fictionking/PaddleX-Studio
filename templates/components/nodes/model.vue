<template>
    <div class="custom-node model-node">
        <div class="node-header">
            <span>{{ data.name || '目标识别节点' }}</span>
        </div>
        <div class="node-content">
            <div class="io-container">
                <!-- 左侧输入连接点 -->
                <div class="node-inputs">
                    <div v-for="input in inputs" :key="input" class="io-connection">
                        <Handle :type="'target'" :position="Position.Left" :id="`inputs.${input}`"
                            :class="['io-left-handle', 'io-port-color-' + input.toLowerCase()]" />
                        <span class="io-label"> {{ input }} </span>
                    </div>
                </div>

                <!-- 右侧输出连接点 -->
                <div class="node-outputs">
                    <div v-for="output in outputs" :key="output" class="io-connection">
                        <Handle :type="'source'" :position="Position.Right" :id="`outputs.${output}`"
                            :class="['io-right-handle', 'io-port-color-' + output.toLowerCase()]" />
                        <span class="io-label"> {{ output }} </span>
                    </div>
                </div>
            </div>

            <!-- 节点中间内容 -->
            <div class="node-properties">
                <div class="property-item">
                    <span class="property-label">模块名称:</span>
                    <span class="property-value">{{ moduleName }}</span>
                </div>
                <div class="property-item">
                    <span class="property-label">模型名称:</span>
                    <span class="property-value">{{ modelName }}</span>
                </div>
                <div v-if="data.params?.model_params" class="property-group">
                    <div class="group-label">模型参数:</div>
                    <div v-for="(value, key) in data.params.model_params" :key="key" class="property-item">
                        <Handle :type="'target'" :position="Position.Left" :id="`params.model_params.${key}`"
                            class="io-left-handle params-port-color" />

                        <span class="property-label">{{ key }}:</span>
                        <el-input v-model="data.params.model_params[key]" class="property-value-input" size="small" />
                    </div>
                </div>
                <div v-if="data.params?.infer_params" class="property-group">
                    <div class="group-label">推理参数:</div>
                    <div v-for="(value, key) in data.params.infer_params" :key="key" class="property-item">
                        <Handle :type="'target'" :position="Position.Left" :id="`params.infer_params.${key}`"
                            class="io-left-handle params-port-color" />
                        <span class="property-label">{{ key }}:</span>
                        <el-input v-model="data.params.infer_params[key]" class="property-value-input" size="small" />
                    </div>
                </div>
            </div>

        </div>
    </div>
</template>

<script>
const { defineComponent, computed } = Vue;
import { Handle, Position } from '/libs/vue-flow/core/vue-flow-core.mjs';

/**
 * 模型节点组件 - 用于Vue Flow工作流设计器
 * 显示模型参数并提供输入输出连接点
 * module_name和model_name作为固定属性显示
 * model_params和infer_params作为动态属性显示
 */
export default defineComponent({
    name: 'ModelNode',
    components: {
        Handle
    },
    props: {
        id: {
            type: String,
            required: true,
        },
        data: {
            type: Object,
            required: true,
        }
    },
    setup(props) {
        // 计算属性，获取输入、输出和参数列表
        const inputs = computed(() => props.data.inputs || ['images']);
        const outputs = computed(() => props.data.outputs || ['images', 'boxes']);
        const moduleName = computed(() => {
            // 模块名称：module_name
            const paramsObj = props.data.params || {};
            return paramsObj.module_name || '';
        });
        const modelName = computed(() => {
            // 模型名称：model_name
            const paramsObj = props.data.params || {};
            return paramsObj.model_name || '';
        });
        const modelParams = computed(() => {
            // 模型参数：model_params
            const paramsObj = props.data.params || {};
            return paramsObj.model_params || {};
        });
        const inferParams = computed(() => {
            // 推理参数：infer_params
            const paramsObj = props.data.params || {};
            return paramsObj.infer_params || {};
        });

        return {
            inputs,
            outputs,
            moduleName,
            modelName,
            modelParams,
            inferParams,
            Position
        };
    }
});
</script>

<style scoped>

.custom-node {
    min-width: 120px;
    max-width: 400px;
    width: fit-content;
    border: 1px solid var(--el-border-color-dark);
    border-radius: 6px;
    overflow: hidden;
    background-color: var(--el-fill-color-dark);
    box-shadow: var(--el-box-shadow);
}

.node-header {
    background-color: var(--el-fill-color);
    color: var(--el-text-color-primary);
    padding: 8px 8px;
    font-weight: bold;
    font-size: 12px;
    margin-bottom: 5px;
}

.node-content {
    font-size: 10px;
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
    /* min-width: 30px; */
    word-break: break-all;
}

.property-value-input {
    flex: 1;
    max-width: 100px;
    font-size: 10px;
    --el-input-border: none;
    --el-input-border-color: transparent;
    border-width: 0;
    --el-input-text-color: var(--el-text-color-secondary);
    --el-input-height: 15px;
    background-color: transparent;
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

.io-left-handle {
    position: absolute;
    left: -10px;
}

.io-right-handle {
    position: absolute;
    right: -10px;
}

.vue-flow__handle {
    border: 2px solid var(--el-border-color-extra-light);
}
</style>