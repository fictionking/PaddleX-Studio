const { createApp } = Vue
const { ElMessage, ElIcon, Document, Folder, ElCard, ElForm } = ElementPlus  // 新增导入ElCard组件

createApp({
    data() {
        return {
            currentPage: 'model',  // 默认显示模型列表页面
            modelPage: 'model_list',  // 默认显示模型列表页面
            currentModel: null,  // 当前选中的模型
            models: [],  // 初始化模型数组
            datasets: [],  // 新增数据集数组
            newModelDialogVisible: false,
            datasetCheck: {
                showDatasetDialog: false,
                checkResult: null,
                checkingDataset: false,
                checkPass: false,
                showCheckResult: false,
                checkLog: ''
            },
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
            categoryOptions: [],
            moduleOptions: [],
            pretrainedOptions: [],
            moduleDescription: '',
            pretrainedDescription: ''
        }
    },
    mounted() {
        // 页面加载后调用API获取模型数据
        this.loadModels();
        this.loadDatasets();
        // 加载modules.json数据填充选项
        fetch('/modules.json')
            .then(res => res.json())
            .then(data => {
                this.categoryOptions = data;
            });

    },
    methods: {
        async handleCheckDataset() {
            if (this.checkingDataset) return;
            this.datasetCheck.checkingDataset = true;
            this.datasetCheck.checkPass = false;
            await this.$nextTick();
            try {
                const response = await axios.post(`/models/${this.currentModel.id}/check`, {
                    dataset_id: this.currentModel.dataset_id
                });
                if (response.data.code === 200) {
                    this.datasetCheck.checkResult = response.data.data;
                    this.datasetCheck.checkPass = this.datasetCheck.checkResult.check_pass;
                }
                this.datasetCheck.showCheckResult = true;
                if (!this.checkPass) {
                    try {
                        const logResponse = await axios.get(`/models/${this.currentModel.id}/check/check_dataset.log`);
                        this.datasetCheck.checkLog = logResponse.data;
                    } catch (error) {
                        this.$message.error('获取日志失败：' + error.message);
                    }
                }
            } catch (error) {
                this.$message.error('网络请求失败：' + error.message);
            } finally {
                this.datasetCheck.checkingDataset = false;
            }

        },
        navigateTo(page) {
            this.currentPage = page;
        },
        loadDatasets() {
            // 调用API获取数据集数据
            fetch('/datasets')
                .then(response => response.json())
                .then(data => {
                    this.datasets = data;
                })
                .catch(error => {
                    console.error('获取数据集数据失败:', error);
                });
        },
        loadModels() {
            // 调用API获取模型数据
            fetch('/models')
                .then(response => response.json())
                .then(data => {
                    this.models = data;
                })
                .catch(error => {
                    console.error('获取模型数据失败:', error);
                });
        },
        modelTrain(modelId) {
            // 调用API获取模型详细信息（GET方法无需body，通过URL参数传递modelId）
            fetch(`/models/${modelId}`, {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' }
            }).then(res => res.json())
                .then(result => {
                    // 将获取到的模型数据赋值给currentModel
                    this.currentModel = result;
                    this.modelPage = 'model_detail';
                });
        },
        handleModelSave() {
            this.$refs.newModelForm.validate((valid) => {
                if (valid) {
                    // 调用后端接口保存模型配置（需与app.py的save_model_config接口对应）
                    modelId = this.newModelFormData.id;
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
                                // 刷新模型列表（假设存在刷新方法）
                                this.loadModels();
                                this.modelTrain(modelId);
                            }
                        });
                } else {
                    // 校验失败提示
                    console.error('表单校验失败');
                    return false;
                }
            });

        },
        handleModelDelete(modelId) {
            this.$confirm('确定要删除该模型吗？', '提示', {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning'
            }).then(() => {
                axios.get(`/models/${this.currentModel.id}/delete`)
                    .then(response => {
                        if (response.data.code === 200) {
                            this.loadModels();
                            this.$message.success('删除成功');
                        } else {
                            this.$message.error(response.data.message);
                        }
                    })
                    .catch(error => {
                        this.$message.error('删除失败');
                        console.error(error);
                    });
            }).catch(() => {
                this.$message.info('已取消删除');
            });
        },
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
        handleDatasetChange(val) {
            const selectedDataset = this.datasets.find(dataset => dataset.id === val);
            if (selectedDataset) {
                this.currentModel.dataset_name = selectedDataset.name;
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
        }
    },
    components: {
        ElIcon, Document, Folder, ElCard, ElForm,  // 注册ElForm及ElCard组件（已正确导入）
        'ico_helpfilled': ElementPlusIconsVue.HelpFilled,
        'ico_menu': ElementPlusIconsVue.Menu,
        'ico_delete': ElementPlusIconsVue.Delete
    }
}).use(ElementPlus).mount('#app')