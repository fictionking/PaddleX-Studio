<template>
    <div>
        <div class="page-header">
            <h2 class="page-header h2">数据集</h2>
            <el-button type="primary" plain>创建数据集</el-button>
        </div>
        <el-row :gutter="20">
            <el-col :span="24">
                <el-card class="list-card" v-for="(dataset, index) in datasets" :key="index" style="margin-bottom: 20px;">
                    <div class="listcard content">
                        <!-- 左侧内容 -->
                        <div class="listcard left-section">
                            <div class="listcard base">
                                <h3 class="listcard base h3" v-text="dataset.name"></h3>
                                <el-tag type="info" effect="plain" style="font-size: 14px;" v-text="dataset.type"></el-tag>
                                <!-- 对应model.pretrained，使用dataset.type字段 -->
                            </div>
                            <p class="listcard desc" v-text="dataset.description"></p>
                            <div class="listcard category">
                                <el-tag type="success" v-text="dataset.category"></el-tag> <!-- 保留原category标签 -->
                                <el-tag type="success" v-text="dataset.module_name"></el-tag> <!-- 新增module_name标签 -->
                            </div>
                        </div>
                        <!-- 右侧内容 -->
                        <div class="listcard right-section">
                            <p class="listcard updatetime" v-text="dataset.update_time"></p> <!-- 示例使用module_id作为右侧信息 -->
                            <div class="listcard actions">
                                <el-button type="text" size="small">删除</el-button>
                            </div>
                        </div>
                    </div>
                </el-card>
            </el-col>
        </el-row>
    </div>
</template>

<script type="module">
import axios from 'axios'

export default {
    data() {
        return {
            datasets: []  // 数据集数据列表
        }
    },
    mounted() {
        this.loadDatasets();  // 组件挂载后加载数据集数据
    },
    methods: {
        loadDatasets() {
            // 调用API获取数据集数据
            fetch('/datasets')
                .then(response => response.json())
                .then(data => {
                    this.datasets = data;
                })
                .catch(error => {
                    console.error('获取数据集数据失败:', error);
                });
        }
    }
}
</script>