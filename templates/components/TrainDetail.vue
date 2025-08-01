<template>
    <div>
        <div class="page-header">
            <div class="page-header-info">
                <h2 class="page-header h2" v-text="currentModel.name"></h2>
                <el-tag type="info" effect="plain" style="font-size: 14px;" v-text="currentModel.pretrained"></el-tag>
                <el-tag type="success" v-text="currentModel.category"></el-tag>
                <el-tag type="success" v-text="currentModel.module_name"></el-tag>
            </div>
            <el-button type="primary" plain @click="handleBack">返回</el-button>
        </div>
        <p class="model-desc" v-text="currentModel.description"></p>
        <br>
        <div v-if="currentModel">
            <div v-if="currentModel.status !== 'config'">
                <el-scrollbar ref="logScrollbar" class="log-scrollbar">
                    <pre ref="logPre" class="log-pre"><code>{{ trainLog }}</code></pre>
                </el-scrollbar>
            </div>
            <div v-if="currentModel.status === 'config'">
                <div class="step-header">
                    <el-steps class="steps" :space="300" :active="currentModel.step" align-center
                        finish-status="success" simple>
                        <el-step title="数据准备"></el-step>
                        <el-step title="参数准备"></el-step>
                        <el-step title="提交训练"></el-step>
                    </el-steps>
                </div>
                <div class="step-body">
                    <!-- 数据准备 -->
                    <div v-if="currentModel.step === 0" class="data-prep-container">
                        <div class="dataset-selector">
                            <span>选择数据集</span>
                            <el-select v-model="dataset_id" placeholder="请选择训练数据集"
                                style="flex: 1;" :disabled="processing">
                                <el-option v-for="dataset in datasets" :key="dataset.id" :label="dataset.name"
                                    :value="dataset.id"></el-option>
                            </el-select>
                            <el-button type="primary" @click="handleCheckDataset"
                                :disabled="!dataset_id || processing">检查数据集</el-button>
                        </div>
                        <div v-if="checking">
                            <el-steps class="steps" :space="300" :active="checkstep" align-center
                                finish-status="success">
                                <el-step title="提交任务" description="提交数据集检查任务"></el-step>
                                <el-step title="格式校验" description="校验数据集格式是否正确"></el-step>
                                <el-step title="数据集保存" description="保存校验通过的数据集"></el-step>
                                <el-step title="完成" description="数据集检查完成"></el-step>
                            </el-steps>
                        </div>
                        <div v-show="showCheckResult" class="check-result-card">
                            <el-card shadow="never">
                                <h3>检查状态：<el-tag :type="checkPass ? 'success' : 'danger'"
                                        v-text="checkPass ? '通过' : '未通过'">
                                    </el-tag></h3>
                                <el-input v-if="!checkPass" v-model="checkLog" style="width: 100%;" :rows="20"
                                    type="textarea" placeholder="检查日志内容将显示在此处" />
                                <component v-if="checkResult" :is="checkShowComponent" :check-result="checkResult"
                                    v-show="checkPass">
                                </component>
                            </el-card>
                        </div>
                    </div>
                    <!-- 参数准备 -->
                    <div v-if="currentModel.step === 1" class="param-setting">
                        <h4>训练参数设置</h4>
                        <el-form :model="training" label-width="auto">
                            <el-form-item v-for="param in trainParams" :key="param['name']" :label="param['label']">
                                <el-input v-model="training[param['name']]" />
                                <div class="param-tip">{{ param['description'] }}</div>
                            </el-form-item>
                        </el-form>
                    </div>
                    <!-- 提交训练 -->
                    <div v-if="currentModel.step === 2" style="align-items: center;text-align: center;">
                        <h4>选择训练运行位置</h4>
                        <el-radio-group v-model="runLocation">
                            <el-radio label="local">本地</el-radio>
                            <el-radio label="distributed">分布式(暂未实现)</el-radio>
                        </el-radio-group>
                    </div>
                </div>
            </div>
            <div class="step-footer">
                <el-button type="primary" @click="handleModelCfgNext" :disabled="processing">{{
                    currentModel.status === 'config' ? (currentModel.step === 2 ? '提交训练' : '下一步') :
                        ['finished', 'aborted', 'failed'].includes(currentModel.status) ? '重新训练' : '中断训练'
                }}</el-button>
                <el-button v-if="currentModel.status === 'finished'" type="primary" @click="download">下载模型</el-button>
                <el-button v-if="currentModel.status === 'finished'" type="primary"
                    @click="openCreateAppDialog">创建应用</el-button>
            </div>
        </div>
        <!-- 新增应用创建对话框 -->
        <el-dialog v-model="showCreateAppDialog" title="模型应用" width="600px">
            <el-form ref="appForm" :model="newAppFormData" :rules="formRules" label-width="100px">
                <el-form-item label="名称" prop="name">
                    <el-input v-model="newAppFormData.name" placeholder="请输入应用名称"></el-input>
                </el-form-item>
                <el-form-item label="唯一标识" prop="id">
                    <el-input v-model="newAppFormData.id" placeholder="请输入唯一标识"></el-input>
                </el-form-item>
            </el-form>
            <div slot="footer" class="dialog-footer">
                <el-button @click="showCreateAppDialog = false">取消</el-button>
                <el-button type="primary" @click="submitAppForm">确定</el-button>
            </div>
        </el-dialog>
    </div>
</template>


<script type="module">

export default {
    props: ['modelId'],
    emits: [],
    data() {
        return {
            currentModel: {},
            datasets: [],
            dataset_id: '',
            showDatasetDialog: false,
            checking: false,
            checkstep: 0,
            checkResult: null,
            checkingDataset: false,
            checkPass: false,
            showCheckResult: false,
            checkLog: '',
            trainParams: [],
            showTrainResult: false,
            trainResult: null,
            trainLog: '',
            processing: false,
            training: {},
            trainLog: '',  // 训练日志内容
            runLocation: 'local',  // 训练运行位置默认值（local/distributed
            newAppFormData: {
                name: '',
                id: '',
                model_id: ''
            },
            showCreateAppDialog: false,
        }
    },
    async created() {
        try {
            const modelId = this.$route.params.modelId; // 从路由参数获取modelId
            if (!modelId) {
                this.$message.error('模型ID未获取到');
                return;
            }
            const response = await axios.get(`/models/${modelId}`);
            if (response.status === 200) {
                this.currentModel = response.data;
                // 如果当前模型是训练状态，启动日志轮询
                switch (this.currentModel.status) {
                    case 'config':
                        if (this.currentModel.step === 1) {
                            this.fetchTrainParams();
                        } else {
                            this.loadDatasets();
                        }
                        break;
                    case 'queued':
                    case 'training':
                        this.startLogPolling();
                        break;
                    case 'finished':
                    case 'aborted':
                    case 'failed':
                        this.fetchTrainLog();
                        break;
                }
            } else {
                this.$message.error('获取模型详情失败：' + response.data.message);
            }
        } catch (error) {
            this.$message.error('网络请求失败：' + error.message);
        }
    },
    beforeUnmount() {
        // 组件卸载时清除定时器
        if (this.logPollingTimer) {
            clearInterval(this.logPollingTimer);
            this.logPollingTimer = null;
        }
    },
    watch: {
        trainLog() {
            // 日志更新时自动滚动到最底部
            this.$nextTick(() => {
                const scrollbar = this.$refs.logScrollbar;
                if (scrollbar) {
                    const wrap = scrollbar.$el.querySelector('.el-scrollbar__wrap');
                    if (wrap) {
                        wrap.scrollTop = wrap.scrollHeight;
                    }
                }
            });
        }
    },
    computed: {
        checkShowComponent() {
            const { defineAsyncComponent } = Vue
            // 检查checkResult是否已加载module_id
            if (!this.checkResult?.show_type) {
                // 未加载时返回空组件或加载提示（可选）
                return null;
            }
            // 数据加载完成后，使用defineAsyncComponent动态导入目标组件
            return defineAsyncComponent(() => import(`/components/check_show_type/${this.checkResult.show_type}.vue`));
        }
    },
    methods: {
        handleBack() {
            this.$nextTick(() => {
                this.$router.push('/train');
            });
        },
        /**
         * 从API获取训练参数定义
         * 调用/train/params接口获取参数并更新组件状态
         */
        fetchTrainParams() {
            axios.get(`/models/${this.currentModel.id}/train/params`)
                .then(response => {
                    this.trainParams = response.data;
                    // 初始化表单数据
                    this.trainParams.forEach(item => {
                        this.training[item['name']] = item['value'];
                    });
                })
                .catch(error => {
                    console.error('获取训练参数失败:', error);
                });
        },
        startLogPolling() {
            // 每2秒获取一次日志
            this.logPollingTimer = setInterval(() => {
                this.fetchTrainLog();
            }, 2000);
            // 立即获取一次初始日志
            this.fetchTrainLog();
        },
        fetchTrainLog() {
            // 调用后端日志接口
            axios.get(`/models/${this.currentModel.id}/train/log`)
                .then(res => {
                    if (res.data.code === 200) {
                        this.trainLog = res.data.data;  // 更新日志内容
                        this.currentModel.status = res.data.status;  // 更新模型状态
                    }
                })
                .catch(err => {
                    console.error('获取训练日志失败:', err);
                });
        },
        loadDatasets() {
            // 调用API获取数据集数据
            fetch(`/datasets?category=${this.currentModel.category}&module=${this.currentModel.module_id}`)
                .then(response => response.json())
                .then(data => {
                    this.datasets = data;
                })
                .catch(error => {
                    console.error('获取数据集数据失败:', error);
                });
        },
        async handleCheckDataset() {
            if (this.processing) return;
            this.processing = true;
            this.checking = true;
            this.checkstep = 1;
            await this.$nextTick();
            try {
                const response = await axios.post(`/models/${this.currentModel.id}/check`, {
                    dataset_id: this.dataset_id
                });
                if (response.data.code === 200) {
                    this.checkResult = response.data.data;
                    this.checkPass = this.checkResult.check_pass;
                    await this.$nextTick();
                    await this.copyDS();
                }
                else {
                    this.checkPass = false;
                }
                if (!this.checkPass) {
                    try {
                        const logResponse = await axios.get(`/models/${this.currentModel.id}/check/check_dataset.log`);
                        this.checkLog = logResponse.data;
                    } catch (error) {
                        this.$message.error('获取日志失败：' + error.message);
                    }
                }
                this.showCheckResult = true;
            } catch (error) {
                this.$message.error('网络请求失败：' + error.message);
            } finally {
                this.processing = false;
            }

        },
        async copyDS() {
            this.checkstep = 2;
            await this.$nextTick();
            try {
                const response = await axios.post(`/models/${this.currentModel.id}/copyds`, {
                    dataset_id: this.dataset_id
                });
                if (response.data.code === 200) {
                    this.checkstep = 4;
                } else {
                    this.$message.error('数据集复制失败：' + response.data.message);
                }
            } catch (error) {
                this.$message.error('网络请求失败：' + error.message);
            }

        },
        async handleModelCfgNext() {
            switch (this.currentModel.status) {
                case 'config':
                    switch (this.currentModel.step) {
                        case 0:
                            if (this.checkPass) {
                                this.fetchTrainParams();
                                this.currentModel.step = 1;
                            } else {
                                this.$message.error('请选择数据集并通过检查');
                            }
                            break;
                        case 1:
                            this.currentModel.step = 2;
                            break;
                        case 2:
                            try {
                                const response = await axios.post(`/models/${this.currentModel.id}/train`, this.training);
                                if (response.data.code === 200) {
                                    window.location.reload(); // 强制刷新当前页面
                                } else {
                                    this.$message.error(response.data.message);
                                }
                            } catch (error) {
                                this.$message.error('网络请求失败：' + error.message);
                            }
                    }
                    break;
                case 'queued':
                case 'training':
                    try {
                        const response = await axios.get(`/models/${this.currentModel.id}/train/stop`);
                        if (response.data.code === 200) {
                            window.location.reload(); // 强制刷新当前页面
                        } else {
                            this.$message.error(response.data.message);
                        }
                    } catch (error) {
                        this.$message.error('网络请求失败：' + error.message);
                    }
                    break;
                case 'finished':
                case 'aborted':
                case 'failed':
                    try {
                        const response = await axios.get(`/models/${this.currentModel.id}/config/1`);
                        if (response.data.code === 200) {
                            window.location.reload(); // 强制刷新当前页面
                        } else {
                            this.$message.error(response.data.message);
                        }
                    } catch (error) {
                        this.$message.error('网络请求失败：' + error.message);
                    }
                    break;
            }

        },
        download() {
            // 调用API获取模型文件
            window.open(`/models/${this.currentModel.id}/download`, '_blank');
        },
        /**
        * 打开创建应用对话框并初始化数据
        * @param {Object} model - 选中的预训练模型
        */
        openCreateAppDialog(model) {
            this.newAppFormData = {
                name: '',
                id: '',
                model_id: this.currentModel.id
            };
            this.showCreateAppDialog = true;
        },
        /**
        * 提交应用表单数据到后端
        */
        async submitAppForm() {
            this.$refs.appForm.validate(async (valid) => {
                if (valid) {
                    try {
                        await axios.post(`/models/${this.newAppFormData.model_id}/createapp`, this.newAppFormData);
                        this.$message.success('应用创建成功');
                        this.showCreateAppDialog = false;
                        this.$router.push(`/app/module/${this.newAppFormData.id}`);
                    } catch (error) {
                        this.$message.error('应用创建失败:' + error.response.data.message);
                    }
                }
            });
        }
    }
}
</script>
<style>
.log-scrollbar {
    height: calc(100vh - 300px);
    width: 100%;
    padding: 20px 0;
}

.log-pre {
    white-space: pre;
    word-wrap: normal;
    padding: 15px;
    margin: 0;
}

.steps {
    margin: 20px auto;
    max-width: 900px;
}

.data-prep-container {
    align-items: center;
    text-align: center;
}

.dataset-selector {
    margin: 20px auto;
    max-width: 600px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.check-result-card {
    margin-top: 20px;
}

.stat-chart-container {
    display: flex;
    align-items: center;
    justify-content: center;
}

.param-setting {
    align-items: center;
    text-align: center;
}

.step-footer {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
}

.train-section {
    padding-bottom: 10px;
}

.val-section {
    padding-top: 10px;
}
</style>