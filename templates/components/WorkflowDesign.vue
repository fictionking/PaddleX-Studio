<template>
    <div style="width: 100%; height: calc(100vh - 120px); display: flex; flex-direction: column;">
        <!-- 标题栏 -->
        <div class="header-bar">
            <div style="display: inline-flex;align-items:center;gap: 10px;">
                <span class="title">{{ workflow?.name }}</span>
                <el-popover placement="bottom" trigger="click" width="300px" popper-class="workflow-edit-popover" :persistent="false">
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
                <el-popover placement="right" trigger="click" :persistent="false">
                    <template #reference>
                        <el-button type="primary" circle plain size="large">
                            <el-icon size="24">
                                <AddNodeIcon />
                            </el-icon>
                        </el-button>
                    </template>
                    <el-button-group size="small" class="tools-row">
                        <el-tooltip content="备注" placement="top">
                            <el-button icon="Tickets" @click="addNode('note')" round />
                        </el-tooltip>
                        <el-tooltip content="分组框" placement="top">
                            <el-button icon="Files"  round />
                        </el-tooltip>
                    </el-button-group>
                    <el-menu mode="vertical" collapse class="node-menu">
                        <el-menu-item-group v-for="item in menuItems" :title="item.label">
                            <template #title>
                                <el-icon>
                                    <Grid />
                                </el-icon>
                                <span>{{ item.label }}</span>
                            </template>
                            <el-menu-item v-for="child in item.children" :index="child.type"
                                @click="addNode(child.type)">
                                {{ child.label }}
                            </el-menu-item>
                        </el-menu-item-group>

                        <el-menu-item-group>
                            <template #title>
                                <el-icon>
                                    <HelpFilled />
                                </el-icon>
                                <span>模型</span>
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
import nodeTypes, { createNodeData, menuItems, initializeNodeCounters } from '/components/nodes/nodes.mjs';

export default {
    props: ['workflowId'],
    components: {
        VueFlow,
    },
    data() {
        return {
            nodeTypes,
            menuItems,
            nodes: [],
            edges: [],
            models: [],
            trains: [],
            workflow: {},
            SaveIcon: SvgIcons.DiskIcon,
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
            // 先使用fromObject加载工作流定义到Vue Flow
            this.fromObject(this.workflow.definition);
            // 初始化节点计数器，确保新生成的ID不会与现有节点ID冲突
            initializeNodeCounters(this.workflow.definition?.nodes || []);
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
                        model_dir: 'models\\' + model.id + '\\train\\best_model\\inference',
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
    display: flex;
    gap: 6px;
    line-height: 1;
    border-bottom: 1px dashed var(--el-text-color-secondary);
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

.tools-row {
    width: 100%;
    display: flex;
    justify-content: center;
    margin: 5px 0;
}
</style>