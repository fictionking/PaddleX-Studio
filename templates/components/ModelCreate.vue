<template>
  <!-- 创建模型对话框 -->
  <el-dialog ref="newModelDlg" title="新建模型训练配置" destroy-on-close width="50%">
    <el-form ref="newModelForm" :model="newModelFormData" :rules="formRules" label-width="120px">
      <div style="display: flex;gap: 20px;">
        <div style="flex: 1;">
          <el-form-item label="模型名称" prop="name" required>
            <el-input v-model="newModelFormData.name"></el-input>
          </el-form-item>
          <el-form-item label="唯一标识" prop="id" required>
            <el-input v-model="newModelFormData.id" placeholder="仅支持大小写字母、数字、-、_"
              oninput="value=value.replace(/[^a-zA-Z0-9-_]/g,'')"></el-input>
          </el-form-item>
          <el-form-item label="模型描述" prop="description" required>
            <el-input type="textarea" v-model="newModelFormData.description"></el-input>
          </el-form-item>
          <el-form-item label="类别" prop="category" required>
            <el-select v-model="newModelFormData.category" placeholder="请选择类别" @change="handleCategoryChange">
              <el-option v-for="cat in categoryOptions" :key="cat.category" :label="cat.category"
                :value="cat.category"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="模块" prop="module_id" required>
            <el-select v-model="newModelFormData.module_id" placeholder="请选择模块" @change="handleModuleChange">
              <el-option v-for="mod in moduleOptions" :key="mod.name" :label="mod.name" :value="mod.id"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="预训练模型" prop="pretrained" required>
            <el-select v-model="newModelFormData.pretrained" placeholder="请选择预训练模型" @change="handlePretrainedChange">
              <el-option v-for="pretrained in pretrainedOptions" :key="pretrained.name" :label="pretrained.name"
                :value="pretrained.name"></el-option>
            </el-select>
          </el-form-item>
        </div>
        <div style="flex: 1; height: 100%;">
          <el-text tag="b">模块描述</el-text>
          <el-input type="textarea" v-model="moduleDescription" readonly :rows="6"></el-input>
          <el-text tag="b">预训练模型描述</el-text>
          <el-input type="textarea" v-model="pretrainedDescription" readonly :rows="6"></el-input>
        </div>
      </div>
    </el-form>
    <div slot="footer" class="dialog-footer">
      <el-button type="primary" @click="handleModelSave">保存</el-button>
    </div>
  </el-dialog>
</template>

<script type="module">
export default {
  props: ['models'],
  data() {
    return {
      newModelFormData: {
        name: '',
        id: '',
        description: '',
        category: '',
        module_id: '',
        module_name: '',
        pretrained: ''
      },
      formRules: {
        name: [
          { required: true, message: '请输入模型名称', trigger: 'blur' }
        ],
        id: [
          { required: true, message: '请输入唯一标识', trigger: 'blur' },
          { pattern: /^[a-zA-Z0-9-_]+$/, message: '仅支持大小写字母、数字、-、_', trigger: 'blur' },
          { validator: this.checkModelUniqueId, trigger: 'blur' }
        ],
        description: [
          { required: true, message: '请输入模型描述', trigger: 'blur' }
        ],
        category: [
          { required: true, message: '请选择类别', trigger: 'change' }
        ],
        module_id: [
          { required: true, message: '请选择模块', trigger: 'change' }
        ],
        pretrained: [
          { required: true, message: '请选择预训练模型', trigger: 'change' }
        ]
      },
      categoryOptions: [], // 类别选项列表
      moduleOptions: [], // 模块选项列表
      pretrainedOptions: [], // 预训练模型选项列表
      moduleDescription: '', // 当前模块描述
      pretrainedDescription: '' // 当前预训练模型描述
    };
  },
  mounted() {
    // 加载modules.json数据填充选项
    fetch('/modules.json')
      .then(res => res.json())
      .then(data => {
        this.categoryOptions = data;
      });

  },
  methods: {
    handleCategoryChange(val) {
      // 从categoryOptions中找到当前选中类别的modules属性
      const currentCategory = this.categoryOptions.find(cat => cat.category === val);
      if (currentCategory) {
        this.moduleOptions = currentCategory.modules;
      } else {
        this.moduleOptions = [];
      }
      this.pretrainedOptions = [];
      this.newModelFormData.module = '';
      this.newModelFormData.pretrained = '';
      this.moduleDescription = '';
      this.pretrainedDescription = '';
    },
    handleModuleChange(val) {
      // 从moduleOptions中找到当前选中模块的pretrained属性
      const currentModule = this.moduleOptions.find(mod => mod.id === val);
      if (currentModule) {
        this.pretrainedOptions = currentModule.pretrained;
        this.moduleDescription = currentModule.description;
        this.newModelFormData.module_name = currentModule.name;
      } else {
        this.pretrainedOptions = [];
      }
      this.newModelFormData.pretrained = '';
      this.pretrainedDescription = '';
    },
    handlePretrainedChange(val) {
      // 从pretrainedOptions中找到当前选中预训练模型的description属性
      const currentPretrained = this.pretrainedOptions.find(pretrained => pretrained.name === val);
      if (currentPretrained) {
        this.pretrainedDescription = currentPretrained.description + '\n' + currentPretrained.model_size;
      }
    },
    checkModelUniqueId(rule, value, callback) {
      if (!value) {
        return callback(new Error('唯一标识不能为空'));
      }
      const isExist = this.models.some(model => model.id === value);
      if (isExist) {
        callback(new Error('该唯一标识已存在'));
      } else {
        callback();
      }
    },
    handleModelSave() {
      // 保存模型配置
      this.$refs.newModelForm.validate(valid => {
        if (valid) {
          // 调用后端接口保存模型配置（需与app.py的save_model_config接口对应）
          const modelId = this.newModelFormData.id;
          fetch('/models/new', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(this.newModelFormData)
          }).then(res => res.json())
            .then(result => {
              if (result.code === 200) {
                this.newModelDialogVisible = false;
                this.newModelFormData = {
                  name: '',
                  id: '',
                  description: '',
                  category: '',
                  module_id: '',
                  module_name: '',
                  pretrained: ''
                };
                this.$router.push(`/model/detail/${modelId}`);
              }
            });
            // this.$refs.newModelForm.resetFields();
            // this.$emit('close');
        } else {
          // 校验失败提示
          console.error('表单校验失败');
          return false;
        }

      });
    }
  }
}
</script>