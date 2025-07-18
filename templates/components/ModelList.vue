<template>
    <div id="modellist">
        <el-row :gutter="20" class="list-container">
            <el-col :span="24">
                <el-card class="list-card" v-for="(model, index) in models" :key="index"
                    @click="$router.push('/model/' + model.id)">
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
                                    :type="['aborted', 'failed'].includes(model.status) ? 'danger' : model.status === 'finished' ? 'success' : model.status === 'training' ? 'warning' : model.status === 'queued' ? 'primary' : 'info'"
                                    v-text="model.status === 'aborted' ? '中止' : model.status === 'finished' ? '训练完成' : model.status === 'training' ? '训练中' : model.status === 'queued' ? '排队中' : model.status === 'config' ? '配置中' : model.status === 'failed' ? '失败' : '未知'"></el-tag>
                            </div>
                            <div class="listcard actions">
                                <el-button type="text" @click.stop="handleModelDelete(model.id)">删除</el-button>
                                <el-button type="primary" round text
                                    @click.stop="openCreateAppDialog(model)">应用</el-button>
                            </div>
                        </div>
                    </div>
                </el-card>
            </el-col>
        </el-row>
    </div>
    <!-- 新增应用创建对话框 -->
    <el-dialog v-model="showCreateAppDialog" title="模型应用" width="600px">
        <el-form ref="appForm" :model="newAppFormData" :rules="formRules" label-width="100px">
            <el-form-item label="名称" prop="name">
                <el-input v-model="newAppFormData.name" placeholder="请输入应用名称"></el-input>
            </el-form-item>
            <el-form-item label="唯一标识" prop="id">
                <el-input v-model="newAppFormData.id" placeholder="请输入唯一标识"></el-input>
            </el-form-item>
        </el-form>
        <div slot="footer" class="dialog-footer">
            <el-button @click="showCreateAppDialog = false">取消</el-button>
            <el-button type="primary" @click="submitAppForm">确定</el-button>
        </div>
    </el-dialog>
</template>
<script type="module">

export default {
    data() {
        return {
            models: [],
            newAppFormData: {
                name: '',
                id: '',
                model_id: ''
            },
            showCreateAppDialog: false,
        }
    },
    mounted() {
        this.autofresh();  // 自动刷新模型数据
    },
    beforeUnmount() {
        // 组件卸载时清除定时器
        if (this.modelsPollingTimer) {
            clearInterval(this.modelsPollingTimer);
            this.modelsPollingTimer = null;
        }
    },
    methods: {
        autofresh() {
            this.modelsPollingTimer = setInterval(() => {
                this.loadModels();
            }, 10000);
            this.loadModels();
        },
        loadModels() {
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
                axios.delete(`/models/${modelId}`)
                    .then(response => {
                        if (response.status === 204) {
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
        /**
        * 打开创建应用对话框并初始化数据
        * @param {Object} model - 选中的预训练模型
        */
        openCreateAppDialog(model) {
            this.newAppFormData = {
                name: '',
                id: '',
                model_id: model.id
            };
            this.showCreateAppDialog = true;
        },
        /**
        * 提交应用表单数据到后端
        */
        async submitAppForm() {
            this.$refs.appForm.validate(async (valid) => {
                if (valid) {
                    try {
                        await axios.post(`/models/${this.newAppFormData.model_id}/createapp`, this.newAppFormData);
                        this.$message.success('应用创建成功');
                        this.showCreateAppDialog = false;
                        this.$router.push(`/app/${this.newAppFormData.id}`);
                    } catch (error) {
                        this.$message.error('应用创建失败:' + error.response.data.message);
                    }
                }
            });
        }
    }
}
</script>
