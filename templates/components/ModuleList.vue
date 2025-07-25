<template>
  <div class="model-definitions-container">
    <!-- 分类选择 -->
    <div class="category-tabs">
      <div v-for="(category, index) in categories" :key="category.id"
        :class="['category-tab', { active: activeCategoryIndex === index }]" @click="activeCategoryIndex = index">
        {{ category.name }}
      </div>
    </div>

    <!-- 模型类型卡片网格 -->
    <div class="module-types-grid">
      <div v-for="moduleType in filteredModules" :key="moduleType.id" class="module-type-card"
        @click="selectModuleType(moduleType)">
        <div class="module-type-header">
          <h3>{{ moduleType.name }}</h3>
          <div class="module-type-badge">{{ Object.keys(moduleType.models).length }}个预训练模型</div>
        </div>
        <el-carousel v-if="Array.isArray(moduleType.description)" height="auto" autoplay arrow="never"  indicator-position="outside">
          <el-carousel-item v-for="item in moduleType.description" :key="item" style="height: auto;">
            <p class="module-type-description" v-html="item || '无描述信息'"></p>
          </el-carousel-item>
        </el-carousel>
        <p v-if="typeof moduleType.description === 'string'" class="module-type-description" v-html="moduleType.description || '无描述信息'"></p>
        <div class="module-type-footer">
          <span class="arrow-icon">→</span>
        </div>
      </div>
    </div>

    <!-- 预训练模型模态框 -->
    <div v-if="selectedModule" class="modal-overlay">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ selectedModule.name }} - 预训练模型</h3>
          <button class="close-btn" @click="selectedModule = null">×</button>
        </div>
        <el-scrollbar max-height="70vh">
          <div class="models-grid">
            <div v-for="model in selectedModule.models" :key="model.name" class="model-card">
              <div class="model-card-header">
                <h4 style="word-break: break-all;">{{ model.name }}</h4>
                <div class="model-card-metrics">
                  <el-rate v-model="model.rate" size="small" clearable @change="handleRateChange(model.name, $event)" />
                  <span v-if="model.model_size">{{ model.model_size }}</span>
                </div>
              </div>
              <div class="model-card-body">
                <p v-if="model.description">{{ model.description }}</p>
              </div>
              <div class="model-card-footer"
                style="display: flex; justify-content: space-between; align-items: center;">
                <el-button type="primary" round text @click="handleUpdateModel(model)">
                  缓存模型
                  <el-icon v-if="cachedModels.includes(model.name)" style="color:#00c58d;">
                    <SuccessFilled />
                  </el-icon>
                </el-button>
                <div>
                  <el-button v-if="selectedModule.is_trainable" type="primary" round text
                    @click="openCreateModelDialog(model)">训练</el-button>
                  <el-button type="primary" round text @click="openCreateAppDialog(model)">应用</el-button>
                </div>
              </div>
            </div>
          </div>
        </el-scrollbar>
      </div>
    </div>

    <!-- 新增模型创建对话框 -->
    <el-dialog v-model="showCreateTrainDialog" title="训练模型" width="600px">
      <div style="margin-bottom: 20px;">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item>{{ newModelFormData.category }}</el-breadcrumb-item>
          <el-breadcrumb-item>{{ newModelFormData.module_name }}</el-breadcrumb-item>
          <el-breadcrumb-item>{{ newModelFormData.pretrained }}</el-breadcrumb-item>
        </el-breadcrumb>
      </div>

      <el-form ref="modelForm" :model="newModelFormData" :rules="formRules" label-width="100px">
        <el-form-item label="名称" prop="name">
          <el-input v-model="newModelFormData.name" placeholder="请输入模型名称"></el-input>
        </el-form-item>
        <el-form-item label="唯一标识" prop="id">
          <el-input v-model="newModelFormData.id" placeholder="请输入唯一标识"></el-input>
        </el-form-item>
        <el-form-item label="描述">
          <el-input type="textarea" v-model="newModelFormData.description" placeholder="请输入描述信息"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="showCreateTrainDialog = false">取消</el-button>
        <el-button type="primary" @click="submitModelForm">确定</el-button>
      </div>
    </el-dialog>

    <!-- 新增应用创建对话框 -->
    <el-dialog v-model="showCreateAppDialog" title="模型应用" width="600px">
      <div style="margin-bottom: 20px;">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item>{{ newAppFormData.category }}</el-breadcrumb-item>
          <el-breadcrumb-item>{{ newAppFormData.module_name }}</el-breadcrumb-item>
          <el-breadcrumb-item>{{ newAppFormData.pretrained }}</el-breadcrumb-item>
        </el-breadcrumb>
      </div>
      <div v-if="newAppFormData.tip" style="margin-bottom:20px;">
        {{ newAppFormData.tip }}
      </div>
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

    <!-- 下载进度对话框 -->
    <el-dialog title="模型更新" v-model="updateDialogVisible" width="600px" align-center :close-on-click-modal="false"
      @close="cancelUpdate">
      <div class="progress-container">
        <el-progress :percentage="downloadProgress" :stroke-width="10" striped striped-flow
          :duration="10"></el-progress>
        <p class="progress-text">{{ progressText }}</p>
        <p class="progress-text">{{ speedText }}</p>
      </div>
    </el-dialog>

  </div>
</template>

<script>
export default {
  data() {
    return {
      definitions: [],
      cachedModels: [],
      activeCategoryIndex: 0,
      selectedModule: null,
      showCreateTrainDialog: false,
      showCreateAppDialog: false,
      newModelFormData: {
        name: '',
        id: '',
        description: '',
        category: '',
        module_id: '',
        module_name: '',
        dataset_type: '',
        pretrained: ''
      },
      newAppFormData: {
        name: '',
        id: '',
        category_id: '',
        module_id: '',
        module_name: '',
        pretrained: '',
      },
      formRules: {
        name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
        id: [{ required: true, message: '请输入唯一标识', trigger: 'blur' }]
      },
      // 更新模型相关数据
      updateDialogVisible: false,
      downloadProgress: 0,
      progressText: '',
      speedText: ''
    };
  },
  components: {
    SuccessFilled: ElementPlusIconsVue.SuccessFilled
  },
  computed: {
    categories() {
      return this.definitions.map(item => item.category);
    },
    filteredModules() {
      if (this.definitions.length === 0) return [];
      return this.definitions[this.activeCategoryIndex].modules;
    }
  },
  mounted() {
    this.fetchModelDefinitions();
    this.fetchCachedModels();
  },
  methods: {
    async fetchModelDefinitions() {
      try {
        const response = await axios.get('/define/modules');
        this.definitions = response.data;
      } catch (error) {
        console.error('获取模型定义失败:', error);
        this.$notify.error({
          title: '错误',
          message: '获取模型定义失败，请刷新页面重试'
        });
      }
    },
    async fetchCachedModels() {
      try {
        const response = await axios.get('/define/modules/cached');
        this.cachedModels = response.data;
      } catch (error) {
        console.error('获取模型缓存状态失败:', error);
        this.$notify.error({
          title: '错误',
          message: '获取模型缓存状态失败，请刷新页面重试'
        });
      }
    },
    selectModuleType(modelType) {
      this.selectedModule = modelType;
    },
    formatMetrics(metrics) {
      return Object.entries(metrics)
        .map(([key, value]) => `${key}: ${value.toFixed(4)}`)
        .join(' | ');
    },
    /**
     * 打开创建模型对话框并初始化数据
     * @param {Object} model - 选中的预训练模型
     */
    openCreateModelDialog(model) {
      let categoryid = this.definitions[this.activeCategoryIndex].category.id
      this.newModelFormData = {
        name: '',
        id: '',
        description: '',
        category: categoryid,
        module_id: this.selectedModule.id,
        module_name: this.selectedModule.name,
        dataset_type: this.selectedModule.dataset_type,
        pretrained: model.name
      };
      this.showCreateTrainDialog = true;
    },
    /**
     * 打开创建应用对话框并初始化数据
     * @param {Object} model - 选中的预训练模型
     */
    openCreateAppDialog(model) {
      let categoryid = this.definitions[this.activeCategoryIndex].category.id
      this.newAppFormData = {
        name: '',
        id: '',
        category: categoryid,
        module_id: this.selectedModule.id,
        module_name: this.selectedModule.name,
        pretrained: model.name
      };
      if (categoryid === 'TimeSeries') {
        this.newAppFormData.tip = '💡此应用只能使用官方示例数据，自定义数据需要使用自训练模型。'
      }
      this.showCreateAppDialog = true;
    },
    /**
     * 提交模型表单数据到后端
     */
    async submitModelForm() {
      this.$refs.modelForm.validate(async (valid) => {
        if (valid) {
          try {
            await axios.post('/models/new', this.newModelFormData);
            this.$message.success('模型创建成功');
            this.showCreateTrainDialog = false;
            this.$router.push(`/model/${this.newModelFormData.id}`);
          } catch (error) {
            this.$message.error('模型创建失败:' + error.response.data.message);
          }
        }
      });
    },
    /**
     * 提交应用表单数据到后端
     */
    async submitAppForm() {
      this.$refs.appForm.validate(async (valid) => {
        if (valid) {
          try {
            await axios.post('/define/module/createapp', this.newAppFormData);
            this.$message.success('应用创建成功');
            this.showCreateAppDialog = false;
            this.$router.push(`/app/${this.newAppFormData.id}`);
          } catch (error) {
            this.$message.error('应用创建失败:' + error.response.data.message);
          }
        }
      });
    },
    /**
     * 处理模型更新功能
     * @param {Object} model - 要更新的模型对象
     */
    handleUpdateModel(model) {
      this.updateDialogVisible = true;
      this.downloadProgress = 0;
      this.progressText = '准备开始下载...';
      this.speedText = '';
      // 获取当前分类ID
      const categoryId = this.definitions[this.activeCategoryIndex].category.id;
      const eventSource = new EventSource(`/define/module/${categoryId}/${this.selectedModule.id}/${model.name}/cacheModel`);

      eventSource.onmessage = (event) => {
        // 忽略心跳包空数据
        if (!event.data.trim()) return;

        const data = JSON.parse(event.data);
        // 处理下载中状态（后端返回'downloading'而非'progress'）
        if (data.status === 'downloading') {
          this.downloadProgress = data.progress;
          this.progressText = `正在下载${data.type}模型: ${data.file}`;
          this.speedText = '下载速度:' + data.speed + '  剩余时间:' + data.remain_time;
        }
        // 处理开始下载状态
        else if (data.status === 'starting') {
          this.progressText = `开始下载${data.type}模型: ${data.file}`;
          this.speedText = '';
        }
        // 处理解压完成状态
        else if (data.status === 'extracted') {
          this.progressText = `${data.model_type}模型解压完成: ${data.filename}`;
          this.speedText = '';
        }
        // 处理单个文件下载完成状态
        else if (data.status === 'completed') {
          this.progressText = `${data.type}模型下载完成`;
          this.speedText = '';
        }
        // 处理所有文件下载完成状态
        else if (data.status === 'all_completed') {
          this.downloadProgress = 100;
          this.progressText = '所有模型更新完成';
          this.speedText = '';
          eventSource.close();
          this.fetchCachedModels();
          setTimeout(() => {
            this.updateDialogVisible = false;
            this.$message.success('模型更新成功');
          }, 1000);
        }
        // 处理错误状态（后端返回'failed'而非'error'）
        else if (data.status === 'failed') {
          eventSource.close();
          this.$message.error(`下载失败: ${data.error}`);
          this.updateDialogVisible = false;
        }
      };

      eventSource.onerror = () => {
        eventSource.close();
        this.$message.error('连接服务器失败');
        this.updateDialogVisible = false;
      };
    },
    /**
     * 取消模型更新
     */
    cancelUpdate() {
      fetch(`/define/module/cacheModel/cancel`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      })
    },
    handleRateChange(modelName, rate) {
      const categoryId = this.definitions[this.activeCategoryIndex].category.id;
      axios.post('/define/module/setModelRate', {
        category_id: categoryId,
        module_id: this.selectedModule.id,
        model_name: modelName,
        rate: rate
      }).then(res => {
        this.$message.success('设置评分成功');
      })
    }
  }
}
</script>

<style scoped>
.model-definitions-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.category-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
  overflow-x: auto;
  padding-bottom: 10px;
}

.category-tab {
  padding: 10px 20px;
  background-color: var(--el-fill-color);
  border-radius: 20px;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.3s ease;
}

.category-tab.active {
  background-color: var(--el-color-primary);
  color: var(--el-color-white);
  font-weight: bold;
}

.module-types-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.module-type-card {
  background: var(--el-fill-color-light);
  border: 1px solid var(--el-fill-color);
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  padding: 20px;
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  display: flex;
  flex-direction: column;
}

.module-type-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
}

.module-type-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.module-type-header h3 {
  margin: 0;
  font-size: 18px;
}

.module-type-badge {
  background-color: var(--el-color-success-light-9);
  color: var(--el-color-success);
  border: 1px solid var(--el-color-success-light-5);
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 12px;
}

.module-type-description {
  color: var(--el-color-info-dark-2);
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 20px;
  overflow: hidden;
  text-overflow: ellipsis;
}

:deep(.module-type-description img) {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 0 auto;
}

.module-type-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: auto;
}

.arrow-icon {
  color: var(--el-color-success-light-3);
  font-size: 20px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-image: radial-gradient(transparent 1px, var(--el-bg-color) 1px);
  background-size: 4px 4px;
  backdrop-filter: saturate(50%) blur(4px);
  box-shadow: 0 0 20px rgba(0, 0, 0, 1);
  border-radius: 10px;
  width: 90%;
  max-width: 1000px;
  overflow-y: auto;
  padding: 25px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  font-size: 22px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
}

.close-btn:hover {
  color: var(--el-color-primary);
}

.models-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  padding: 20px;
}

.model-card {
  background-color: var(--el-fill-color);
  border-radius: 8px;
  padding: 15px;
  display: flex;
  flex-direction: column;
}

.model-card-header h4 {
  margin: 0 0 10px 0;
  font-size: 16px;
}

.model-card-metrics {
  font-size: 12px;
  color: var(--text-secondary-color);
  margin-bottom: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.model-card-body {
  margin-bottom: 15px;
}

.model-card-body p {
  font-size: 14px;
  color: var(--el-color-info-dark-2);
  margin-bottom: 10px;
}

.model-card-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: auto;
}

/* 进度对话框样式 */
.progress-container {
  padding: 20px 0;
}

.progress-text {
  margin-top: 10px;
  color: #606266;
  font-size: 14px;
}

@media (max-width: 768px) {

  .module-types-grid,
  .models-grid {
    grid-template-columns: 1fr;
  }
}
</style>
