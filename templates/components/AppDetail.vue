<template>
  <div class="app-detail-container">
    <div class="page-header">
      <div class="page-header-info">
        <h2 class="page-header h2" v-text="appConfig.name"></h2>
        <el-tag type="info" effect="plain" style="font-size: 14px;" v-text="appConfig.id"></el-tag>
        <el-tag type="success" v-text="appConfig.type === 'module' ? '模型' : '产线'"></el-tag>
        <el-tag type="success" v-text="appConfig.category"></el-tag>
        <el-tag type="success" v-text="appConfig.module_name"></el-tag>
        <el-tag type="success" v-text="appConfig.model_name"></el-tag>
        <el-tag :class="appConfig.status === 'running' ? 'status_running' : 'status_stopped'"
          :type="appConfig.status == 'stopped' ? 'primary' : 'success'"
          v-text="appConfig.status === 'running' ? '运行中' : '未运行'"></el-tag>
      </div>
      <el-button type="primary" plain @click="$router.push('/app')">返回</el-button>
    </div>
    <div class="params-container">
      <h3>模型参数配置</h3>
      <el-form :model="formData" label-width="120px" @submit.prevent="saveConfig">
        <el-form-item v-for="(param, key) in modelParams" :key="key" :label="key">
          <el-input-number v-if="param.type === 'int' || param.type === 'float'" v-model="formData[key]"
            :step="param.type === 'float' ? 0.01 : 1" :min="param.min !== null ? param.min : undefined"
            :max="param.max !== null ? param.max : undefined" :readonly="!param.config_able"
            controls-position="right"></el-input-number>
          <el-input v-else v-model="formData[key]" :readonly="!param.config_able"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="saveConfig">保存配置</el-button>
          <el-button v-if="appConfig.status == 'stopped'" type="primary" @click.stop="handleAppStart()">启动</el-button>
          <el-button v-if="appConfig.status == 'running'" type="danger" @click.stop="handleAppStop()">停止</el-button>
        </el-form-item>
      </el-form>

      <h3>推理参数配置</h3>
      <el-form :model="predictFormData" label-width="120px">
        <el-form-item v-for="(param, key) in predict_params" :key="key" :label="key">
          <el-input-number v-if="param.type === 'int' || param.type === 'float'" v-model="predictFormData[key]"
            :step="param.type === 'float' ? 0.01 : 1" :min="param.min !== null ? param.min : undefined"
            :max="param.max !== null ? param.max : undefined" controls-position="right"></el-input-number>
          <el-input v-else v-model="predictFormData[key]"></el-input>
        </el-form-item>
      </el-form>
    </div>


  </div>
</template>

<script>
export default {
  name: 'AppDetail',
  props: ['appId'],
  data() {
    return {
      appConfig: {},
      modelParams: {},
      predict_params: {},
      input_types: [],
      result_types: [],
      formData: {},
      predictFormData: {}
    };
  },
  mounted() {
    // 页面加载时获取配置数据
    this.fetchConfig();
  },
  async created() {
  },
  methods: {
    /**
     * 从后端获取模型参数配置
     */
    async fetchConfig() {
      try {
        const response = await axios.get(`/apps/config/${this.$route.params.appId}`);
        if (response.data.status === 'success') {
          this.appConfig = response.data.data;
          this.modelParams = this.appConfig.model_params;
          this.predict_params = this.appConfig.predict_params;
          this.input_types = this.appConfig.input_types;
          this.result_types = this.appConfig.result_types;
          // 初始化表单数据
          Object.keys(this.modelParams).forEach(key => {
            this.formData[key] = this.modelParams[key].value;
          });
          Object.keys(this.predict_params).forEach(key => {
            this.predictFormData[key] = this.predict_params[key].default;
          });
        } else {
          alert('获取配置失败：' + response.data.message);
        }
      } catch (error) {
        console.error('获取配置失败:', error);
        alert('获取配置失败，请重试');
      }
    },
    /**
     * 保存模型参数配置到后端
     */
    async saveConfig() {
      try {
        await axios.post(`/apps/config/${this.$route.params.appId}`, { model_params: this.formData });
        alert('配置保存成功');
      } catch (error) {
        console.error('保存配置失败:', error);
        alert('保存配置失败，请重试');
      }
    },
    handleAppStart() {
      // 显示加载中模态框
      const loading = this.$loading({
        lock: true,
        text: '应用启动中，请稍候...',
        background: 'rgba(0, 0, 0, 0.7)'
      });
      axios.get(`/apps/start/${this.$route.params.appId}`)
        .then(response => {
          this.$message.success('应用启动成功');
          this.appConfig.status = 'running'
        })
        .catch(error => {
          this.$message.error('应用启动失败');
          console.error(error);
        })
        .finally(() => {
          loading.close();  // 无论成功失败都关闭加载框
        });
    },
    /**
     * 处理应用停止操作
     * @param {string} appId - 应用ID
     */
    handleAppStop() {
      // 显示加载中模态框
      const loading = this.$loading({
        lock: true,
        text: '应用停止中，请稍候...',
        background: 'rgba(0, 0, 0, 0.7)'
      });
      axios.get(`/apps/stop`)
        .then(response => {
          this.$message.success('应用停止成功');
          this.appConfig.status = 'stopped'
        })
        .catch(error => {
          this.$message.error('应用停止失败');
          console.error(error);
        })
        .finally(() => {
          loading.close();  // 无论成功失败都关闭加载框
        });
    }
  }
}
</script>

<style scoped>
.app-detail-container {
  padding: 20px;
}

.params-container {
  max-width: 400px;
  margin: 20px auto;
}

.disabled-hint {
  color: #999;
  margin-left: 10px;
}

.status_running {
  background-color: rgba(0, 197, 141, 0.1);
  border-color: #00c58d;
  color: #00c58d;
  font-weight: bolder;
}

.status_stopped {
  background-color: rgba(0, 91, 170, 0.1);
  border-color: #005baa;
  color: #005baa;
  font-weight: bolder;
}
</style>