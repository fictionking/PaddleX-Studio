<template>
    <div>
        <div class="page-header">
            <el-button type="primary" plain @click="showCreateDialog">创建数据集</el-button>
        </div>
        <el-row :gutter="20" class="list-container">
            <el-col :span="24">
                <el-card class="list-card" v-for="(dataset, index) in datasets" :key="index"
                    @click="$router.push('/dataset/' + dataset.id)">
                    <div class="listcard content">
                        <!-- 左侧内容 -->
                        <div class="listcard left-section">
                            <div class="listcard base">
                                <h3 class="listcard base h3" v-text="dataset.name"></h3>
                                <el-tag type="info" effect="plain" style="font-size: 14px;"
                                    v-text="dataset.dataset_type?.label || ''"></el-tag>
                            </div>
                            <p class="listcard desc" v-text="dataset.description"></p>
                            <div class="listcard category">
                                <el-tag type="success" v-text="dataset.category?.name || ''"></el-tag>
                                <el-tag type="success" v-text="dataset.module?.name || ''"></el-tag>
                            </div>
                        </div>
                        <!-- 右侧内容 -->
                        <div class="listcard right-section">
                            <p class="listcard updatetime" v-text="dataset.update_time"></p>
                            <div class="listcard actions">
                                <el-button type="text" @click.stop="deleteDataset(dataset.id)">删除</el-button>
                            </div>
                        </div>
                    </div>
                </el-card>
            </el-col>
        </el-row>

        <!-- 创建数据集对话框 -->
        <el-dialog title="创建数据集" v-model="dialogVisible" width="500px">
            <el-form ref="form" :model="form" :rules="rules" label-width="100px">
                <el-form-item label="数据集名称" prop="name">
                    <el-input v-model="form.name"></el-input>
                </el-form-item>
                <el-form-item label="唯一标识" prop="id">
                    <el-input v-model="form.id" placeholder="仅支持大小写字母、数字、-、_"
                        oninput="value=value.replace(/[^a-zA-Z0-9-_]/g,'')"></el-input>
                </el-form-item>
                <el-form-item label="描述" prop="description">
                    <el-input type="textarea" v-model="form.description"></el-input>
                </el-form-item>
                <el-form-item label="类别" prop="category">
                    <el-select v-model="form.category" placeholder="请选择类别" @change="handleCategoryChange">
                        <el-option v-for="item in dataset_types" :key="item.id" :label="item.name"
                            :value="item.id"></el-option>
                    </el-select>
                </el-form-item>
                <el-form-item label="模块" prop="module">
                    <el-select v-model="form.module" placeholder="请选择模块" @change="handleModuleChange">
                        <el-option v-for="module in currentModules" :key="module.id" :label="module.name"
                            :value="module.id"></el-option>
                    </el-select>
                </el-form-item>
                <el-form-item label="数据类型" prop="dataset_type">
                    <el-select v-model="form.dataset_type" placeholder="请选择数据类型">
                        <el-option v-for="type in currentTypes" :key="type.value" :label="type.label"
                            :value="type.value"></el-option>
                    </el-select>
                </el-form-item>
            </el-form>
            <div slot="footer" class="dialog-footer">
                <el-button @click="resetForm('form')">取消</el-button>
                <el-button type="primary" @click="submitForm('form')">确定</el-button>
            </div>
        </el-dialog>

    </div>
</template>

<script>
export default {
    data() {
        return {
            datasets: [],  // 数据集数据列表
            dialogVisible: false,  // 创建对话框显示状态
            form: {  // 创建数据集表单数据
                name: '',
                description: '',
                category: '',
                module: '',
                dataset_type: '',
            },
            rules: {  // 表单验证规则
                name: [{ required: true, message: '请输入数据集名称', trigger: 'blur' }],
                id: [
                    { required: true, message: '请输入唯一标识', trigger: 'blur' },
                    { pattern: /^[a-zA-Z0-9-_]+$/, message: '仅支持大小写字母、数字、-、_', trigger: 'blur' }
                ],
                module: [{ required: true, message: '请选择模块', trigger: 'change' }],
                dataset_type: [{ required: true, message: '请选择数据类型', trigger: 'change' }],
                category: [{ required: true, message: '请选择类别', trigger: 'change' }]
            },
            currentModules: [],
            currentTypes: [],
            dataset_types: []
        }
    },
    mounted() {
        fetch('/define/dataset_types')
            .then(response => response.json())
            .then(data => {
                this.dataset_types = data;
            })
            .catch(error => {
                console.error('获取数据集类型定义失败:', error);
            });
        this.autofresh();  // 自动刷新数据集数据
    },
    beforeUnmount() {
        // 组件卸载时清除定时器
        if (this.datasetsPollingTimer) {
            clearInterval(this.datasetsPollingTimer);
            this.datasetsPollingTimer = null;
        }
    },
    methods: {
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
        /**
         * 自动刷新数据集列表
         * 设置定时器定期调用loadDatasets方法刷新数据
         */
        autofresh() {
            this.datasetsPollingTimer = setInterval(() => {
                this.loadDatasets();
            }, 10000);
            this.loadDatasets();
        },
        // 删除数据集
        // 显示创建对话框
        // 处理类别变化
        handleCategoryChange(categoryId) {
            if (categoryId) {
                // 根据ID查找类别对象
                const category = this.dataset_types.find(item => item.id === categoryId);
                this.currentModules = category ? category.modules || [] : [];
                // 重置模块和数据类型选择
                this.form.module = '';
                this.form.dataset_type = '';
            }
        },

        // 处理模块变化
        /**
         * 处理模块变化
         * @param {string} moduleId - 选中的模块ID
         */
        handleModuleChange(moduleId) {
            if (moduleId) {
                // 根据ID查找模块对象
                const module = this.currentModules.find(item => item.id === moduleId);
                this.currentTypes = module ? module.dataset || [] : [];
                // 重置数据类型选择
                this.form.dataset_type = '';
            }
        },

        /**
         * 显示创建数据集对话框
         */
        showCreateDialog() {
            this.dialogVisible = true;
        },

        /**
         * 重置表单
         * @param {string} formName - 表单名称
         */
        resetForm(formName) {
            this.$refs[formName].resetFields();
            this.dialogVisible = false;
        },

        /**
         * 提交表单创建数据集
         * @param {string} formName - 表单名称
         */
        submitForm(formName) {
            this.$refs[formName].validate((valid) => {
                if (valid) {
                    // 查找选中的类别、模块和数据类型对象
                    const category = this.dataset_types.find(item => item.id === this.form.category);
                    const module = this.currentModules.find(item => item.id === this.form.module);
                    const datasetType = this.currentTypes.find(item => item.value === this.form.dataset_type);

                    const newDataset = {
                        id: this.form.id,
                        name: this.form.name,
                        description: this.form.description,
                        category: {
                            id: category.id,
                            name: category.name,
                        },
                        module: {
                            id: module.id,
                            name: module.name,
                        },
                        dataset_type: {
                            value: datasetType.value,
                            label: datasetType.label,
                            convert_enable: datasetType.convert_enable,
                        }
                    };

                    axios.post('/datasets/new', newDataset, {
                        headers: {
                            'Content-Type': 'application/json'
                        }
                    })
                        .then(response => {
                            this.$message({ message: '数据集创建成功', type: 'success' });
                            this.dialogVisible = false;
                            this.loadDatasets(); // 刷新数据集列表
                        })
                        .catch(error => {
                            console.error('创建数据集失败:', error.response.data.error);
                            this.$message({ message: error.response.data.error, type: 'error' });
                        });
                } else {
                    return false;
                }
            });
        },
        // 删除数据集
        deleteDataset(datasetId) {
            if (!confirm('确定要删除该数据集吗？')) return;
            fetch(`/datasets/${datasetId}`, { method: 'DELETE' })
                .then(response => {
                    if (response.ok) {
                        this.loadDatasets(); // 删除成功后刷新列表
                    }
                })
                .catch(error => {
                    console.error('删除数据集失败:', error);
                });
        }

    }
}
</script>