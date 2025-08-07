<template>
  <div class="pipeline-definitions-container">
    <!-- 分类选择 -->
    <div class="category-tabs">
      <div v-for="(category, index) in categories" :key="category.id"
        :class="['category-tab', { active: activeCategoryIndex === index }]" @click="activeCategoryIndex = index">
        {{ category.name }}
      </div>
    </div>

    <!-- 产线类型卡片网格 -->
    <div class="pipeline-types-grid">
      <div v-for="pipeline in filteredPipelines" :key="pipeline.id" class="pipeline-type-card">
        <div class="pipeline-type-header">
          <h3>{{ pipeline.title }}</h3>
        </div>
        <el-carousel v-if="Array.isArray(pipeline.description)" height="auto" autoplay arrow="never"
          indicator-position="outside">
          <el-carousel-item v-for="item in pipeline.description" :key="item" style="height: auto;">
            <p class="pipeline-type-description" v-html="item || '无描述信息'"></p>
          </el-carousel-item>
        </el-carousel>
        <p v-else class="pipeline-type-description" v-html="pipeline.description || '无描述信息'"></p>
        <div class="pipeline-type-footer" style="display: flex; justify-content: space-between; align-items: center;">
          <el-button type="primary" round text @click="handleUpdateModel(pipeline)">缓存产线所用模型</el-button>
          <el-button type="primary" round text @click="openCreateAppDialog(pipeline)">应用</el-button>
        </div>
      </div>
    </div>

    <!-- 新增应用创建对话框 -->
    <el-dialog v-model="showCreateAppDialog" title="模型应用" width="600px">
      <div style="margin-bottom: 20px;">
        <el-breadcrumb separator="/">
          <el-breadcrumb-item>{{ newAppFormData.category }}</el-breadcrumb-item>
          <el-breadcrumb-item>{{ newAppFormData.pipeline_name }}</el-breadcrumb-item>
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
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showCreateAppDialog = false">取消</el-button>
          <el-button type="primary" @click="submitAppForm">确定</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 下载进度对话框 -->
    <el-dialog title="模型更新" v-model="updateDialogVisible" width="600px" align-center :close-on-click-modal="false"
      @close="cancelUpdate">
      <div class="progress-container">
        <p class="progress-text">{{ progressText }}</p>
        <el-progress :percentage="downloadProgress" :stroke-width="10" striped striped-flow
          :duration="10"></el-progress>
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
      activeCategoryIndex: 0,
      selectedModule: null,
      showCreateAppDialog: false,
      newAppFormData: {
        name: '',
        id: '',
        category: '',
        pipeline_id: '',
        pipeline_name: ''
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
  computed: {
    categories() {
      return this.definitions.map(item => item.category);
    },
    filteredPipelines() {
      if (this.definitions.length === 0) return [];
      return this.definitions[this.activeCategoryIndex].pipelines;
    }
  },
  mounted() {
    this.fetchPipelineDefinitions();
  },
  methods: {
    async fetchPipelineDefinitions() {
      try {
        const response = await axios.get('/define/pipelines');
        this.definitions = response.data;
      } catch (error) {
        console.error('获取产线定义失败:', error);
        this.$notify.error({
          title: '错误',
          message: '获取产线定义失败，请刷新页面重试'
        });
      }
    },

    /**
     * 打开创建应用对话框并初始化数据
     * @param {Object} pipeline - 选中的产线
     */
    openCreateAppDialog(pipeline) {
      const categoryid = this.definitions[this.activeCategoryIndex].category.id;
      this.newAppFormData = {
        name: '',
        id: '',
        category: categoryid,
        pipeline_id: pipeline.id,
        pipeline_name: pipeline.title
      };
      if (categoryid === 'TimeSeries') {
        this.newAppFormData.tip = '💡此应用只能使用官方示例数据，自定义数据需要使用自训练模型。'
      }
      this.showCreateAppDialog = true;
    },

    /**
     * 提交应用表单数据到后端
     */
    async submitAppForm() {
      this.$refs.appForm.validate(async (valid) => {
        if (valid) {
          try {
            await axios.post('/define/pipelines/createapp', this.newAppFormData);
            this.$message.success('应用创建成功');
            this.showCreateAppDialog = false;
            this.$router.push(`/app/pipeline/${this.newAppFormData.id}`);
          } catch (error) {
            this.$message.error('应用创建失败:' + error.response.data.message);
          }
        }
      });
    },
    /**
     * 处理产线更新功能
     * @param {Object} pipeline - 要更新的产线对象
     */
    handleUpdateModel(pipeline) {
      this.updateDialogVisible = true;
      this.downloadProgress = 0;
      this.progressText = '准备开始下载...';
      this.speedText = '';
      const eventSource = new EventSource(`/define/pipelines/cacheModels/${pipeline.id}`);

      eventSource.onmessage = (event) => {
        // 忽略心跳包空数据
        if (!event.data.trim()) return;

        const data = JSON.parse(event.data);
        // 处理下载中状态
        if (data.status === 'downloading') {
          this.downloadProgress = data.progress;
          this.progressText = `正在下载[${data.idx}/${data.count}]${data.category_id}/${data.module_id}/${data.model_id}的${data.type}模型: ${data.file}`;
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
          setTimeout(() => {
            this.updateDialogVisible = false;
            this.$message.success('模型更新成功');
          }, 1000);
        }
        // 处理错误状态
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
      fetch(`/define/cancelCache`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json'
        }
      });
    }
  }
}
</script>

<style scoped>
.pipeline-definitions-container {
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

.pipeline-types-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.pipeline-type-card {
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

.pipeline-type-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
}

.pipeline-type-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.pipeline-type-header h3 {
  margin: 0;
  font-size: 18px;
}

.pipeline-type-description {
  color: var(--el-color-info-dark-2);
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 20px;
  overflow: hidden;
  text-overflow: ellipsis;
}

:deep(.pipeline-type-description img) {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 0 auto;
}

.pipeline-type-footer {
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
  .pipeline-types-grid {
    grid-template-columns: 1fr;
  }
}
</style>
