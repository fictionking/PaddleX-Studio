<template>
    <div id="modellist">
        <div class="page-header">
            <h2 class="page-header h2">模型空间</h2>
            <el-button type="primary" plain @click="showCreateDialog">创建模型</el-button>
        </div>

        <el-row :gutter="20">
            <el-col :span="24">
                <el-card class="list-card" v-for="(model, index) in models" :key="index" @click="modelTrain(model.id)">
                    <div class="listcard content">
                        <!-- 左侧内容 -->
                        <div class="listcard left-section">
                            <div class="listcard base">
                                <h3 class="listcard base h3" v-text="model.name"></h3>
                                <el-tag type="info" effect="plain" style="font-size: 14px;"
                                    v-text="model.pretrained"></el-tag>
                            </div>
                            <p class="listcard desc" v-text="model.description"></p>
                            <div class="listcard category">
                                <el-tag type="success" v-text="model.category"></el-tag>
                                <el-tag type="success" v-text="model.module_name"></el-tag>
                            </div>
                        </div>
                        <!-- 右侧内容 -->
                        <div class="listcard right-section">
                            <p class="listcard updatetime" v-text="model.update_time"></p>
                            <div class="model-status">
                                <el-tag round
                                    :type="model.status === 'aborted' ? 'danger' :model.status === 'finished' ? 'success' : model.status === 'training' ? 'warning' : model.status === 'queued' ? 'primary' : 'info'"
                                    v-text="model.status === 'aborted' ? '中止' : model.status === 'finished' ? '训练完成' : model.status === 'training' ? '训练中' : model.status === 'queued' ? '排队中' : model.status === 'config' ? '配置中' : '未知'">
                                </el-tag>
                            </div>
                            <div class="listcard actions">
                                <el-button type="text" @click.stop="handleModelDelete(model.id)">删除</el-button>
                            </div>
                        </div>
                    </div>
                </el-card>
            </el-col>
        </el-row>
    </div>
    <!-- 动态加载模型配置组件 -->
    <component :is="configComponent" v-model="dialogVisible" :models="models" @close="handleClose">
    </component>
</template>
<script type="module">

export default {
    data() {
        return {
            models: [],
            dialogVisible: false
        }
    },
    mounted() {
        this.autofresh();  // 自动刷新模型数据
    },
    computed: {
        configComponent() {
            const { defineAsyncComponent } = Vue
            return defineAsyncComponent(() => import('/components/ModelCreate.vue'));
        }
    },
    methods: {
        autofresh() {
            this.logPollingTimer = setInterval(() => {
                this.loadModels();
            }, 10000);
            this.loadModels();
        },
        loadModels() {
            if (this.dialogVisible) {
                return;
            }
            // 调用API获取模型数据（使用axios）
            axios.get('/models')
                .then(response => {
                    // 确保data为数组，避免v-for错误
                    this.models = Array.isArray(response.data) ? response.data : [];
                })
                .catch(error => {
                    console.error('获取模型数据失败:', error);
                    // 保持models为数组
                    this.models = [];
                });
        },
        handleModelDelete(modelId) {
            this.$confirm('确定要删除该模型吗？', '提示', {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning'
            }).then(() => {
                axios.get(`/models/${modelId}/delete`)
                    .then(response => {
                        if (response.data.code === 200) {
                            this.loadModels();  // 删除成功后刷新模型列表
                            this.$message.success('删除成功');
                        } else {
                            this.$message.error(response.data.message);
                        }
                    })
                    .catch(error => {
                        this.$message.error('删除失败');
                        console.error(error);
                    });
            }).catch(() => {
                this.$message.info('已取消删除');
            });
        },
        modelTrain(modelId) {
            // 跳转到模型详情路由
            this.$router.push(`/model/detail/${modelId}`);
        },
        showCreateDialog() {
            this.dialogVisible = true;
        },
        handleClose() {
            this.dialogVisible = false;
            this.loadModels();
        }
    }
}
</script>
