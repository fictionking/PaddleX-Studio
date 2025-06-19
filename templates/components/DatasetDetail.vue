<style scoped>
.upload-section {
  margin-bottom: 20px; 
  padding: 20px; 
  border: 1px dashed var(--el-border-color-light);
  border-radius: 14px;
}
.dataset-detail-container {
  padding: 20px;
}

.tag-font {
  font-size: 14px;
}
.el-menu-custom {
  --el-menu-item-height: 32px;
}
.file-manager {
  display: flex;
  gap: 20px;
  height: calc(100vh - 450px);
  overflow: hidden;
}
.file-tree {
  width: 30%;
  height: 95%;
  overflow-y: scroll;
  flex: 1;
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  padding: 10px;
}
.file-preview {
  width: 70%;
  height: 95%;
  flex: 2;
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  padding: 10px;
}
.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e6e6e6;
}
.empty-preview {
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  color: var(--el-text-color-placeholder);
  background-color: var(--el-bg-color);
  border-radius: 4px;
}
.image-preview {
  text-align: center;
}
.image-preview img {
  max-width: 100%;
  max-height: calc(100vh - 320px);
  object-fit: contain;
}
.text-preview {
  background-color: var(--el-fill-color-light);
  padding: 15px;
  border-radius: 4px;
  font-family: monospace;
  white-space: pre-wrap;
  word-wrap: break-word;
  overflow-y: auto;
  max-height: calc(100vh - 610px);
}
.truncated-warning {
  margin-top: 10px;
}
.context-menu {
  position: absolute;
  z-index: 1000;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}
.el-upload__text-custom {
  margin-bottom: 20px;
}
.btn-bold {
  font-weight: bold;
}
</style>
<template>
  <div class="dataset-detail-container">
    <div class="page-header">
      <div class="page-header-info">
        <h2 class="page-header h2" v-text="currentDataset.name"></h2>
        <el-tag type="info" effect="plain" class="tag-font" v-text="currentDataset.type"></el-tag>
        <el-tag type="success" v-text="currentDataset.category"></el-tag>
        <el-tag type="success" v-text="currentDataset.module_name"></el-tag>
      </div>
      <el-button type="primary" plain @click="$router.push('/dataset')">返回</el-button>
    </div>

    <!-- 文件上传区域 -->
    <div class="upload-section">
      <el-upload class="upload-demo" drag action="" :http-request="handleUpload" :before-upload="beforeUpload"
        :on-success="uploadSuccess" :on-error="uploadError" multiple>
        <div class="el-upload__text-custom">
          <el-icon>
            <UploadFilled />
          </el-icon>将文件拖到此处，或<em>点击上传</em>，支持多文件上传，压缩文件将自动解压
        </div>
        <el-button type="success" plain round class="btn-bold" @click.stop="showDoc">点此查看数据集说明</el-button>
      </el-upload>
    </div>

    <!-- 文件列表区域 -->
    <div class="file-manager">
      <div class="file-tree"
        ref="fileTreeRef">
        <el-tree accordion highlight-current :data="fileTree" :props="treeProps" :expand-on-click-node="true"
          @node-click="handleNodeClick" @node-contextmenu="handleContextMenu" ref="fileTreeRef" v-slot="{ data }">
          <span class="custom-tree-node">
            <span
              :style="data.type === 'directory' ? { color: 'var(--el-color-primary)', fontWeight: 'bold' } : { color: 'var(--el-color-success)' }">
              {{ data.name }}
            </span>
          </span>
        </el-tree>
        <!-- 右键菜单 -->
        <div v-show="contextMenuVisible" ref="contextMenu" class="context-menu"
          :style="{ top: contextMenuPosition.top + 'px', left: contextMenuPosition.left + 'px' }">
          <el-menu @select="handleContextMenuSelect" background-color="#fff" text-color="#333"
            active-text-color="#409EFF" :default-active="''" class="el-menu-custom">
            <el-menu-item index="createDir"><el-icon>
                <FolderAdd />
              </el-icon>创建目录</el-menu-item>
            <el-menu-item index="delete"><el-icon>
                <Delete />
              </el-icon>删除</el-menu-item>
          </el-menu>
        </div>
      </div>

      <!-- 文件预览区域 -->
      <div class="file-preview">
        <div v-if="selectedFile" class="preview-header">
          <h3>{{ selectedFile.name }} [{{ formatFileSize(selectedFile.size) }}]</h3>
          <div class="preview-actions">
            <el-button type="text" @click="downloadFile"><el-icon>
                <Download />
              </el-icon>下载</el-button>
            <el-button type="text" @click="confirmDelete"><el-icon>
                <Delete />
              </el-icon>删除</el-button>
          </div>
        </div>
        <div v-if="!selectedFile" class="empty-preview">
          请选择文件进行预览
        </div>
        <div v-else class="preview-content">
          <div v-if="selectedFile.filetype === 'image'" class="image-preview">
            <img :src="previewContent" alt="预览图片" />
          </div>
          <div v-else-if="selectedFile.filetype === 'text'" class="text-preview">
            <pre>{{ previewContent }}</pre>
            <div v-if="isTruncated" class="truncated-warning">
              <el-alert title="文件内容过长，仅显示部分内容" type="warning" inline show-icon />
            </div>
          </div>
          <div v-else class="unsupported-preview">
            <el-alert title="不支持预览的文件类型" type="info" show-icon :closable="false" />
          </div>
        </div>
      </div>
    </div>

    <!-- 删除确认对话框 -->
    <el-dialog title="确认删除" v-model="deleteDialogVisible" width="30%">
      <p>确定要删除 <strong>{{ selectedFile?.name }}</strong> 吗？</p>
      <span slot="footer" class="dialog-footer">
        <el-button @click="deleteDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="deleteSelectedFile">确定</el-button>
      </span>
    </el-dialog>

    <!-- 批量删除确认对话框 -->
    <el-dialog title="确认批量删除" v-model="batchDeleteDialogVisible" width="30%">
      <p>确定要删除选中的 {{ selectedNodes.length }} 个项目吗？</p>
      <span slot="footer" class="dialog-footer">
        <el-button @click="batchDeleteDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="deleteSelectedNodes">确定</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script type="module">

export default {
  name: 'DatasetDetail',
  props: ['datasetId'],
  data() {
    return {
      currentDataset: {},
      fileTree: [],
      treeProps: {
        children: 'children',
        label: 'name'
      },
      selectedFile: null,
      previewContent: '',
      isTruncated: false,
      deleteDialogVisible: false,
      batchDeleteDialogVisible: false,
      selectedNodes: [],
      contextMenuVisible: false,
      contextMenuPosition: {
        top: 0,
        left: 0
      },
      currentDirectoryPath: '', // 当前选中目录路径
      contextMenuVisible: false
    };
  },
  components: {
    Download: ElementPlusIconsVue.Download,
    Delete: ElementPlusIconsVue.Delete,
    FolderAdd: ElementPlusIconsVue.FolderAdd,
    UploadFilled: ElementPlusIconsVue.UploadFilled,
    QuestionFilled: ElementPlusIconsVue.QuestionFilled
  },
  async created() {
    try {
      const datasetId = this.$route.params.datasetId;
      if (!datasetId) {
        this.$message.error('数据集ID未获取到');
        return;
      }
      const response = await axios.get(`/datasets/${datasetId}`);
      if (response.status === 200) {
        this.currentDataset = response.data;
        this.fetchFileTree();
      } else {
        this.$message.error('获取数据集详情失败：' + response.data.message);
      }
    } catch (error) {
      this.$message.error('网络请求失败：' + error.message);
    }
  },
  computed: {
  },
  mounted() {
    document.addEventListener('click', this.handleClickOutside);
  },
  beforeUnmount() {
    document.removeEventListener('click', this.handleClickOutside);
  },
  methods: {
    /**
     * 格式化文件大小显示
     * @param {Number} bytes - 文件大小(字节)
     * @returns {String} 格式化后的大小字符串
     */
    formatFileSize(bytes) {
      if (bytes === 0) return '0 Bytes';
      const k = 1024;
      const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
    /**
     * 获取文件目录树
     */
    fetchFileTree() {
      axios.get(`/datasets/${this.currentDataset.id}/files`)
        .then(response => {
          this.fileTree = [response.data];
        })
        .catch(error => {
          this.$message.error(`获取文件列表失败: ${error.message}`);
        });
    },

    /**
     * 处理文件上传
     * @param {Object} params - 上传参数
     */
    handleUpload(params) {
      const formData = new FormData();
      formData.append('file', params.file);
      formData.append('directory', this.currentDirectoryPath || '/');

      axios.post(`/datasets/${this.currentDataset.id}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: progressEvent => {
          const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          params.onProgress({ percent });
        }
      })
        .then(() => {
          params.onSuccess();
          this.$message.success('文件上传成功');
          this.fetchFileTree();
        })
        .catch(error => {
          params.onError(error);
          this.$message.error(`上传失败: ${error.message}`);
        });
    },

    /**
     * 上传前检查
     * @param {File} file - 要上传的文件
     * @returns {boolean} 是否允许上传
     */
    beforeUpload(file) {
      // 可以添加文件大小限制等检查
      return true;
    },

    /**
     * 上传成功处理
     */
    uploadSuccess() {
      // 由handleUpload中的then回调处理
    },

    /**
     * 上传失败处理
     * @param {Error} error - 错误对象
     */
    uploadError(error) {
      this.$message.error(`上传失败: ${error.message}`);
    },

    /**
     * 处理节点点击事件，预览文件
     * @param {Object} data - 节点数据
     */
    handleNodeClick(data) {
      if (data.type === 'directory') {
        this.currentDirectoryPath = data.path;
      } else if (data.type === 'file') {
        this.selectedFile = data;
        this.previewFile(data.path);
      }
    },

    /**
     * 预览文件内容
     * @param {string} filePath - 文件路径
     */
    previewFile(filePath) {
      // 对于图片类型，直接使用API URL
      if (filePath.match(/\.(png|jpg|jpeg|gif|bmp|webp)$/i)) {
        this.selectedFile.filetype = 'image';
        this.previewContent = `/datasets/${this.currentDataset.id}/files/${encodeURIComponent(filePath)}`;
        return;
      }

      // 对于文本类型，获取内容
      axios.get(`/datasets/${this.currentDataset.id}/files/${encodeURIComponent(filePath)}`)
        .then(response => {
          const data = response.data;
          this.selectedFile.filetype = 'text';
          this.previewContent = data.content;
          this.isTruncated = data.truncated;
        })
        .catch(error => {
          this.selectedFile.filetype = 'other';
          this.previewContent = '';
        });
    },

    /**
     * 处理右键菜单
     * @param {Event} event - 事件对象
     * @param {Object} data - 节点数据
     */
    handleContextMenu(event, data) {
      event.preventDefault();
      this.selectedNodes = [data];
      this.contextMenuPosition = {
        top: event.clientY,
        left: event.clientX
      };
      this.contextMenuVisible = true;
    },

    /**
     * 处理右键菜单选择事件
     * @param {string} index - 菜单项索引
     */
    handleContextMenuSelect(index) {
      if (index === 'createDir') {
        this.createDirectory();
      } else if (index === 'delete') {
        this.confirmBatchDelete();
      }
      this.contextMenuVisible = false;
    },

    /**
     * 创建新目录
     */
    createDirectory() {
      this.$prompt('请输入目录名称', '创建目录', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputValidator: (value) => {
          if (!value.trim()) {
            return '目录名称不能为空';
          }
          // 检查目录名称中是否包含路径分隔符
          if (value.includes('/') || value.includes('\\')) {
            return '目录名称不能包含斜杠或反斜杠';
          }
          return true;
        }
      }).then(({ value }) => {
        const dirName = value.trim();
        // 直接使用目录名称作为参数，不进行路径拼接
        axios.post(`/datasets/${this.currentDataset.id}/mkdir`, {
          dir_name: dirName
        })
          .then(() => {
            this.$message.success('目录创建成功');
            this.fetchFileTree();
          })
          .catch(error => {
            this.$message.error(`创建目录失败: ${error.response?.data?.error || error.message}`);
          });
      }).catch(() => {
        // 用户取消输入
      });
    },

    /**
     * 确认批量删除
     */
    confirmBatchDelete() {
      if (this.selectedNodes.length > 0) {
        this.batchDeleteDialogVisible = true;
      }
    },
    /**
     * 处理点击菜单外部区域事件
     * @param {Event} event - 点击事件对象
     */
    handleClickOutside(event) {
      if (this.contextMenuVisible && this.$refs.contextMenu && !this.$refs.contextMenu.contains(event.target)) {
        this.contextMenuVisible = false;
      }
    },

    /**
     * 确认删除选中文件
     */
    confirmDelete() {
      if (this.selectedFile) {
        this.deleteDialogVisible = true;
      }
    },

    /**
     * 删除选中文件
     */
    deleteSelectedFile() {
      if (!this.selectedFile) return;

      axios.delete(`/datasets/${this.currentDataset.id}/files/delete`, {
        data: {
          paths: [this.selectedFile.path]
        }
      })
        .then(() => {
          this.$message.success('文件删除成功');
          this.deleteDialogVisible = false;
          this.selectedFile = null;
          this.previewContent = '';
          this.fetchFileTree();
        })
        .catch(error => {
          this.$message.error(`删除失败: ${error.message}`);
        });
    },

    /**
     * 删除选中的多个节点（文件或目录）
     */
    deleteSelectedNodes() {
      if (this.selectedNodes.length === 0) return;

      const paths = this.selectedNodes.map(node => node.path);

      axios.delete(`/datasets/${this.currentDataset.id}/files/delete`, {
        data: { paths }
      })
        .then(() => {
          this.$message.success('选中项目已成功删除');
          this.batchDeleteDialogVisible = false;
          this.fetchFileTree();
        })
        .catch(error => {
          this.$message.error(`删除失败: ${error.message}`);
        });
    },

    /**
     * 下载文件
     */
    downloadFile() {
      if (!this.selectedFile) return;

      window.open(`/datasets/${this.currentDataset.id}/files/dl/${encodeURIComponent(this.selectedFile.path)}`, '_blank');
    },

    showDoc() {
      window.open(`/docs/annotations/${this.currentDataset.type}`, '_blank');
    }
  }
}
</script>