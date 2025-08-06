<template>
  <div class="app-detail-container">
    <div class="page-header">
      <div class="page-header-info">
        <h2 class="page-header h2" v-text="appInfo.name"></h2>
        <el-tag type="info" effect="plain" style="font-size: 14px;" v-text="appInfo.id"></el-tag>
        <el-tag type="success" v-text="appInfo.type === 'module' ? '模型' : '产线'"></el-tag>
        <el-tag type="success" v-for="tag in appInfo.tags" :key="tag">{{ tag }}</el-tag>
        <el-tag :class="appInfo.status === 'running' ? 'status_running' : 'status_stopped'"
          :type="appInfo.status == 'stopped' ? 'primary' : 'success'"
          v-text="appInfo.status === 'running' ? '运行中' : '未运行'"></el-tag>
      </div>
      <el-button type="primary" plain @click="$router.push('/app')">返回</el-button>
    </div>
    <div class="layout-container">
      <div class="left-column">
        <div class="part-container">
          <h3>模型参数配置</h3>
          <el-form :model="modelFormData" label-width="auto" @submit.prevent="saveConfig">
            <el-form-item v-for="(param, key) in modelParams" :key="key" :label="key">
              <el-tooltip :disabled="!param.desc" :content="param.desc" raw-content>
                <el-input-number v-if="['int', 'float'].includes(param.type)" v-model="modelFormData[key]"
                  :step="param.type === 'float' ? 0.01 : 1" :min="param.min !== null ? param.min : undefined"
                  :max="param.max !== null ? param.max : undefined" controls-position="right"
                  :readonly="!param.config_able"></el-input-number>
                <el-switch v-else-if="param.type === 'bool'" v-model="modelFormData[key]" active-text="True"
                  inactive-text="False" :readonly="!param.config_able"></el-switch>
                <el-input v-else-if="param.type === 'dict'" v-model="modelFormData[key]" type="textarea"
                  placeholder="请输入JSON格式的字典，例如: {&quot;key&quot;: &quot;value&quot;}" :rows=4
                  :readonly="!param.config_able"></el-input>
                <el-input v-else-if="param.type === 'list'" v-model="modelFormData[key]" type="textarea"
                  placeholder="请输入JSON格式的列表，例如: [&quot;value1&quot;, &quot;value2&quot;]" :rows=4
                  :readonly="!param.config_able"></el-input>
                <el-select v-else-if="param.type === 'enum'" v-model="modelFormData[key]"
                  :readonly="!param.config_able">
                  <el-option v-for="item in param.enum" :key="item" :label="item" :value="item"></el-option>
                </el-select>
                <el-input v-else v-model="modelFormData[key]" :readonly="!param.config_able"></el-input>
              </el-tooltip>
            </el-form-item>
            <el-form-item label=" ">
              <el-button type="primary" @click="saveConfig">保存配置</el-button>
              <el-button v-if="appInfo.status == 'stopped'" type="primary"
                @click.stop="handleAppStart()">启动</el-button>
              <el-button v-if="appInfo.status == 'running'" type="danger" @click.stop="handleAppStop()">停止</el-button>
            </el-form-item>
          </el-form>
        </div>
        <div class="part-container">
          <h3>推理参数配置</h3>
          <el-form :model="predictFormData" label-width="auto">
            <el-form-item v-for="(param, key) in predict_params" :key="key" :label="key">
              <el-tooltip :disabled="!param.desc" :content="param.desc" raw-content>
                <el-input-number v-if="['int', 'float'].includes(param.type)" v-model="predictFormData[key]"
                  :step="param.type === 'float' ? 0.01 : 1" :min="param.min !== null ? param.min : undefined"
                  :max="param.max !== null ? param.max : undefined" controls-position="right"
                  :readonly="!param.config_able"></el-input-number>
                <el-switch v-else-if="param.type === 'bool'" v-model="predictFormData[key]" active-text="True"
                  inactive-text="False" :readonly="!param.config_able"></el-switch>
                <el-input v-else-if="param.type === 'dict'" v-model="predictFormData[key]" type="textarea"
                  placeholder="请输入JSON格式的字典，例如: {&quot;key&quot;: &quot;value&quot;}" :rows=4
                  :readonly="!param.config_able"></el-input>
                <el-input v-else-if="param.type === 'list'" v-model="predictFormData[key]" type="textarea"
                  placeholder="请输入JSON格式的列表，例如: [&quot;value1&quot;, &quot;value2&quot;]" :rows=4
                  :readonly="!param.config_able"></el-input>
                <el-select v-else-if="param.type === 'enum'" v-model="predictFormData[key]"
                  :readonly="!param.config_able">
                  <el-option v-for="item in param.enum" :key="item" :label="item" :value="item"></el-option>
                </el-select>
                <el-input v-else v-model="predictFormData[key]" :readonly="!param.config_able"></el-input>
              </el-tooltip>
            </el-form-item>
          </el-form>
        </div>
        <div class="part-container">
          <h3>API</h3>
          <el-form label-width="auto">
            <el-form-item label="启动服务">
              <el-text>GET /apps/start/{{ appInfo.id }}</el-text>
            </el-form-item>
            <el-form-item label="停止服务">
              <el-text>GET /apps/stop</el-text>
            </el-form-item>
            <el-form-item label="推理">
              <el-text>POST /apps/infer/{{ appInfo.id }}/{{ current_result_type }}</el-text>
            </el-form-item>
          </el-form>
        </div>
        <el-text>💡不推荐在生产环境使用，只用于简单测试，具体可参考PaddleX文档。</el-text>
      </div>

      <div class="right-column">
        <div class="part-container">
          <h3>推理输入配置</h3>
          <el-form label-width="120px">
            <!-- 图片上传组件 -->
            <el-form-item v-if="input_types === 'img'" label="上传图片">
              <el-upload class="upload-demo" action="#" :limit="1" :auto-upload="false" :on-change="handleFileChange"
                style="width: 400px">
                <div style="display: flex; align-items: center;">
                  <el-button size="small" type="primary">点击上传图片</el-button>
                  <span class="el-upload__tip" style="padding-left: 10px;">只能上传jpg/png文件，且不超过2MB</span>
                </div>

              </el-upload>
            </el-form-item>

            <!-- 文件上传组件 -->
            <el-form-item v-if="input_types === 'file'" label="上传文件">
              <el-upload class="upload-demo" action="#" :limit="1" :auto-upload="false" :on-change="handleFileChange">
                <div style="display: flex; align-items: center; justify-content: center;">
                  <el-button size="small" type="primary">点击上传文件</el-button>
                  <span class="el-upload__tip" style="padding-left: 10px;">支持任意类型文件，且不超过10MB</span>
                </div>
              </el-upload>
            </el-form-item>

            <!-- 文本输入组件 -->
            <el-form-item v-if="input_types === 'text'" label="输入文本">
              <el-input v-model="inputText" type="textarea" rows="4" placeholder="请输入文本内容"></el-input>
            </el-form-item>

            <el-form-item v-if="typeof input_types === 'object' && !Array.isArray(input_types) && input_types !== null"
              v-for="(param, key) in input_types" :key="key" :label="key">
              <el-tooltip :disabled="!param.desc" :content="param.desc" raw-content>
                <el-upload v-if="['img', 'file'].includes(param.type)" action="#" :limit="1" :auto-upload="false"
                  :on-change="(file, fileList) => handleFileChange(file, fileList, key)">
                  <el-button size="small" type="primary">点击上传文件</el-button>
                </el-upload>
                <el-input v-else-if="param.type === 'text'" v-model="inputDict[key]" type="textarea"
                  placeholder="请输入文本内容" :rows=4></el-input>
              </el-tooltip>
            </el-form-item>

            <el-form-item label="推理结果类型">
              <el-select v-model="current_result_type" placeholder="请选择结果类型" style="width: 240px">
                <el-option v-for="type in result_types" :key="type" :label="type" :value="type"></el-option>
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="success" @click="submitInference">提交推理</el-button>
            </el-form-item>
          </el-form>
        </div>

        <!-- 推理结果展示区域 -->
        <div v-if="inferenceResult.data" class="part-container">
          <h3>推理结果</h3>
          <!-- 图片结果展示 -->
          <div v-if="inferenceResult.type === 'img'" class="result-image">
            <img v-if="!inferenceResult.loading" :src="inferenceResult.data" alt="推理结果图片"
              style="max-width: 100%; max-height: 500px;">
            <div v-if="!inferenceResult.data && !inferenceResult.loading" class="image-error">图片加载失败，请重试</div>
          </div>
          <!-- JSON结果展示 - 虚拟滚动优化版 -->
          <div v-else-if="inferenceResult.type === 'json'" class="result-json">
            <el-scrollbar class="json-native-scrollbar">
              <pre><code>{{ inferenceResult.data.join('\n') }}</code></pre>
            </el-scrollbar>
          </div>
          <!-- HTML结果展示 -->
          <div v-else-if="inferenceResult.type === 'html'" class="result-html" v-html="inferenceResult.data"></div>
          <!-- CSV结果展示 -->
          <div v-else-if="inferenceResult.type === 'csv'" class="result-csv">
            <a :href="inferenceResult.data" download="result.csv">下载CSV</a>
          </div>
          <!-- 视频结果展示 -->
          <div v-else-if="inferenceResult.type === 'video'" class="result-video">
            <a :href="inferenceResult.data" download="result.mp4">下载视频</a>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
export default {
  name: 'ModelAppDetail',
  data() {
    return {
      appId: '',
      appInfo: {},
      appConfig: {},
      modelParams: {},
      predict_params: {},
      result_types: [],
      modelFormData: {},
      predictFormData: {},
      input_types: null,
      inputText: '',
      inputDict: {},
      uploadedFiles: {},
      inferenceResult: { type: '', data: null, loading: false },
      current_result_type: 'json'
    }
  },
  beforeUnmount() {
    // 组件销毁时释放弱引用管理的URL
    this.revokeSafeObjectURL(this.inferenceResult.data);
  },
  mounted() {
  },
  async created() {
    this.appId = this.$route.params.appId;
    await this.fetchAppInfo();
    // 页面加载时获取配置数据
    this.fetchConfig();
  },
  methods: {
    /**
     * 获取应用详情
     */
    async fetchAppInfo() {
      try {
        this.loadingConfig = true;
        const response = await axios.get(`/apps/info/${this.appId}`);
        this.appInfo = response.data;
      } catch (error) {
        console.error('获取应用详情失败:', error);
        this.errorConfig = '获取应用详情失败，请重试';
      }
    },
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
          this.result_types = this.appConfig.result_types;
          this.input_types = this.appConfig.input_types;
          // 初始化表单数据
          Object.keys(this.modelParams).forEach(key => {
            this.modelFormData[key] = this.modelParams[key].value;
          });
          Object.keys(this.predict_params).forEach(key => {
            this.predictFormData[key] = this.predict_params[key].value;
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
        await axios.post(`/apps/config/${this.$route.params.appId}`, { model_params: this.modelFormData });
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
          this.appInfo.status = 'running'
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
          this.appInfo.status = 'stopped'
        })
        .catch(error => {
          this.$message.error('应用停止失败');
          console.error(error);
        })
        .finally(() => {
          loading.close();  // 无论成功失败都关闭加载框
        });
    },
    /**
     * 处理文件上传变化事件
     */
    handleFileChange(file, fileList, key = 'default') {
      if (key === 'default') {
        this.uploadedFiles = file.raw;
      } else {
        this.inputDict[key] = file.raw;
      }
    },
    /**
     * 使用弱引用创建安全的对象URL
     * @param {Blob} blob - 二进制对象
     * @returns {string} 对象URL
     */
    createSafeObjectURL(blob) {
      const url = URL.createObjectURL(blob);
      return url;
    },
    /**
     * 安全地撤销Blob URL并从引用跟踪中移除
     * @param {string} url - 要撤销的Blob URL
     */
    revokeSafeObjectURL(url) {
      if (typeof url === 'string' && url.startsWith('blob:')) {
        URL.revokeObjectURL(url);
      }
    },
    /**
     * 提交推理请求
     */
    async submitInference() {
      // 根据input_types类型验证输入
      const isDictType = typeof this.input_types === 'object';
      let hasInput = false;

      // 验证输入是否存在
      if (['img', 'file'].includes(this.input_types)) {
        hasInput = !!this.uploadedFiles;
      } else if (this.input_types === 'text') {
        hasInput = !!this.inputText.trim();
      } else if (isDictType) {
        hasInput = Object.keys(this.inputDict).length > 0;
      }

      if (!hasInput) {
        this.$message.warning('请提供推理输入内容');
        return;
      }

      const formData = new FormData();
      // 根据input_types类型处理输入参数
      if (['img', 'file'].includes(this.input_types)) {
        formData.append('input', this.uploadedFiles);
      } else if (this.input_types === 'text') {
        formData.append('input', this.inputText.trim());
      } else if (isDictType) {
        // 处理对象类型输入，分离文件和文本值
        const inputObj = {};
        Object.keys(this.inputDict).forEach(key => {
          const value = this.inputDict[key];
          if (value instanceof File) {
            // 如果是文件，添加到FormData，并在inputObj中记录文件标识
            const fileKey = `file_${Date.now()}_${key}`;
            formData.append(fileKey, value);
            inputObj[key] = { uid: fileKey };
          } else {
            inputObj[key] = value;
          }
        });
        formData.append('input', JSON.stringify(inputObj));
      }

      // 遍历predictFormData的所有属性并添加到FormData
      const predict_params = {}
      Object.keys(this.predictFormData).forEach(key => {
        const value = this.predictFormData[key];
        // 仅添加非null值
        if (value !== null && value !== undefined) {
          if (this.predict_params[key].type === 'dict' || this.predict_params[key].type === 'list')
            predict_params[key] = JSON.parse(value);
          else
            predict_params[key] = value;
        }
      });
      formData.append('predict_params', JSON.stringify(predict_params));
      // 移除旧的file参数，统一使用input参数传递所有输入内容
      // if (this.uploadedFile) formData.append('file', this.uploadedFile);
      // 显示加载中模态框
      const loading = this.$loading({
        lock: true,
        text: '推理中，请稍候...',
        background: 'rgba(0, 0, 0, 0.7)'
      });
      try {
        // 下次推理前释放已存在的对象URL
        this.revokeSafeObjectURL(this.inferenceResult.data);

        this.inferenceResult = {
          type: this.current_result_type,
          data: null,
          loading: true
        };

        // 根据结果类型动态设置响应类型
        const responseConfig = {
          headers: { 'Content-Type': 'multipart/form-data' },
          // 当结果类型为图片、视频、csv时，设置responseType为blob
          ...((this.current_result_type === 'img' || this.current_result_type === 'video' || this.current_result_type === 'csv') && { responseType: 'blob' })
        };
        const response = await axios.post(`/apps/infer/${this.$route.params.appId}/${this.current_result_type}`, formData, responseConfig);
        // 处理推理结果
        this.handleInferenceResult(response);
        this.$message.success('推理成功');
      } catch (error) {
        if (error.response && error.response.data) {
          //如果是Blob提取内容转成json
          let data;
          try {
            if (error.response.data instanceof Blob) {
              data = new TextDecoder().decode(await error.response.data.arrayBuffer())
              data = JSON.parse(data)
            }
            else if (typeof error.response.data === 'string') {
              data = JSON.parse(error.response.data)
            }
            else
              data = error.response.data
            this.$message.error('推理失败:' + data.error);
          } catch (e) {
            console.warn('无法解析JSON响应:', e);
            this.$message.error('推理失败!' + error.message);
          }
        }
        else {
          this.$message.error('推理失败!' + error.message);
        }
      } finally {
        loading.close();  // 无论成功失败都关闭加载框
      }
    },
    /**
       * 根据响应类型和结果类型处理并展示推理结果
       * @param {Object} response - Axios响应对象，可能包含文件或文本数据
       */
    handleInferenceResult(response) {
      switch (this.current_result_type) {
        case 'img':
          const imgFile = new File([response.data], 'result.jpg', { type: 'image/jpeg' });
          this.inferenceResult.data = this.createSafeObjectURL(imgFile);
          this.inferenceResult.loading = false;
          break;
        case 'csv':
          //保存文件到本地
          const csvFile = new File([response.data], 'result.csv', { type: 'text/csv' });
          this.inferenceResult.data = this.createSafeObjectURL(csvFile);
          this.inferenceResult.loading = false;
          break;
        case 'video':
          //保存文件到本地
          const videoFile = new File([response.data], 'result.mp4', { type: 'video/mp4' });
          this.inferenceResult.data = this.createSafeObjectURL(videoFile);
          this.inferenceResult.loading = false;
          break;
        case 'json':
          const jsonData = typeof response.data === 'string' ? JSON.parse(response.data) : response.data;
          const formatted = JSON.stringify(jsonData, null, 2);
          const jsonLines = formatted.split('\n');
          if (jsonLines.length > 500) {
            this.inferenceResult.data = jsonLines.slice(0, 500);
            // 添加超长提示文本到数组末尾
            this.inferenceResult.data.push('...(超长未显示)');
          }
          else
            this.inferenceResult.data = jsonLines;
          this.inferenceResult.loading = false;
          break;
        default:
          this.inferenceResult.data = response.data;
          this.inferenceResult.loading = false;
          break;
      }
    },
  }
}
</script>

<style scoped>
.app-detail-container {
  padding: 20px;
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

.result-image,
.result-video,
.result-csv,
.result-html {
  margin-top: 10px;
}

.result-json {
  position: relative;
}

.json-native-scrollbar {
  height: 500px;
  width: 100%;
  overflow: auto;
}

.json-native-scrollbar .el-scrollbar__wrap {
  overflow-x: auto;
  overflow-y: auto;
}

.json-native-scrollbar .el-scrollbar__bar.is-vertical {
  width: 6px;
  right: 0;
}

.json-native-scrollbar .el-scrollbar__thumb {
  background-color: rgba(144, 147, 153, 0.5);
  border-radius: 3px;
}

.json-native-scrollbar .el-scrollbar__thumb:hover {
  background-color: rgba(144, 147, 153, 0.7);
}

.result-html {
  min-height: 200px;
  padding: 10px;
}

.layout-container {
  display: flex;
  gap: 20px;
  margin: 20px 0;
}

.left-column {
  width: 600px;
  margin: 20px auto;
}

.right-column {
  width: 100%;
  margin: 20px auto;
}

.part-container {
  padding-top: 0px;
  padding-bottom: 15px;
  padding-left: 15px;
  padding-right: 15px;
  border: 1px solid var(--el-border-color);

  border-radius: 4px;
  margin: 20px auto;
}
</style>