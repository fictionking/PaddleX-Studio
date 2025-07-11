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
    <div class="layout-container">
      <div class="left-column">
        <div class="part-container">
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
              <el-button v-if="appConfig.status == 'stopped'" type="primary"
                @click.stop="handleAppStart()">启动</el-button>
              <el-button v-if="appConfig.status == 'running'" type="danger" @click.stop="handleAppStop()">停止</el-button>
            </el-form-item>
          </el-form>
        </div>
        <div class="part-container">
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
        <div class="part-container">
          <h3>Api</h3>
          <el-form :model="predictFormData" label-width="120px">
            <el-form-item label="启动服务">
              <el-text>GET /apps/start/{{appConfig.id}}</el-text>
            </el-form-item>
            <el-form-item label="停止服务">
              <el-text>GET /apps/stop</el-text>
            </el-form-item>
            <el-form-item label="推理">
              <el-text>POST /apps/infer/{{appConfig.id}}/{{current_result_type}}</el-text>
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
            <el-form-item v-if="input_types.includes('img') && !input_types.includes('file')" label="上传图片">
              <el-upload class="upload-demo" action="#" :limit="1" :auto-upload="false" :on-change="handleImageChange"
                style="width: 400px">
                <div style="display: flex; align-items: center;">
                  <el-button size="small" type="primary">点击上传图片</el-button>
                  <span class="el-upload__tip" style="padding-left: 10px;">只能上传jpg/png文件，且不超过2MB</span>
                </div>

              </el-upload>
            </el-form-item>

            <!-- 文件上传组件 -->
            <el-form-item v-if="input_types.includes('file') && !input_types.includes('img')" label="上传文件">
              <el-upload class="upload-demo" action="#" :limit="1" :auto-upload="false" :on-change="handleFileChange">
                <div style="display: flex; align-items: center; justify-content: center;">
                  <el-button size="small" type="primary">点击上传文件</el-button>
                  <span class="el-upload__tip" style="padding-left: 10px;">支持任意类型文件，且不超过10MB</span>
                </div>
              </el-upload>
            </el-form-item>

            <!-- 文本输入组件 -->
            <el-form-item v-if="input_types.includes('text')" label="输入文本">
              <el-input v-model="inputText" type="textarea" rows="4" placeholder="请输入文本内容"></el-input>
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
          <!-- JSON结果展示 -->
          <div v-else-if="inferenceResult.type === 'json'" class="result-json">
            <el-input type="textarea" :rows="10" :value="JSON.stringify(inferenceResult.data, null, 2)" readonly
              style="width: 100%;" :autosize="{ minRows: 10, maxRows: 20 }" />
          </div>
          <!-- HTML结果展示 -->
          <div v-else-if="inferenceResult.type === 'html'" class="result-html" v-html="inferenceResult.data"></div>
        </div>
      </div>
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
      result_types: [],
      formData: {},
      predictFormData: {},
      input_types: [],
      inputText: '',
      uploadedImage: null,
      uploadedFile: null,
      inferenceResult: { type: '', data: null, loading: false },
      urlReferences: new Map(),
      current_result_type: 'json'
    }
  },
  beforeUnmount() {
    // 组件销毁时释放弱引用管理的URL
    this.revokeSafeObjectURL(this.inferenceResult.data);
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
          this.result_types = this.appConfig.result_types;
          this.input_types = this.appConfig.input_types || [];
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
    },
    /**
     * 处理图片上传变化事件
     */
    handleImageChange(file, fileList) {
      this.uploadedImage = file.raw;
    },
    /**
     * 处理文件上传变化事件
     */
    handleFileChange(file, fileList) {
      this.uploadedFile = file.raw;
    },
    /**
     * 使用弱引用创建安全的对象URL
     * @param {Blob} blob - 二进制对象
     * @returns {string} 对象URL
     */
    createSafeObjectURL(blob) {
      const url = URL.createObjectURL(blob);
      this.urlReferences.set(url, blob); // Map存储URL与Blob映射
      return url;
    },

    /**
     * 释放弱引用管理的对象URL
     * @param {string} url - 需要释放的对象URL
     */
    /**
     * 安全地撤销Blob URL并从引用跟踪中移除
     * @param {string} url - 要撤销的Blob URL
     */
    revokeSafeObjectURL(url) {
      if (typeof url === 'string' && url.startsWith('blob:') && this.urlReferences.has(url)) {
        URL.revokeObjectURL(url);
        this.urlReferences.delete(url);
      }
    },
    /**
     * 提交推理请求
     */
    async submitInference() {
      if (!this.uploadedImage && !this.uploadedFile && !this.inputText) {
        this.$message.warning('请提供推理输入内容');
        return;
      }

      const formData = new FormData();
      // 直接添加文本输入和推理参数到FormData
      // 仅当inputText不为空时添加input字段
      if (this.inputText) {
        formData.append('input', this.inputText);
      }
      // 遍历predictFormData的所有属性并添加到FormData
      const predict_params = {}
      Object.keys(this.predictFormData).forEach(key => {
        const value = this.predictFormData[key];
        // 仅添加非null值
        if (value !== null && value !== undefined) {
          predict_params[key] = value;
        }
      });
      formData.append('predict_params', JSON.stringify(predict_params));
      // 添加文件/图片
      if (this.uploadedImage) formData.append('file', this.uploadedImage);
      if (this.uploadedFile) formData.append('file', this.uploadedFile);

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
          // 当结果类型为图片时，设置responseType为blob
          ...(this.current_result_type === 'img' && { responseType: 'blob' })
        };
        const response = await axios.post(`/apps/infer/${this.$route.params.appId}/${this.current_result_type}`, formData, responseConfig);
        this.$message.success('推理成功');
        // 处理推理结果
        this.handleInferenceResult(response);
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
            this.$message.error('推理失败!');
          }
        }
        else {
          this.$message.error('推理失败!');
        }
      }
    },
    /**
     * 处理推理结果
     */
    /**
     * 根据结果类型展示推理结果
     * @param {Object} result - 推理结果数据
     */
    /**
       * 根据响应类型和结果类型处理并展示推理结果
       * @param {Object} response - Axios响应对象，可能包含文件或文本数据
       */
    handleInferenceResult(response) {

      const contentType = response.headers['content-type'] || '';
      const isFileResponse = contentType.includes('application/octet-stream') ||
        contentType.includes('image/') ||
        this.current_result_type === 'img';

      if (isFileResponse) {
        this.inferenceResult.data = this.createSafeObjectURL(response.data);
        this.inferenceResult.loading = false;
      } else {
        // 处理文本类型响应
        let resultData = response.data;
        // 尝试解析JSON（如果是JSON字符串）
        if (typeof resultData === 'string' && contentType.includes('application/json')) {
          try {
            resultData = JSON.parse(resultData);
          } catch (e) {
            console.warn('无法解析JSON响应:', e);
          }
        }
        this.inferenceResult.data = resultData;
        this.inferenceResult.loading = false;
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
.result-json,
.result-html {
  margin-top: 10px;
}

.result-html {
  min-height: 200px;
  padding: 10px;
  background-color: #f9f9f9;
}

.layout-container {
  display: flex;
  gap: 20px;
  margin: 20px 0;
}

.left-column {
  width: 500px;
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