<template>
    <WorkflowNode v-bind="$props">
        <template #properties>
            <SelectProperty label="文件格式" v-model="data.params.format"
                :options="[{ label: 'json', value: 'json' }, { label: 'json lines', value: 'jsonl' }, { label: 'yaml', value: 'yaml' }, { label: 'csv', value: 'csv' }, { label: 'txt', value: 'txt' }]"  />
            <InputWithButtonProperty label="输出目录" v-model="data.params.path"
                buttonIcon="Files" @buttonClick="handleClick" />
            <InputProperty label="保存文件名" v-model="data.params.filename" handleId="params.filename"
                handleClass="filename" />
            <BoolProperty label="清空文件夹" v-model="data.params.clear_dir" />
            <el-dialog v-model="dialogShow" title="选择数据集中的目录" width="500" append-to-body>
                <div class="file-tree">
<el-tree accordion highlight-current :expand-on-click-node="false"
                    :props="props" :load="loadNode" lazy
                    @node-click="handleNodeClick" />
                </div>
            </el-dialog>
        </template>
    </WorkflowNode>
</template>

<script>
import { WorkflowNode, InputProperty, SelectProperty, InputWithButtonProperty, BoolProperty } from './base/WorkflowNode.mjs';

/**
 * 图像文件输出节点组件
 * 用于配置和展示图像输出相关参数
 */
export default {
    components: {
        WorkflowNode,
        InputProperty,
        SelectProperty,
        InputWithButtonProperty,
        BoolProperty
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
    data() {
        return {
            dialogShow: false,
            props: {
                children: 'children',
                label: 'name',
                isLeaf: 'leaf',
            },
        }
    },
    methods: {
        async loadDatasets() {
            // 调用API获取数据集数据
            let datasets = [];
            try {
                const response = await fetch('/datasets');
                const data = await response.json();

                for (const item of data) {
                    datasets.push({
                        id: item.id,
                        name: item.name,
                        leaf: false,
                        path: 'datasets/' + item.id,
                    });
                }

            } catch (error) {
                console.error('获取数据集数据失败:', error);
            }
            return datasets;
        },
        async loadPath(datasetId) {
            // 调用API获取目录/文件数据
            try {
                const response = await fetch(`/datasets/${datasetId}/files`);
                const data = await response.json();
                const fileTree = data.children;
                // 递归修改所有树结构数据的路径，并且只保留目录类型
                const filteredTree = this.recursivelyUpdatePaths(fileTree, datasetId);

                return filteredTree;
            } catch (error) {
                console.error('获取目录/文件数据失败:', error);
            }
            return [];
        },

        /**
         * 递归更新树结构中所有节点的路径，并只保留目录类型的节点
         * @param {Array} data - 树结构数据数组
         * @param {string} datasetId - 数据集ID
         * @returns {Array} 过滤后的目录树结构
         */
        recursivelyUpdatePaths(data, datasetId) {
            if (!Array.isArray(data)) return [];

            // 过滤出目录类型的节点
            const filteredData = data.filter(item => item.type === 'directory');

            for (const item of filteredData) {
                item.path = 'datasets/' + datasetId + '/' + item.path;
                item.leaf = false; // 目录节点永远不是叶子节点
                // 如果有子节点，递归处理并只保留目录类型
                if (item.children && Array.isArray(item.children)) {
                    item.children = this.recursivelyUpdatePaths(item.children, datasetId);
                }
            }

            return filteredData;
        },

        handleClick() {
            this.dialogShow = true;
        },

        async loadNode(node, resolve, reject) {
            if (node.level === 0) {
                try {
                    const datasets = await this.loadDatasets();
                    if (datasets.length === 0) {
                        reject('获取数据集数据失败');
                    }
                    resolve(datasets);
                } catch (error) {
                    reject('获取数据集数据失败: ' + error.message);
                }
            } else if (node.level === 1) {
                try {
                    const fileTree = await this.loadPath(node.data.id);
                    if (fileTree.length === 0) {
                        reject('获取目录/文件数据失败');
                    }
                    resolve(fileTree);
                } catch (error) {
                    reject('获取目录/文件数据失败: ' + error.message);
                }
            } else {
                resolve(node.data.children);
            }
        },
        /**
         * 处理节点点击事件，选择目录
         * @param {Object} data - 节点数据
         */
        handleNodeClick(data) {
            // 由于已经过滤掉了非目录类型，这里可以直接设置路径
            this.data.params.path = data.path;
            this.dialogShow = false;
        },
    }
};
</script>
<style scoped>
.file-tree {
  height: 500px;
  overflow-y: scroll;
  flex: 1;
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  padding: 10px;
}
</style>
