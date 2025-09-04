<template>
    <div style="width: 100%; height: calc(100vh - 120px); display: flex; flex-direction: column;">
        <!-- 标题栏 -->
        <div class="header-bar">
            <div style="display: inline-flex;align-items:center;gap: 10px;">
                <span class="title">{{ workflow?.name }}</span>
                <el-popover placement="bottom" trigger="click" width="300px" popper-class="workflow-edit-popover">
                    <template #reference>
                        <el-icon>
                            <Edit />
                        </el-icon>
                    </template>
                    <el-form size="small">
                        <el-form-item label="工作流名称" prop="name" style="margin-bottom: 10px;">
                            <el-input v-model="workflow.name" placeholder="请输入工作流名称" style="width: 200px;" />
                        </el-form-item>
                        <el-form-item label="工作流描述" prop="description" style="margin-bottom: 10px;">
                            <el-input v-model="workflow.description" placeholder="请输入工作流描述" type="textarea" :rows="2"
                                style="width: 200px;" />
                        </el-form-item>
                    </el-form>
                </el-popover>
            </div>

            <div class="header-buttons">
                <el-button type="success" @click="runWorkflow()" icon="Promotion">运行</el-button>
                <el-button type="primary" @click="saveWorkflow()" :icon="SaveIcon">保存</el-button>
                <el-button type="primary" plain @click="$router.push('/workflow')">退出</el-button>
            </div>
        </div>
        <!-- 设计区 -->
        <div class="design-area">
            <div style="width: 100%; height: 100%; position: relative;">
                <div class="tips">
                    • 按Backspace键删除节点或连线<br>
                    • 拖拽连线末端(靠近节点边缘处)调整连接目标<br>
                    • 按住Shift键可以框选多个节点<br>
                    • 按住Ctrl键可以点击选择多个节点<br>
                </div>
                <VueFlow :nodes="nodes" :edges="edges" :nodeTypes="nodeTypes" :edgesUpdatable="true"
                    :snap-to-grid="true" :connect-on-click="false" @edge-update="updateConnect" @connect="newConnect"
                    @nodesChange="applyNodeChanges" class="vue-flow">
                </VueFlow>
            </div>
            <!-- 添加节点按钮和菜单 -->
            <div class="node-panel-container">
                <el-popover placement="right" trigger="click">
                    <template #reference>
                        <el-button type="primary" circle plain size="large">
                            <el-icon size="24">
                                <svg viewBox="0 0 32 32">
                                    <path fill="currentColor"
                                        d="M23.52,0a8.45,8.45,0,0,0-7.8,5.22l-.09.27H4a4,4,0,0,0-4,4v3.43H16.28l.22.4.85,1.05H0V28a4,4,0,0,0,4,4H19.86a4,4,0,0,0,4-4V17.07l1.39-.14A8.56,8.56,0,0,0,23.52,0ZM3.63,23.55a1.45,1.45,0,1,1,1.43-1.44A1.44,1.44,0,0,1,3.63,23.55Zm16.57,0a1.45,1.45,0,1,1,1.44-1.44A1.44,1.44,0,0,1,20.2,23.55ZM23.58,16A7.46,7.46,0,1,1,31,8.56,7.43,7.43,0,0,1,23.58,16Z" />
                                    <polygon fill="currentColor"
                                        points="28.66 7.58 28.66 9.96 24.8 9.96 24.8 13.86 22.43 13.86 22.43 9.96 18.57 9.96 18.57 7.58 22.43 7.58 22.43 3.68 24.8 3.68 24.8 7.58 28.66 7.58" />
                                </svg>
                            </el-icon>
                        </el-button>
                    </template>
                    <el-menu mode="vertical" collapse class="node-menu">
                        <el-menu-item index="save" @click="saveWorkflow()">保存</el-menu-item>
                        <el-menu-item-group>
                            <template #title>
                                <el-icon>
                                    <Files />
                                </el-icon>
                                <span> 输入输出</span>
                            </template>
                            <el-menu-item index="start" @click="addNode('request')">请求输入</el-menu-item>
                            <el-menu-item index="end" @click="addNode('response')">请求输出</el-menu-item>
                            <el-menu-item index="load_image" @click="addNode('load_image')">加载图像</el-menu-item>
                            <el-menu-item index="save_image" @click="addNode('save_image')">保存图像</el-menu-item>
                        </el-menu-item-group>

                        <el-menu-item-group>
                            <template #title>
                                <el-icon>
                                    <Operation />
                                </el-icon>
                                <span> 常量节点</span>
                            </template>
                            <el-menu-item index="number_const" @click="addNode('number_const')">数值常量</el-menu-item>
                            <el-menu-item index="string_const" @click="addNode('string_const')">字符串常量</el-menu-item>
                            <el-menu-item index="text_const" @click="addNode('text_const')">文本常量</el-menu-item>
                            <el-menu-item index="bool_const" @click="addNode('bool_const')">布尔常量</el-menu-item>
                        </el-menu-item-group>

                        <el-menu-item-group>
                            <template #title>
                                <el-icon>
                                    <HelpFilled />
                                </el-icon>
                                <span> 模型节点</span>
                            </template>
                            <el-sub-menu v-for="category in models" :index="category.category.id" class="node-menu">
                                <template #title>{{ category.category.name }}</template>
                                <template v-for="module in category.modules">
                                    <el-sub-menu v-if="module.infer_params && module.infer_params.ports"
                                        :index="module.id" class="node-menu" collapse-close-icon="ArrowRight"
                                        collapse-open-icon="CaretRight">
                                        <template #title>{{ module.name }}</template>
                                        <div class="menu-scroll-container">
                                            <el-tooltip v-for="value, key in module.models" effect="light"
                                                placement="right">
                                                <el-menu-item :index="key" @click="addNode('model', {
                                                    name: module.name,
                                                    params: {
                                                        module_name: module.id,
                                                        model_name: key,
                                                        model_dir: 'weights\\' + key + '\\inference',
                                                        model_params: module.infer_params?.model_params || {},
                                                        infer_params: module.infer_params?.predict_params || {},
                                                    },
                                                    inputs: module.infer_params?.ports?.inputs || [],
                                                    outputs: module.infer_params?.ports?.outputs || [],
                                                })" class="node-menu">
                                                    {{ value.name }}
                                                </el-menu-item>
                                                <template #content>
                                                    <span
                                                        style="display: inline-block; max-width: 300px; word-wrap: break-word;">{{
                                                            value?.description }}</span>
                                                </template>
                                            </el-tooltip>
                                        </div>
                                    </el-sub-menu>
                                </template>

                            </el-sub-menu>
                            <el-sub-menu index="trainModels" class="trainModels">
                                <template #title>
                                    <div>
                                        <el-icon style="color:#409efc">
                                            <TrendCharts />
                                        </el-icon>
                                        <span>本地训练模型</span>
                                    </div>
                                </template>
                                <div class="menu-scroll-container">
                                    <el-tooltip v-for="item in trains" effect="light" placement="right">
                                        <el-menu-item :index="'train_' + item.id" @click="addLocalTrainNode(item)"
                                            class="node-menu">
                                            {{ item.name }}
                                        </el-menu-item>
                                        <template #content>
                                            <span
                                                style="display: inline-block; max-width: 300px; word-wrap: break-word;">{{
                                                    item?.description }}</span>
                                        </template>
                                    </el-tooltip>
                                </div>
                            </el-sub-menu>
                        </el-menu-item-group>
                    </el-menu>
                </el-popover>
            </div>
        </div>
    </div>
</template>
<script>
const { markRaw, defineComponent } = Vue
import { VueFlow, useVueFlow } from '/libs/vue-flow/core/vue-flow-core.mjs';
import nodeTypes, { createNodeData } from '/components/nodes/nodes.mjs';

export default {
    props: ['workflowId'],
    components: {
        VueFlow,
    },
    data() {
        return {
            nodeTypes,
            nodes: [],
            edges: [],
            models: [],
            trains: [],
            workflow: {},
            SaveIcon: markRaw(defineComponent({
                template: `<svg viewBox="0 0 256 256" >
                            <path fill="currentColor"
                                d="M127.86,255.88h-101c-4.72,0-9.23-.33-13.59-2.51A22.3,22.3,0,0,1,.64,236.69,51.31,51.31,0,0,1,0,227.43Q0,127.59,0,27.72c0-3.89.07-7.78,1.32-11.54A22.6,22.6,0,0,1,22.4.55C28.1.29,33.81.25,39.48.32c6.13,0,7.91,1.78,8,7.81.06,6.73,0,13.49-.07,20.21q0,27.19,0,54.4c0,9.79.36,10.05,10,10.05q66.06,0,132.1-.06c4.41,0,8.8.19,13.18-.07,3.73-.2,5-1.68,5.31-5.37.13-1.55.07-3.1.07-4.65q0-36.15,0-72.27c0-3.36-.56-7.21,2.9-9.09,3.92-2.11,8.18-1.19,11.87,1.05a54.56,54.56,0,0,1,8.67,6.56c5.27,5,10.28,10.22,15.39,15.36,1.09,1.12,1.95,2.41,3,3.6,4.45,5.07,6.13,10.81,6.1,17.77-.23,59.83-.1,119.67-.07,179.5v6.23c0,10.85-6.19,17.67-14.9,22.81-2.73,1.62-6,1.62-9.1,1.62-10.88.06-21.75.13-32.63.13Q163.59,255.91,127.86,255.88Zm-.6-18.56v.06h83.08a31.53,31.53,0,0,0,4.65-.26,4.48,4.48,0,0,0,4.09-4,37.49,37.49,0,0,0,.26-5.41q.19-44.66.4-89.27a23,23,0,0,0-.14-3.1c-.59-5.28-2.17-6.79-7.38-6.89-3.1,0-6.2.13-9.33.13q-78.42,0-156.85-.07c-9.63,0-10.22.56-10.22,10q-.06,44.66,0,89.31a36.2,36.2,0,0,0,.3,5.41c.33,2.4,1.61,3.62,4.12,3.89,2.3.23,4.65.23,7,.23Z">
                            </path>
                            <path fill="currentColor"
                                d="M128.22.52H177.9c3.1,0,6.2-.13,9.3-.23,9.2-.3,10.55.89,10.62,9.82.06,6-.14,11.9-.14,17.87q0,20.57.07,41.14c0,1.55,0,3.1,0,4.65-.2,7.38-1.75,8.93-9.36,8.93-18.37,0-36.76-.16-55.12-.13-22,0-44,.2-66,.26a20.83,20.83,0,0,1-5.34-.65,4.76,4.76,0,0,1-3.73-4.46c-.13-2-.2-4.12-.2-6.19q0-31.45,0-62.9c0-6.89,1.41-8.34,8-8.34,2.61,0,5.18.13,7.75.16h54.36A.11.11,0,0,1,128.22.52Zm45.2,41.21c0-7.26.1-14.51,0-21.76,0-4.91-1.55-6.56-6.43-6.83S157.17,13,152.26,13c-4.39.1-5.94,1.65-6.5,6.07a18.32,18.32,0,0,0-.1,2.34c0,14-.06,27.95,0,41.93,0,4.58,1.51,6.13,6,6.3,4.91.2,9.82.26,14.73.13,5.24-.13,6.89-1.81,7-7.12C173.52,55.7,173.42,48.71,173.42,41.73Z">
                            </path>
                        </svg>`
            })),
        }
    },
    /** 组件挂载时加载工作流配置 */
    async mounted() {
        try {
            const workflowId = this.$route.params.workflowId;
            const response = await fetch('/workflows/' + workflowId);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            this.workflow = await response.json();
            this.fromObject(this.workflow.definition)
            const modelResponse = await fetch('/define/modules');
            if (!modelResponse.ok) {
                throw new Error(`HTTP error! status: ${modelResponse.status}`);
            }
            this.models = await modelResponse.json();
            const trainResponse = await fetch('/models');
            if (!trainResponse.ok) {
                throw new Error(`HTTP error! status: ${trainResponse.status}`);
            }
            this.trains = await trainResponse.json();
        } catch (error) {
            console.error('Failed to load workflow configuration:', error);
        }
    },
    setup() {
        /** 初始化vue flow相关函数 */
        const { updateEdge, addEdges, addNodes, applyNodeChanges, toObject, fromObject } = useVueFlow()
        return {
            updateEdge,
            addEdges,
            addNodes,
            applyNodeChanges,
            toObject,
            fromObject,
        }
    },
    methods: {
        newConnect(connection) {
            if (this.checkConnect(connection)) {
                this.addEdges(connection)
            }
        },
        updateConnect({ edge, connection }) {
            if (this.checkConnect(connection)) {
                this.updateEdge(edge, connection)
            }
        },
        checkConnect(connection) {
            if (connection.sourceHandle.startsWith('outputs.')
                && (connection.targetHandle.startsWith('inputs.') ||
                    connection.targetHandle.startsWith('params.'))) {
                return true
            }
            return false
        },

        /** 添加新节点 */
        addNode(type, data = {}) {
            // 创建节点数据
            const newNode = createNodeData(type, data);
            // 添加新节点到节点列表
            this.addNodes(newNode)
        },
        addLocalTrainNode(model) {
            const category = this.models.find(item => item.category.id == model.category);
            const module = category?.modules?.find(item => item.id == model.module_id);

            if (module) {
                if (!module.infer_params.ports || !module.infer_params.ports.inputs || !module.infer_params.ports.outputs) {
                    this.$message.error('模型不支持工作流，缺少输入输出端口定义')
                    return
                }
                this.addNode('model', {
                    name: model.name,
                    params: {
                        module_name: module.id,
                        model_name: model.pretrained,
                        model_dir: 'models\\' + model.id + '\\best_model\\inference',
                        model_params: module.infer_params?.model_params || {},
                        infer_params: module.infer_params?.predict_params || {},
                    },
                    inputs: module.infer_params?.ports?.inputs || [],
                    outputs: module.infer_params?.ports?.outputs || [],
                })
            }
        },
        saveWorkflow() {
            this.workflow.definition = this.toObject()
            fetch('/workflows/' + this.workflow.id, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(this.workflow)
            }).then(res => {
                if (res.ok) {
                    this.$message({ message: '工作流保存成功', type: 'success' });
                } else {
                    throw new Error('保存工作流失败');
                }
            }).catch(err => {
                this.$message({ message: err.message, type: 'error' });
            })
        },

        /**
         * 运行工作流
         */
        runWorkflow() {
            // 先保存工作流再运行
            this.workflow.definition = this.toObject()
            fetch('/workflows/' + this.workflow.id, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(this.workflow)
            }).then(res => {
                if (res.ok) {
                    this.$message({ message: '工作流保存成功', type: 'success' });
                    // 保存成功后运行工作流
                    return fetch('/workflows/' + this.workflow.id + '/run', {
                        method: 'POST'
                    });
                } else {
                    throw new Error('保存工作流失败');
                }
            }).then(res => {
                if (res.ok) {
                    this.$message({ message: '工作流已开始运行', type: 'success' });
                } else {
                    throw new Error('运行工作流失败');
                }
            }).catch(err => {
                this.$message({ message: err.message, type: 'error' });
            });
        }
    }
}
</script>
<style scoped>
/* @import '/libs/vue-flow/core/style.css'; */
/* @import '/libs/vue-flow/core/theme-default.css'; */
@import '/assets/workflow.css';

.tips {
    position: absolute;
    top: 0px;
    right: 0px;
    padding: 5px 10px;
    border-radius: 4px;
    font-size: 12px;
    color: var(--el-text-color-disabled);
}

:deep(.vue-flow .vue-flow__edge.selected .vue-flow__edge-path) {
    stroke: rgb(224, 154, 2) !important;
}

:deep(.vue-flow .vue-flow__edge.updating .vue-flow__edge-path) {
    stroke: var(--el-text-color-regular) !important;
}

:deep(.vue-flow .vue-flow__edge-path) {
    stroke: var(--el-border-color) !important;
    stroke-width: 3 !important;
}

:deep(.vue-flow__handle) {
    border: 2px solid rgba(0, 0, 0, 0.7) !important;
}

/* 节点面板容器样式 */
.node-panel-container {
    position: absolute;
    left: 5px;
    top: 50%;
    transform: translateY(-50%);
    z-index: 100;
}

/* 节点菜单样式 */
.node-menu {
    border: none;
    width: auto;
    --el-menu-item-height: 32px;
    --el-menu-sub-item-height: 32px;
}

/* 滚动菜单容器样式 */
.menu-scroll-container {
    max-height: 400px;
    /* 设置最大高度，超出部分显示滚动条 */
    overflow-y: auto;
    /* 垂直方向滚动 */
    padding: 0px;
    min-width: 250px;
}

/* 自定义滚动条样式 */
.menu-scroll-container::-webkit-scrollbar {
    width: 8px;
    /* 滚动条宽度 */
    height: 8px;
    /* 滚动条高度 */
}

.menu-scroll-container::-webkit-scrollbar-track {
    background: transparent;
    /* 滚动条轨道背景 */
}

.menu-scroll-container::-webkit-scrollbar-thumb {
    background: #a8a8a8;
    /* 滚动条滑块颜色 */
    border-radius: 4px;
    /* 滚动条滑块圆角 */
}

.menu-scroll-container::-webkit-scrollbar-thumb:hover {
    background: #888;
    /* 滚动条滑块悬停颜色 */
}

:deep(.el-menu-item-group__title) {
    white-space: nowrap;
    width: auto;
    padding-left: 0px;
}

:deep(.trainModels .el-sub-menu__title) {
    padding-left: 0px;
}

/* 节点标题颜色 */
.node-title {
    color: #303133;
}

/* 输入输出类型端口样式 */
.input-port,
.output-port {
    cursor: pointer;
    background-color: #909399;
    border: 2px solid #909399;
}

/* 参数端口样式 */
.param-port {
    background-color: #409EFF;
    border: 2px solid #409EFF;
}

/* 确保连接线不会穿过节点 */
:deep(.vue-flow__connection-path) {
    z-index: 1;
}

/* 节点可拖拽区域样式 */
:deep(.vue-flow__handle) {
    z-index: 2;
}

/* 标题栏样式 */
.header-bar {
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 20px;
}

.title {
    font-size: 18px;
    font-weight: bold;
    display: inline-flex;
    align-items: center;
    line-height: 1;
}

.header-buttons {
    display: flex;
    gap: 10px;
}

.header-buttons .el-button {
    min-width: 80px;
}

/* 设计区样式 */
.design-area {
    flex: 1;
    position: relative;
    width: 100%;
    overflow: hidden;
}

/* 工作流编辑弹窗样式 */
.workflow-edit-popover {
    padding: 10px;
    box-sizing: border-box;
}

.workflow-edit-popover .el-form {
    margin: 0;
}
</style>