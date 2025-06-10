<template>
    <div>
        <div class="page-header">
            <div class="page-header-info">
                <h2 class="page-header h2" v-text="currentModel.name"></h2>
                <el-tag type="info" effect="plain" style="font-size: 14px;" v-text="currentModel.pretrained"></el-tag>
                <el-tag type="success" v-text="currentModel.category"></el-tag>
                <el-tag type="success" v-text="currentModel.module_name"></el-tag>
            </div>
            <el-button type="primary" plain @click="handleBack">返回</el-button>
        </div>
        <p class="model-desc" v-text="currentModel.description"></p>
        <br>
        <!-- 动态加载模型配置组件 -->
        <component v-if="showConfigComponent" :is="configComponent" :current-model="currentModel">
        </component>
    </div>
</template>


<script type="module">

export default {
    props: ['modelId'],
    emits: [],
    data() {
        return {
            currentModel: {},
            showConfigComponent: true
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
            const { defineAsyncComponent } = Vue
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
        handleBack() {
            this.showConfigComponent = false;
            this.$nextTick(() => {
                this.$router.push('/model');
            });
        }
    }
}
</script>