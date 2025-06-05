<template>
    <div>
        <div class="page-header">
            <div class="page-header-info">
                <h2 class="page-header h2" v-text="currentModel.name"></h2>
                <el-tag type="info" effect="plain" style="font-size: 14px;" v-text="currentModel.pretrained"></el-tag>
                <el-tag type="success" v-text="currentModel.category"></el-tag>
                <el-tag type="success" v-text="currentModel.module_name"></el-tag>
            </div>
            <el-button type="primary" plain @click="$router.push('/model')">返回</el-button>
        </div>
        <p class="model-desc" v-text="currentModel.description"></p>
        <br>
        <!-- 动态加载模型配置组件 -->
        <component :is="configComponent" :current-model="currentModel"
           @check-ds="handleCheckDataset" @copy-ds="handleCopyDS">
        </component>

    </div>
</template>


<script type="module">

export default {
    props: ['modelId'],
    emits: [],
    data() {
        return {
            currentModel: {}
        }
    },
    async created() {
        try {
            const modelId = this.$route.params.modelId; // 从路由参数获取modelId
            if (!modelId) {
                this.$message.error('模型ID未获取到');
                return;
            }
            const response = await axios.get(`/models/${modelId}`);
            if (response.status === 200) {
                this.currentModel = response.data;
            } else {
                this.$message.error('获取模型详情失败：' + response.data.message);
            }
        } catch (error) {
            this.$message.error('网络请求失败：' + error.message);
        }
    },
    computed: {
        // 导入Vue的defineAsyncComponent用于异步组件加载
        configComponent() {
            const {defineAsyncComponent } = Vue
            // 检查currentModel是否已加载module_id
            if (!this.currentModel.module_id) {
                // 未加载时返回空组件或加载提示（可选）
                return null; 
            }
            // 数据加载完成后，使用defineAsyncComponent动态导入目标组件
            return defineAsyncComponent(() => import(`/components/model/${this.currentModel.module_id}.vue`));
        }

    },
    methods: {
        async handleCheckDataset() {
            if (this.modelConfig.processing) return;
            this.modelConfig.processing = true;
            this.modelConfig.checkPass = false;
            await this.$nextTick();
            try {
                const response = await axios.post(`/models/${this.currentModel.id}/check`, {
                    dataset_id: this.currentModel.dataset_id
                });
                if (response.data.code === 200) {
                    this.modelConfig.checkResult = response.data.data;
                    this.modelConfig.checkPass = this.modelConfig.checkResult.check_pass;
                }
                this.modelConfig.showCheckResult = true;
                if (!this.checkPass) {
                    try {
                        const logResponse = await axios.get(`/models/${this.currentModel.id}/check/check_dataset.log`);
                        this.modelConfig.checkLog = logResponse.data;
                    } catch (error) {
                        this.$message.error('获取日志失败：' + error.message);
                    }
                }
            } catch (error) {
                this.$message.error('网络请求失败：' + error.message);
            } finally {
                this.modelConfig.processing = false;
            }

        },
        async handleCopyDS() {
            if (this.modelConfig.processing || !this.modelConfig.checkPass) return;
            this.modelConfig.processing = true;
            await this.$nextTick();
            try {
                const response = await axios.post(`/models/${this.currentModel.id}/copyds`, {
                    dataset_id: this.currentModel.dataset_id
                });
                if (response.data.code === 200) {
                    this.currentModel = response.data.data;
                } else {
                    this.$message.error('数据集复制失败：' + response.data.message);
                }
            } catch (error) {
                this.$message.error('网络请求失败：' + error.message);
            } finally {
                this.modelConfig.processing = false;
            }

        }
    }
}
</script>