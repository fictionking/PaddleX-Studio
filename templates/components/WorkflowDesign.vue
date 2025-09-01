<template>
    <div style="width: 100%; height: calc(100vh - 120px); position: relative;">
        <div class="tips">
            • 按Backspace键删除节点或连线<br>
            • 拖拽连线末端(靠近节点边缘处)调整连接目标<br>
            • 按住Shift键可以框选多个节点<br>
            • 按住Ctrl键可以点击选择多个节点<br>
        </div>
        <VueFlow :nodes="nodes" :edges="edges" :nodeTypes="nodeTypes" :edgesUpdatable="true" :snap-to-grid="true"
            :connect-on-click="false" @edge-update="updateConnect" @connect="newConnect" @nodesChange="nodesChange"
            class="vue-flow">
        </VueFlow>
    </div>
    <!-- 添加节点按钮和菜单 -->
    <div class="node-panel-container">
        <el-popover placement="right" trigger="click">
            <template #reference>
                <el-button type="primary" icon="Plus" circle size="medium" >
                </el-button>
            </template>
            <el-menu mode="vertical" class="node-menu">
                <el-menu-item-group title="基础节点">
                    <el-menu-item @click="addNode('start', '')">开始节点</el-menu-item>
                    <el-menu-item @click="addNode('end', '')">结束节点</el-menu-item>
                    <el-menu-item @click="addNode('load_image', '')">加载图像</el-menu-item>
                    <el-menu-item @click="addNode('save_image', '')">保存图像</el-menu-item>
                </el-menu-item-group>

                <el-menu-item-group title="常量节点">
                    <el-menu-item @click="addNode('number_const', '')">数值常量</el-menu-item>
                    <el-menu-item @click="addNode('string_const', '')">字符串常量</el-menu-item>
                </el-menu-item-group>

                <el-menu-item-group title="模型节点">
                    <el-menu-item @click="addNode('model', 'object_detection')">目标识别</el-menu-item>
                    <el-menu-item @click="addNode('model', 'image_classification')">图像分类</el-menu-item>
                </el-menu-item-group>
            </el-menu>
        </el-popover>
    </div>
</template>
<script>
import { VueFlow, useVueFlow } from '/libs/vue-flow/core/vue-flow-core.mjs';
import nodeTypes, { createNodeData } from '/components/nodes/nodes.mjs';

export default {
    components: {
        VueFlow,
    },
    data() {
        return {
            nodeTypes,
            nodes: [],
            edges: []
        }
    },
    /** 组件挂载时加载工作流配置 */
    async mounted() {
        try {
            // 从服务端加载工作流配置JSON文件
            const response = await fetch('/assets/workflow_config.json');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const config = await response.json();
            this.nodes = config.nodes || [];
            this.edges = config.edges || [];
        } catch (error) {
            console.error('Failed to load workflow configuration:', error);
        }
    },
    setup() {
        /** 初始化vue flow相关函数 */
        const { updateEdge, addEdges } = useVueFlow()
        return {
            updateEdge,
            addEdges,
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
        nodesChange(nodeChange) {
            nodeChange.forEach(event => {
                if (event.type === 'position') {
                    if (!event.dragging) {
                        return
                    }
                    // 查找对应的节点并更新其位置属性
                    const node = this.nodes.find(n => n.id === event.id);
                    if (node && node.data) {
                        // 使用 event.position 获取节点的新位置
                        node.position.x = event.position.x;
                        node.position.y = event.position.y;
                    }
                }
            });
        },

        /** 添加新节点 */
        addNode(type, subtype = '') {
            // 创建节点数据
            const newNode = createNodeData(type, subtype);

            // 添加新节点到节点列表
            this.nodes.push(newNode);
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
    left: 0px;
    top: 50%;
    transform: translateY(-50%);
    z-index: 100;
}

/* 节点菜单样式 */
.node-menu {
    border: none;
    --el-menu-item-height: 32px;
}

</style>