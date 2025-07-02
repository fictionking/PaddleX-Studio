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
    <div class="model-types-grid">
      <div v-for="modelType in filteredModelTypes" :key="modelType.id" class="model-type-card"
        @click="selectModelType(modelType)">
        <div class="model-type-header">
          <h3>{{ modelType.name }}</h3>
          <div class="model-type-badge">{{ modelType.pretrained.length }}个预训练模型</div>
        </div>
        <p class="model-type-description">{{ modelType.description || '无描述信息' }}</p>
        <div class="model-type-footer">
          <span class="arrow-icon">→</span>
        </div>
      </div>
    </div>

    <!-- 预训练模型模态框 -->
    <div v-if="selectedModelType" class="modal-overlay">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ selectedModelType.name }} - 预训练模型</h3>
          <button class="close-btn" @click="selectedModelType = null">×</button>
        </div>
        <div class="pretrained-models-grid">
          <div v-for="model in selectedModelType.pretrained" :key="model.id" class="pretrained-model-card">
            <div class="model-card-header">
              <h4>{{ model.name }}</h4>
              <div class="model-card-metrics">
                <span v-if="model.model_size">{{ model.model_size }}</span>
              </div>
            </div>
            <div class="model-card-body">
              <p v-if="model.description">{{ model.description }}</p>
            </div>
            <div class="model-card-footer">
              <el-button v-if="model.pretrained_model_url" type="primary" round text
                @click="openCreateModelDialog(model)">训练</el-button>
              <el-button type="primary" round text @click="openCreateModelDialog(model)">应用</el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 新增模型创建对话框 -->
    <el-dialog v-model="showCreateDialog" title="训练模型" width="600px">
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
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="submitModelForm">确定</el-button>
      </div>
    </el-dialog>

  </div>
</template>

<script>
export default {
  data() {
    return {
      definitions: [],
      activeCategoryIndex: 0,
      selectedModelType: null,
      showCreateDialog: false,
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
      formRules: {
        name: [{ required: true, message: '请输入模型名称', trigger: 'blur' }],
        id: [{ required: true, message: '请输入唯一标识', trigger: 'blur' }]
      }
    };
  },
  computed: {
    categories() {
      return this.definitions.map(item => item.category);
    },
    filteredModelTypes() {
      if (this.definitions.length === 0) return [];
      return this.definitions[this.activeCategoryIndex].modules;
    }
  },
  mounted() {
    this.fetchModelDefinitions();
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
    selectModelType(modelType) {
      this.selectedModelType = modelType;
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
        module_id: this.selectedModelType.id,
        module_name: this.selectedModelType.name,
        dataset_type: this.selectedModelType.dataset_type,
        pretrained: model.name
      };
      this.showCreateDialog = true;
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
            this.showCreateDialog = false;
            this.$router.push(`/model/${this.newModelFormData.id}`);
          } catch (error) {
            this.$message.error('模型创建失败:' + error.response.data.message);
          }
        }
      });
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

.model-types-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.model-type-card {
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

.model-type-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
}

.model-type-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.model-type-header h3 {
  margin: 0;
  font-size: 18px;
}

.model-type-badge {
  background-color: var(--el-color-success-light-9);
  color: var(--el-color-success);
  border: 1px solid var(--el-color-success-light-5);
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 12px;
}

.model-type-description {
  color: var(--el-color-info-dark-2);
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 20px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.model-type-footer {
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
  /* background-color: rgba(0, 0, 0, 0.5); */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  /* background-color: var(--el-bg-color); */
  background-image: radial-gradient(transparent 1px, var(--el-bg-color) 1px);
  background-size: 4px 4px;
  backdrop-filter: saturate(50%) blur(4px);
  box-shadow: 0 0 20px rgba(0, 0, 0, 1);
  border-radius: 10px;
  width: 90%;
  max-width: 1000px;
  max-height: 80vh;
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

.pretrained-models-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.pretrained-model-card {
  background-color: var(--el-fill-color);
  border-radius: 8px;
  padding: 15px;
  display: flex;
  flex-direction: column;
}

.model-card-header h4 {
  margin: 0 0 10px 0;
  font-size: 16px;
  /* color: var(--text-color); */
}

.model-card-metrics {
  font-size: 12px;
  color: var(--text-secondary-color);
  margin-bottom: 10px;
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
  /* gap: 2px; */
}

@media (max-width: 768px) {

  .model-types-grid,
  .pretrained-models-grid {
    grid-template-columns: 1fr;
  }
}
</style>
