<template>
  <div class="pipeline-app-detail-container">
    <el-card>
      <div>
        <div class="card-header">
          <span>产线应用详情</span>
        </div>
      </div>

      <el-tabs v-model="activeTab">
        <!-- 参数配置标签页 -->
        <el-tab-pane label="参数配置" name="config">
          <div v-if="loadingConfig" class="loading-container">
            <span>加载配置中...</span>
          </div>
          <div v-else-if="errorConfig" class="error-container">
            <el-alert :message="errorConfig" type="error" show-icon />
          </div>
          <div v-else class="config-form-container">
            <el-form ref="configForm" :model="configData" label-width="120px">
              <el-form-item label="产线名称">
                <el-input v-model="configData.pipeline_name" disabled />
              </el-form-item>

              <!-- 扁平化配置列表 -->
              <div class="flat-config-list">
                <div v-for="item in flatConfigItems" :key="item.id" class="config-item">
                  <div :style="{ 'padding-left': item.depth * 40 + 'px' }" class="config-item-header"
                    @click="!isObject(item.value) ? toggleEdit(item.id) : null">
                    <span class="config-key">{{ item.key }}: </span>
                    <span v-if="!isObject(item.value)" class="config-value">{{ formatValue(item.value) }}</span>
                    <el-icon v-if="!isObject(item.value)" class="edit-icon">
                      <Edit />
                    </el-icon>
                  </div>
                  <div v-if="editingItemId === item.id && !isObject(item.value)" class="config-item-editor">
                    <component :is="getComponentType(item.value)" v-model="editValue"
                      :options="getComponentOptions(item.key, item.value)"
                      @change="handleValueChange(item.path, editValue)" />
                    <div class="editor-buttons">
                      <el-button size="small" @click="toggleEdit(null)">取消</el-button>
                      <el-button type="primary" size="small" @click="saveEdit(item.id)">保存</el-button>
                    </div>
                  </div>
                </div>
              </div>

              <el-form-item>
                <el-button type="primary" @click="saveConfig">保存配置</el-button>
                <el-button @click="resetConfig">重置</el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>

        <!-- API文档标签页 -->
        <el-tab-pane label="API文档" name="api-docs">
          <div v-if="loadingApiDocs" class="loading-container">
            <span>加载API文档中...</span>
          </div>
          <div v-else-if="errorApiDocs" class="error-container">
            <el-alert :message="errorApiDocs" type="error" show-icon />
          </div>
          <div v-else class="api-docs-container">
            <div class="api-info">
              <h2>{{ apiDocs.info.title }}</h2>
              <p>{{ apiDocs.info.description }}</p>
              <p>版本: {{ apiDocs.info.version }}</p>
            </div>

            <el-divider />

            <div v-for="(pathItem, path) in apiDocs.paths" :key="path" class="api-path-item">
              <div class="path-header">
                <el-tag v-for="method in Object.keys(pathItem)" :key="method" :type="getMethodType(method)">
                  {{ method.toUpperCase() }}
                </el-tag>
                <span class="path-url">{{ path }}</span>
              </div>

              <div v-for="(methodItem, method) in pathItem" :key="method" class="api-method-item">
                <h3>{{ methodItem.summary }}</h3>
                <p class="method-description">{{ methodItem.description }}</p>

                <!-- 请求参数 -->
                <div v-if="methodItem.requestBody" class="api-section">
                  <h4>请求参数</h4>
                  <el-table :data="getRequestParams(methodItem.requestBody)">
                    <el-table-column prop="name" label="参数名" width="150" />
                    <el-table-column prop="type" label="类型" width="150" />
                    <el-table-column prop="description" label="描述" />
                    <el-table-column prop="required" label="必填" width="80" />
                  </el-table>
                </div>

                <!-- 响应 -->
                <div class="api-section">
                  <h4>响应</h4>
                  <el-table :data="getResponseParams(methodItem.responses)">
                    <el-table-column prop="code" label="状态码" width="100" />
                    <el-table-column prop="description" label="描述" width="200" />
                    <el-table-column prop="schema" label="数据结构" />
                  </el-table>
                </div>

                <!-- 测试按钮 -->
                <el-button type="primary" size="small" @click="openApiTestDialog(path, method, methodItem)"
                  style="margin-top: 10px;">
                  测试API
                </el-button>
              </div>
            </div>
          </div>
        </el-tab-pane>

      </el-tabs>

    </el-card>

    <!-- API测试对话框 -->
    <el-dialog v-model="showApiTestDialog" :title="apiTestDialogTitle" width="800px" :close-on-click-modal="false">
      <div v-if="loadingApiTest" class="loading-container">
        <span>准备测试环境...</span>
      </div>
      <div v-else class="api-test-container">
        <el-form ref="apiTestForm" :model="apiTestFormData" label-width="120px">
          <el-form-item v-for="param in apiTestParams" :key="param.name" :label="param.name">
            <component :is="getComponentType(param.defaultValue)" v-model="apiTestFormData[param.name]"
              :options="getComponentOptions(param.name, param.defaultValue, param.type)" />
          </el-form-item>
        </el-form>

        <div class="api-test-result" v-if="apiTestResult">
          <h4>测试结果</h4>
          <pre>{{ formattedApiTestResult }}</pre>
        </div>
      </div>
      <div class="api-test-footer">
        <el-button @click="showApiTestDialog = false">取消</el-button>
        <el-button type="primary" @click="submitApiTest">发送请求</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
export default {
  name: 'PipeLineAppDetail',
  components: {
    Edit: ElementPlusIconsVue.Edit,
  },
  data() {
    return {
      activeTab: 'config',
      // 配置相关数据
      configData: {},
      loadingConfig: true,
      errorConfig: '',
      // 扁平化配置项
      flatConfigItems: [],
      // 编辑相关
      editingItemId: null,
      editValue: null,
      // API文档相关数据
      apiDocs: {},
      loadingApiDocs: true,
      errorApiDocs: '',
      // API测试相关数据
      showApiTestDialog: false,
      apiTestDialogTitle: '',
      apiTestPath: '',
      apiTestMethod: '',
      apiTestParams: [],
      apiTestFormData: {},
      loadingApiTest: false,
      apiTestResult: null
    };
  },
  created() {
    // 从路由参数中获取应用ID
    this.appId = this.$route.params.appId;
    // 使用异步函数确保fetchConfig执行完成后再执行fetchApiDocs
    this.initData();
  },
  methods: {
    /**
     * 判断一个值是否是对象类型
     * @param {any} value - 要判断的值
     * @returns {boolean} - 是否是对象类型
     */
    isObject(value) {
      return value !== null && typeof value === 'object' && !Array.isArray(value);
    },

    /**
     * 初始化数据
     */
    async initData() {
      await this.fetchConfig();
      // 只有当configData有值且没有错误时才获取API文档
      if (Object.keys(this.configData).length > 0 && !this.errorConfig) {
        this.fetchApiDocs();
      }
    },
    /**
     * 获取配置数据
     */
    async fetchConfig() {
      try {
        this.loadingConfig = true;
        const response = await axios.get(`/apps/pipeline/config/${this.appId}`);
        // 假设返回的数据格式与config.yaml结构一致
        this.configData = response.data;
        // 扁平化配置数据
        this.flatConfigItems = this.flattenConfig(this.configData || {});
        this.errorConfig = '';
      } catch (error) {
        console.error('获取配置失败:', error);
        this.errorConfig = '获取配置失败，请重试';
      } finally {
        this.loadingConfig = false;
      }
    },

    /**
     * 扁平化配置数据
     * @param {Object} config - 配置对象
     * @param {Array} path - 当前路径
     * @param {Number} depth - 当前深度
     * @returns {Array} 扁平化后的配置项数组
     */
    flattenConfig(config, path = ['SubModules'], depth = 0) {
      let result = [];
      if (!config || typeof config !== 'object') return result;

      for (const key in config) {
        if (Object.prototype.hasOwnProperty.call(config, key)) {
          const currentPath = [...path, key];
          const value = config[key];
          const id = currentPath.join('.');

          // 添加当前项
          result.push({
            id,
            key,
            value,
            path: currentPath,
            depth
          });

          // 如果是对象且不是数组，继续递归
          if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
            result = result.concat(this.flattenConfig(value, currentPath, depth + 1));
          }
        }
      }

      return result;
    },

    /**
     * 切换编辑状态
     * @param {String} id - 配置项ID
     */
    toggleEdit(id) {
      if (id) {
        // 查找要编辑的项
        const item = this.flatConfigItems.find(item => item.id === id);
        if (item) {
          this.editingItemId = id;
          // 深拷贝值，避免直接修改原数据
          this.editValue = this.deepClone(item.value);
        }
      } else {
        this.editingItemId = null;
        this.editValue = null;
      }
    },

    /**
     * 处理值变化
     * @param {Array} path - 属性路径
     * @param {any} value - 新值
     */
    handleValueChange(path, value) {
      this.editValue = value;
    },

    /**
     * 保存编辑
     * @param {String} id - 配置项ID
     */
    saveEdit(id) {
      // 找到对应的配置项
      const index = this.flatConfigItems.findIndex(item => item.id === id);
      if (index !== -1) {
        // 更新配置项的值
        this.flatConfigItems[index].value = this.deepClone(this.editValue);
        // 更新原始配置对象
        this.updateNestedValue(this.configData, this.flatConfigItems[index].path, this.editValue);
        // 关闭编辑状态
        this.toggleEdit(null);
      }
    },

    /**
     * 更新嵌套属性的值
     * @param {Object} obj - 目标对象
     * @param {Array} path - 属性路径
     * @param {any} value - 新值
     */
    updateNestedValue(obj, path, value) {
      if (path.length === 0) return;

      let current = obj;
      for (let i = 0; i < path.length - 1; i++) {
        const key = path[i];
        if (!current.hasOwnProperty(key)) {
          current[key] = {};
        }
        current = current[key];
      }
      current[path[path.length - 1]] = value;
    },

    /**
     * 深拷贝
     * @param {any} value - 要拷贝的值
     * @returns {any} 拷贝后的值
     */
    deepClone(value) {
      if (value === null || typeof value !== 'object') return value;

      if (Array.isArray(value)) {
        return value.map(item => this.deepClone(item));
      } else {
        const cloned = {};
        for (const key in value) {
          if (Object.prototype.hasOwnProperty.call(value, key)) {
            cloned[key] = this.deepClone(value[key]);
          }
        }
        return cloned;
      }
    },

    /**
     * 格式化值显示
     * @param {any} value - 要格式化的值
     * @returns {string} 格式化后的字符串
     */
    formatValue(value) {
      if (value === null) return 'null';
      if (value === undefined) return 'undefined';
      if (typeof value === 'object') {
        if (Array.isArray(value)) {
          return `[Array(${value.length})]`;
        } else {
          return '{Object}';
        }
      } else {
        return String(value);
      }
    },

    /**
     * 获取API文档
     */
    async fetchApiDocs() {
      try {
        this.loadingApiDocs = true;
        // 假设根据应用类型获取对应的OpenAPI定义
        const response = await axios.get(`/define/pipeline/${this.configData.category}/${this.configData.pipeline_name}`);
        this.apiDocs = response.data;
        this.errorApiDocs = '';
      } catch (error) {
        console.error('获取API文档失败:', error);
        this.errorApiDocs = '获取API文档失败，请重试';
      } finally {
        this.loadingApiDocs = false;
      }
    },

    /**
     * 保存配置
     */
    async saveConfig() {
      try {
        await axios.post(`/apps/${this.appId}/config`, this.configData);
        this.$message.success('配置保存成功');
      } catch (error) {
        console.error('保存配置失败:', error);
        this.$message.error('保存配置失败，请重试');
      }
    },

    /**
     * 重置配置
     */
    resetConfig() {
      this.fetchConfig();
    },

    /**
     * 获取组件类型
     * @param {any} value - 参数值
     * @returns {string} 组件类型
     */
    getComponentType(value) {
      if (typeof value === 'boolean') {
        return 'el-switch';
      } else if (typeof value === 'number') {
        return 'el-input-number';
      } else if (Array.isArray(value)) {
        return 'el-select';
      } else {
        return 'el-input';
      }
    },

    /**
     * 获取组件选项
     * @param {string} key - 键名
     * @param {any} value - 参数值
     * @returns {object} 组件选项
     */
    getComponentOptions(key, value) {
      const options = {};
      if (typeof value === 'number') {
        options.min = 0;
      } else if (Array.isArray(value)) {
        options.multiple = true;
        options.options = value.map(item => ({ label: item, value: item }));
      } else if (typeof value === 'boolean') {
        options.activeText = '是';
        options.inactiveText = '否';
      }
      return options;
    },

    /**
     * 获取请求方法类型对应的标签类型
     * @param {string} method - 请求方法
     * @returns {string} 标签类型
     */
    getMethodType(method) {
      const methodTypes = {
        get: 'primary',
        post: 'success',
        put: 'warning',
        delete: 'danger',
        patch: 'info'
      };
      return methodTypes[method] || 'default';
    },

    /**
     * 获取请求参数列表
     * @param {object} requestBody - 请求体定义
     * @returns {array} 参数列表
     */
    getRequestParams(requestBody) {
      // 简化处理，实际应根据OpenAPI规范解析schema
      const params = [];
      if (requestBody && requestBody.content && requestBody.content['application/json']) {
        const schema = requestBody.content['application/json'].schema;
        if (schema && schema.properties) {
          Object.keys(schema.properties).forEach(key => {
            const prop = schema.properties[key];
            params.push({
              name: key,
              type: this.getSchemaType(prop),
              description: prop.description || '',
              required: schema.required && schema.required.includes(key) ? '是' : '否'
            });
          });
        }
      }
      return params;
    },

    /**
     * 获取响应参数列表
     * @param {object} responses - 响应定义
     * @returns {array} 响应参数列表
     */
    getResponseParams(responses) {
      const params = [];
      Object.keys(responses).forEach(code => {
        const response = responses[code];
        let schema = '';
        if (response.content && response.content['application/json']) {
          schema = this.getSchemaDescription(response.content['application/json'].schema);
        }
        params.push({
          code: code,
          description: response.description || '',
          schema: schema
        });
      });
      return params;
    },

    /**
     * 获取schema类型
     * @param {object} schema - schema定义
     * @returns {string} 类型描述
     */
    getSchemaType(schema) {
      if (!schema) {
        return 'unknown';
      }
      if (schema.oneOf) {
        return schema.oneOf.map(item => this.getSchemaType(item)).join(' | ');
      } else if (schema.type === 'array' && schema.items) {
        return `array<${this.getSchemaType(schema.items)}>`;
      } else if (schema.type === 'object') {
        return 'object';
      } else {
        return schema.type || 'unknown';
      }
    },


    /**
     * 获取schema描述
     * @param {object} schema - schema定义
     * @returns {string} 描述
     */
    getSchemaDescription(schema) {
      if (schema.allOf) {
        return schema.allOf.map(item => this.getSchemaDescription(item)).join(' & ');
      } else if (schema.$ref) {
        return `参考: ${schema.$ref.split('/').pop()}`;
      } else if (schema.type === 'object' && schema.properties) {
        const props = Object.keys(schema.properties).map(key => {
          return `${key}: ${this.getSchemaType(schema.properties[key])}`;
        });
        return `{ ${props.join(', ')} }`;
      } else {
        return this.getSchemaType(schema);
      }
    },

    /**
     * 打开API测试对话框
     * @param {string} path - API路径
     * @param {string} method - 请求方法
     * @param {object} methodItem - 方法定义
     */
    openApiTestDialog(path, method, methodItem) {
      this.apiTestDialogTitle = `${method.toUpperCase()} ${path}`;
      this.apiTestPath = path;
      this.apiTestMethod = method;
      this.apiTestParams = [];
      this.apiTestFormData = {};
      this.apiTestResult = null;

      // 解析请求参数
      if (methodItem.requestBody) {
        const schema = methodItem.requestBody.content['application/json'].schema;
        if (schema && schema.properties) {
          Object.keys(schema.properties).forEach(key => {
            const prop = schema.properties[key];
            let defaultValue = null;
            if (prop.default !== undefined) {
              defaultValue = prop.default;
            } else if (prop.type === 'string') {
              defaultValue = '';
            } else if (prop.type === 'number') {
              defaultValue = 0;
            } else if (prop.type === 'boolean') {
              defaultValue = false;
            } else if (prop.type === 'array') {
              defaultValue = [];
            } else if (prop.type === 'object') {
              defaultValue = {};
            }

            this.apiTestParams.push({
              name: key,
              type: this.getSchemaType(prop),
              description: prop.description || '',
              required: schema.required && schema.required.includes(key),
              defaultValue: defaultValue
            });

            this.apiTestFormData[key] = defaultValue;
          });
        }
      }

      this.showApiTestDialog = true;
    },

    /**
     * 提交API测试请求
     */
    async submitApiTest() {
      try {
        this.loadingApiTest = true;
        this.apiTestResult = null;

        const url = `${this.apiTestPath}`;
        const data = this.apiTestFormData;

        let response;
        if (this.apiTestMethod === 'get') {
          response = await axios.get(url, { params: data });
        } else {
          response = await axios[this.apiTestMethod](url, data);
        }

        this.apiTestResult = response.data;
      } catch (error) {
        console.error('API测试失败:', error);
        this.apiTestResult = {
          error: '请求失败',
          message: error.message || '未知错误'
        };
      } finally {
        this.loadingApiTest = false;
      }
    }
  }
}
</script>

<style scoped>
.pipeline-app-detail-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.loading-container,
.error-container {
  padding: 40px 0;
  text-align: center;
}

.config-form-container {
  padding: 20px 0;
}

.flat-config-list {
  max-height: 500px;
  overflow-y: auto;
  padding: 10px;
  margin-bottom: 20px;
}

.config-item {
  margin-bottom: 10px;
  border-bottom: 1px dashed #787878;
  padding-bottom: 10px;
}

.config-item:last-child {
  border-bottom: none;
}

.config-item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  padding: 5px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.config-item-header:hover {
  background-color: #7b7b7b;
}

.config-key {
  font-weight: bold;
  margin-right: 10px;
}

.config-value {
  /* color: #666; */
  flex: 1;
  text-align: left;
  margin-right: 10px;
}

.edit-icon {
  color: #409eff;
}

.config-item-editor {
  margin-top: 10px;
  padding: 10px;
  /* background-color: #f9f9f9; */
  border-radius: 4px;
}

.editor-buttons {
  margin-top: 10px;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.api-docs-container {
  padding: 20px 0;
}

.api-info {
  margin-bottom: 20px;
}

.api-path-item {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.path-header {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.path-url {
  margin-left: 10px;
  font-weight: bold;
  /* color: #333; */
}

.api-method-item {
  margin-left: 20px;
}

.method-description {
  color: #666;
  margin-bottom: 15px;
}

.api-section {
  margin-bottom: 20px;
}

.api-test-container {
  max-height: 500px;
  overflow-y: auto;
}

.api-test-result {
  margin-top: 20px;
  padding: 10px;
  background-color: #f5f5f5;
  border-radius: 4px;
  max-height: 300px;
  overflow-y: auto;
}

.api-test-result pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>