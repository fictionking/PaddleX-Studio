<template>
  <div class="pipeline-app-detail-container">
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
    <el-card>
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
                <el-button v-if="appInfo.status == 'stopped'" type="primary"
                @click.stop="handleAppStart()">启动</el-button>
                <el-button v-if="appInfo.status == 'running'" type="danger" @click.stop="handleAppStop()">停止</el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-tab-pane>

        <!-- API文档标签页 -->
        <el-tab-pane label="API文档" name="api-docs">
          <div class="api-docs-container" style="display: flex; width: 100%; overflow: hidden;">
            <rapi-doc style="flex:1; margin:0px; max-width: 100%; box-sizing: border-box;"
              :spec-url="apiDocsUrl" schema-style="tree" :theme="isDark ? 'dark' : 'light'" show-header='false'
              show-info='false' allow-authentication='false' allow-server-selection='true'
              allow-api-list-style-selection='false' update-route="false"
              render-style="focused" schema-description-expanded="true" ></rapi-doc>
          </div>
        </el-tab-pane>

      </el-tabs>

    </el-card>

  </div>
</template>

<script>
export default {
  inject: ['isDark'],

  name: 'PipeLineAppDetail',
  components: {
    Edit: ElementPlusIconsVue.Edit,
  },
  data() {
    return {
      appId: '',
      appInfo: {},
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
      apiDocsUrl: '',
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
      await this.fetchAppInfo();
      await this.fetchConfig();
      // 只有当configData有值且没有错误时才获取API文档
      if (Object.keys(this.configData).length > 0 && !this.errorConfig) {
        this.fetchApiDocs();
      }
    },
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
      this.apiDocsUrl = `/define/pipeline/${this.configData.category}/${this.configData.pipeline_name}.json`;
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
    handleAppStart() {
      // 显示加载中模态框
      const loading = this.$loading({
        lock: true,
        text: '应用启动中，请稍候...',
        background: 'rgba(0, 0, 0, 0.7)'
      });
      axios.get(`/apps/start/${this.appId}`)
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
  max-height: 700px;
  overflow-y: auto;
  padding: 10px;
  margin-bottom: 20px;
}

.config-item {
  margin-bottom: 0px;
  border-bottom: 1px dashed #78787876;
  padding-bottom: 0px;
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
  background-color: #0000003a;
}

.config-key {
  font-size: 14px;
  font-weight: bold;
  margin-right: 10px;
}

.config-value {
  font-size: 12px;
  opacity: 0.5;
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
  padding: 0px 0;
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