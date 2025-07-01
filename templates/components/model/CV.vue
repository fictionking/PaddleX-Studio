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

.sample-grid {
    display: flex;
    flex-direction: column;
    border-right: 1px solid #888888;
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

.sample-row {
    height: 600px;
}

.sample-section {
    flex: 1;
}

.train-section {
    padding-bottom: 10px;
}

.val-section {
    padding-top: 10px;
}

.image-item {
    width: 100px;
    height: 100px;
    margin: 5px
}
</style>
<template>
    <div>
        <div v-if="currentModel.status !== 'config'">
            <el-scrollbar ref="logScrollbar" class="log-scrollbar">
                <pre ref="logPre" class="log-pre"><code>{{ trainLog }}</code></pre>
            </el-scrollbar>
        </div>
        <div v-if="currentModel.status === 'config'">
            <div class="step-header">
                <el-steps class="steps" :space="300" :active="currentModel.step" align-center finish-status="success"
                    simple>
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
                        <el-select v-model="dataset_id" placeholder="请选择训练数据集" @change="handleDatasetChange"
                            style="flex: 1;" :disabled="processing">
                            <el-option v-for="dataset in datasets" :key="dataset.id" :label="dataset.name"
                                :value="dataset.id"></el-option>
                        </el-select>
                        <el-button type="primary" @click="handleCheckDataset"
                            :disabled="!dataset_id || processing">检查数据集</el-button>
                    </div>
                    <div v-if="checking">
                        <el-steps class="steps" :space="300" :active="checkstep" align-center finish-status="success">
                            <el-step title="提交任务" description="提交数据集检查任务"></el-step>
                            <el-step title="格式校验" description="校验数据集格式是否正确"></el-step>
                            <el-step title="数据集保存" description="保存校验通过的数据集"></el-step>
                            <el-step title="完成" description="数据集检查完成"></el-step>
                        </el-steps>
                    </div>
                    <div v-show="showCheckResult" class="check-result-card">
                        <el-card shadow="never">
                            <h3>检查状态：<el-tag :type="checkPass ? 'success' : 'danger'" v-text="checkPass ? '通过' : '未通过'">
                                </el-tag></h3>
                            <div v-show="!checkPass">
                                <el-input v-if="!checkPass" v-model="checkLog" style="width: 100%;" :rows="20"
                                    type="textarea" placeholder="检查日志内容将显示在此处" />
                            </div>

                            <div v-if="checkResult" v-show="checkPass">
                                <el-row>
                                    <el-col :span="8">
                                        <el-statistic title="训练样本数量" :value="checkResult.attributes.train_samples" />
                                    </el-col>
                                    <el-col :span="8">
                                        <el-statistic title="验证样本数量" :value="checkResult.attributes.val_samples" />
                                    </el-col>
                                    <el-col :span="8">
                                        <el-statistic title="类别数量" :value="checkResult.attributes.num_classes" />
                                    </el-col>
                                </el-row>
                                <el-row :gutter="20" class="sample-row">
                                    <!-- 左边图片区域 -->
                                    <el-col :span="16" class="sample-grid">
                                        <div class="sample-section train-section">
                                            <h4>训练集信息</h4>
                                            <div class="image-grid">
                                                <el-image
                                                    v-for="(path, index) in checkResult.attributes.train_sample_paths"
                                                    :key="path" :src="path" class="image-item" fit="cover"
                                                    :preview-src-list="checkResult.attributes.train_sample_paths"
                                                    :initial-index="index"></el-image>
                                            </div>
                                        </div>
                                        <div class="sample-section val-section">
                                            <h4>验证集信息</h4>
                                            <div class="image-grid">
                                                <el-image
                                                    v-for="(path, index) in checkResult.attributes.val_sample_paths"
                                                    :key="path" :src="path" class="image-item" fit="cover"
                                                    :preview-src-list="checkResult.attributes.val_sample_paths"
                                                    :initial-index="index"></el-image>
                                            </div>
                                        </div>
                                    </el-col>
                                    <!-- 右边统计图区域 -->
                                    <el-col :span="8" class="stat-chart-container">
                                        <div style="width: 100%;">
                                            <h4>数据分布统计图</h4>
                                            <el-image :src="checkResult.analysis.histogram" style="max-width: 100%;"
                                                fit="contain"></el-image>
                                        </div>
                                    </el-col>
                                </el-row>
                            </div>
                        </el-card>
                    </div>
                </div>
                <!-- 参数准备 -->
                <div v-if="currentModel.step === 1" class="param-setting">
                    <h4>训练参数设置</h4>
                    <el-form label-width="160px">
                        <el-form-item label="轮次(Epochs)">
                            <el-input v-model="training.epochs" type="number" placeholder="10" />
                            <div class="param-tip">训练轮次越大，耗时越久，最终精度通常越高</div>
                        </el-form-item>
                        <el-form-item label="批大小(Batch Size)">
                            <el-input v-model="training.batchSize" type="number" placeholder="8" />
                            <div class="param-tip">单卡Batch Size，值越大，显存占用越高</div>
                        </el-form-item>
                        <el-form-item label="类别数量(Class Num)">
                            <el-input v-model="training.classNum" type="number" placeholder="4" />
                            <div class="param-tip">类别的数量，根据实际情况填写</div>
                        </el-form-item>
                        <el-form-item label="学习率(Learning Rate)">
                            <el-input v-model="training.learningRate" type="number" step="0.00001"
                                placeholder="0.00010" />
                            <div class="param-tip">学习率建议参考Batch Size进行同比例的调整</div>
                        </el-form-item>
                        <el-collapse>
                            <el-collapse-item title="高级配置">
                                <el-form-item label="热启动步数(WarmUp Steps)">
                                    <el-input v-model="training.warmUpSteps" type="number" placeholder="100" />
                                    <div class="param-tip">在训练初始阶段以较小学习率训练的step数</div>
                                </el-form-item>
                                <el-form-item label="log打印间隔(Log Interval) / step">
                                    <el-input v-model="training.logInterval" type="number" placeholder="10" />
                                    <div class="param-tip">每隔多少个step打印一次log信息</div>
                                </el-form-item>
                                <el-form-item label="评估、保存间隔(Eval Interval) / epoch">
                                    <el-input v-model="training.trainEvalInterval" type="number" placeholder="例如：1" />
                                </el-form-item>
                            </el-collapse-item>
                        </el-collapse>
                    </el-form>
                </div>
                <!-- 提交训练 -->
                <div v-if="currentModel.step === 2" style="align-items: center;text-align: center;">
                    <h4>选择训练运行位置</h4>
                    <el-radio-group v-model="runLocation">
                        <el-radio label="local">本地</el-radio>
                        <el-radio label="dock">Dock(暂未实现)</el-radio>
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
        </div>
    </div>
</template>

<script type="module">
export default {
    data() {
        return {
            datasets: [],
            dataset_id: '',
            dataset_name: '',
            showDatasetDialog: false,
            checking: false,
            checkstep: 0,
            checkResult: null,
            checkingDataset: false,
            checkPass: false,
            showCheckResult: false,
            checkLog: '',
            showTrainResult: false,
            trainResult: null,
            trainLog: '',
            processing: false,
            training: {
                epochs: 10,
                batchSize: 8,
                classNum: 4,
                learningRate: 0.00010,
                warmUpSteps: 100,
                logInterval: 10,
                trainEvalInterval: 1
            },
            trainLog: '',  // 训练日志内容
            runLocation: 'local'  // 训练运行位置默认值（local/dock）
        }
    },
    mounted() {
        // 如果当前模型是训练状态，启动日志轮询
        switch (this.currentModel.status) {
            case 'config':
                if (this.currentModel.step === 1) {
                    this.training.classNum = this.currentModel.num_classes;
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
    },
    beforeUnmount() {
        // 组件卸载时清除定时器
        if (this.logPollingTimer) {
            clearInterval(this.logPollingTimer);
            this.logPollingTimer = null;
        }
    },
    props: ['currentModel'],
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
    emits: [],
    methods: {
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
            fetch('/datasets')
                .then(response => response.json())
                .then(data => {
                    this.datasets = data;
                })
                .catch(error => {
                    console.error('获取数据集数据失败:', error);
                });
        },
        handleDatasetChange(value) {
            const selectedDataset = this.datasets.find(dataset => dataset.id === value);
            if (selectedDataset) {
                this.dataset_name = selectedDataset.name;
            }
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
                    this.training.classNum = this.checkResult.attributes.num_classes;
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
        }
    }
}
</script>