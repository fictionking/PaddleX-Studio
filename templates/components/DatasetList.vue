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
                                    v-text="dataset.type"></el-tag>
                            </div>
                            <p class="listcard desc" v-text="dataset.description"></p>
                            <div class="listcard category">
                                <el-tag type="success" v-text="dataset.category"></el-tag>
                                <el-tag type="success" v-text="dataset.dataset_type_name"></el-tag>
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
                        <el-option v-for="item in dataset_types" :key="item.value" :label="item.label"
                            :value="item.value"></el-option>
                    </el-select>
                </el-form-item>
                <el-form-item label="模块" prop="dataset_type">
                    <el-select v-model="form.dataset_type" placeholder="请选择模块" @change="handleModuleChange">
                        <el-option v-for="module in currentModules" :key="module.value" :label="module.label"
                            :value="module.value"></el-option>
                    </el-select>
                </el-form-item>
                <el-form-item label="数据类型" prop="type">
                    <el-select v-model="form.type" placeholder="请选择数据类型">
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

<script type="module">

export default {
    data() {
        return {
            datasets: [],  // 数据集数据列表
            dialogVisible: false,  // 创建对话框显示状态
            form: {  // 创建数据集表单数据
                name: '',
                description: '',
                category: '',
                dataset_type: '',
                dataset_type_name: '',
                type: ''
            },
            rules: {  // 表单验证规则
                name: [{ required: true, message: '请输入数据集名称', trigger: 'blur' }],
                id: [
                    { required: true, message: '请输入唯一标识', trigger: 'blur' },
                    { pattern: /^[a-zA-Z0-9-_]+$/, message: '仅支持大小写字母、数字、-、_', trigger: 'blur' }
                ],
                dataset_type: [{ required: true, message: '请选择模块', trigger: 'change' }],
                type: [{ required: true, message: '请选择数据类型', trigger: 'change' }],
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
        handleCategoryChange() {
            const category = this.dataset_types.find(item => item.value === this.form.category);
            if (category) {
                this.currentModules = category.modules || [];
                this.currentTypes = category.types || [];
                // 重置模块和数据类型选择
                this.form.dataset_type = '';
                this.form.dataset_type_name = '';
                this.form.type = '';
            }
        },

        // 处理模块变化
        handleModuleChange() {
            const module = this.currentModules.find(item => item.value === this.form.dataset_type);
            if (module) {
                this.form.dataset_type_name = module.label;
            }
        },

        showCreateDialog() {
            this.dialogVisible = true;
        },

        // 重置表单
        resetForm(formName) {
            this.$refs[formName].resetFields();
            this.dialogVisible = false;
        },

        // 提交表单
        submitForm(formName) {
            this.$refs[formName].validate((valid) => {
                if (valid) {
                    // 生成唯一ID
                    // 使用用户输入的ID而非自动生成
                    const newDataset = { ...this.form };

                    fetch('/datasets/new', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(newDataset)
                    })
                        .then(response => response.json())
                        .then(data => {
                            this.$message({ message: '数据集创建成功', type: 'success' });
                            this.dialogVisible = false;
                            this.loadDatasets(); // 刷新数据集列表
                        })
                        .catch(error => {
                            console.error('创建数据集失败:', error);
                            this.$message({ message: '创建数据集失败', type: 'error' });
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