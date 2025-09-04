<template>
    <div>
        <div class="page-header">
            <el-button type="primary" plain @click="showCreateDialog">新建工作流</el-button>
        </div>
        <el-row :gutter="20" class="list-container">
            <el-col :span="24">
                <el-card class="list-card" v-for="(workflow, index) in workflows" :key="index"
                    @click="goToDetail(workflow.id)">
                    <div class="listcard content">
                        <!-- 左侧内容 -->
                        <div class="listcard left-section">
                            <div class="listcard base">
                                <h3 class="listcard base h3" v-text="workflow.name"></h3>
                                <el-tag :type="workflow.status === 'running' ? 'success' : 'info'" effect="plain" 
                                    style="font-size: 14px;"
                                    v-text="workflow.status === 'running' ? '运行中' : '已停止' || ''"></el-tag>
                            </div>
                            <p class="listcard desc" v-text="workflow.description"></p>
                        </div>
                        <!-- 右侧内容 -->
                        <div class="listcard right-section">
                            <p class="listcard updatetime" v-text="workflow.update_time"></p>
                            <div class="listcard actions">
                                <el-button type="text" @click.stop="deleteWorkflow(workflow.id, workflow.name)">删除</el-button>
                            </div>
                        </div>
                    </div>
                </el-card>
            </el-col>
        </el-row>

        <!-- 新建工作流对话框 -->
        <el-dialog title="创建工作流" v-model="dialogVisible" width="500px">
            <el-form ref="form" :model="form" :rules="rules" label-width="100px">
                <el-form-item label="唯一标识" prop="id">
                    <el-input v-model="form.id" placeholder="请输入唯一标识（英文、数字、下划线组合，不超过50个字符）"></el-input>
                </el-form-item>
                <el-form-item label="工作流名称" prop="name">
                    <el-input v-model="form.name"></el-input>
                </el-form-item>
                <el-form-item label="描述" prop="description">
                    <el-input type="textarea" v-model="form.description"></el-input>
                </el-form-item>
            </el-form>
            <template #footer>
                <div class="dialog-footer">
                    <el-button @click="resetForm('form')">取消</el-button>
                    <el-button type="primary" @click="submitForm('form')">确定</el-button>
                </div>
            </template>
        </el-dialog>
    </div>
</template>

<script>
export default {
    data() {
        return {
            workflows: [],  // 工作流数据列表
            dialogVisible: false,  // 创建对话框显示状态
            form: {  // 创建工作流表单数据
                id: '',
                name: '',
                description: '',
            },
            rules: {  // 表单验证规则
                id: [
                    { required: true, message: '请输入唯一标识', trigger: 'blur' },
                    { pattern: /^[a-zA-Z0-9_]+$/, message: '唯一标识只能包含字母、数字和下划线', trigger: 'blur' },
                    { max: 50, message: '唯一标识长度不能超过50个字符', trigger: 'blur' }
                ],
                name: [{ required: true, message: '请输入工作流名称', trigger: 'blur' }]
            },
            datasetsPollingTimer: null
        }
    },
    mounted() {
        this.autofresh();  // 自动刷新工作流数据
    },
    beforeUnmount() {
        // 组件卸载时清除定时器
        if (this.datasetsPollingTimer) {
            clearInterval(this.datasetsPollingTimer);
            this.datasetsPollingTimer = null;
        }
    },
    methods: {
        loadWorkflows() {
            // 调用API获取工作流数据
            fetch('/workflows')
                .then(response => response.json())
                .then(data => {
                    this.workflows = data;
                })
                .catch(error => {
                    console.error('获取工作流数据失败:', error);
                });
        },
        
        /**
         * 自动刷新工作流列表
         * 设置定时器定期调用loadWorkflows方法刷新数据
         */
        autofresh() {
            this.datasetsPollingTimer = setInterval(() => {
                this.loadWorkflows();
            }, 10000);
            this.loadWorkflows();
        },
        
        /**
         * 跳转到工作流详情页
         * @param {string} workflowId - 工作流ID
         */
        goToDetail(workflowId) {
            this.$router.push('/workflow/' + workflowId);
        },
        
        /**
         * 显示创建工作流对话框
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
         * 提交表单创建工作流
         * @param {string} formName - 表单名称
         */
        submitForm(formName) {
            this.$refs[formName].validate((valid) => {
                if (valid) {
                    const newWorkflow = {
                        id: this.form.id,
                        name: this.form.name,
                        description: this.form.description
                    };
                    
                    fetch('/workflows', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(newWorkflow)
                    })
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                this.$message({ message: '工作流创建成功', type: 'success' });
                                this.dialogVisible = false;
                                this.loadWorkflows(); // 刷新工作流列表
                            } else {
                                throw new Error(data.error || '创建工作流失败');
                            }
                        })
                        .catch(error => {
                            console.error('创建工作流失败:', error);
                            this.$message({ message: error.message, type: 'error' });
                        });
                } else {
                    return false;
                }
            });
        },
        
        /**
         * 删除工作流
         * @param {string} workflowId - 工作流ID
         * @param {string} workflowName - 工作流名称
         */
        deleteWorkflow(workflowId, workflowName) {
            if (!confirm(`确定要删除工作流「${workflowName}」吗？`)) return;
            fetch(`/workflows/${workflowId}`, { method: 'DELETE' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        this.$message({ message: '工作流删除成功', type: 'success' });
                        this.loadWorkflows(); // 删除成功后刷新列表
                    } else {
                        throw new Error(data.error || '删除工作流失败');
                    }
                })
                .catch(error => {
                    console.error('删除工作流失败:', error);
                    this.$message({ message: error.message, type: 'error' });
                });
        }
    }
};
</script>

<style scoped>

.listcard.content {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
/* 
.listcard.left-section {
    flex: 1;
    overflow: hidden;
}

.listcard.base {
    display: flex;
    align-items: center;
    margin-bottom: 8px;
}

.listcard.base.h3 {
    margin: 0;
    margin-right: 10px;
    font-size: 16px;
    font-weight: 500;
} */

.listcard.desc {
    margin: 0;
    color: #666;
    font-size: 14px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
/* 
.listcard.category {
    margin-top: 8px;
}

.listcard.category .el-tag {
    margin-right: 5px;
}

.listcard.right-section {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
} */

.listcard.updatetime {
    margin: 0;
    color: #999;
    font-size: 12px;
    margin-bottom: 10px;
}
/* 
.listcard.actions {
    display: flex;
} */

</style>