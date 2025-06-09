<template>
    <div v-if="currentModel.status === 'config'">
        <div class="step-header">
            <el-steps style="max-width: 900px; margin: 0 auto;" :space="300" :active="currentModel.step" align-center
                finish-status="success">
                <el-step title="数据准备"></el-step>
                <el-step title="参数准备"></el-step>
                <el-step title="提交训练"></el-step>
            </el-steps>
        </div>
        <div class="step-body">
            <!-- 数据准备 -->
            <div v-if="currentModel.step === 0" style="align-items: center;text-align: center;">
                <br>
                <div style="margin: 20px auto; max-width: 600px;">
                    <el-select v-model="dataset_id" placeholder="请选择训练数据集" @change="handleDatasetChange"
                        style="width: 100%;" :disabled="processing">
                        <el-option v-for="dataset in datasets" :key="dataset.id" :label="dataset.name"
                            :value="dataset.id"></el-option>
                    </el-select>
                    <div style="display: flex;margin-top: 10px;gap: 20px;align-items: center;" v-if="dataset_id">
                        已选数据集：<el-text v-text="dataset_name"></el-text>
                        <el-button type="primary" @click="handleCheckDataset" :disabled="processing">检查数据集</el-button>
                    </div>
                </div>
                <div v-show="showCheckResult" style="margin-top: 20px;">
                    <el-card>
                        <h3>检查状态：<el-tag :type="checkPass ? 'success' : 'danger'" v-text="checkPass ? '通过' : '未通过'">
                            </el-tag></h3>
                        <div v-show="!checkPass">
                            <el-input v-if="!checkPass" v-model="checkLog" style="width: 100%;" :rows="20"
                                type="textarea" placeholder="检查日志内容将显示在此处" />
                        </div>

                        <div v-if="checkResult" v-show="checkPass">
                            <el-row :gutter="20" style="height: 600px;">
                                <!-- 左边图片区域 -->
                                <el-col :span="16"
                                    style="display: flex; flex-direction: column; border-right: 1px solid #eee;">
                                    <div style="flex: 1; padding-bottom: 10px;">
                                        <h4>训练集信息</h4>
                                        <p>样本数量：<el-text v-text="checkResult.attributes.train_samples"></el-text>
                                        </p>
                                        <div class="image-grid">
                                            <el-image v-for="path in checkResult.attributes.train_sample_paths"
                                                :key="path" :src="path" style="width: 100px; height: 100px; margin: 5px"
                                                fit="cover"></el-image>
                                        </div>
                                    </div>
                                    <div style="flex: 1; padding-top: 10px;">
                                        <h4>验证集信息</h4>
                                        <p>样本数量：<el-text v-text="checkResult.attributes.val_samples"></el-text>
                                        </p>
                                        <div class="image-grid">
                                            <el-image v-for="path in checkResult.attributes.val_sample_paths"
                                                :key="path" :src="path" style="width: 100px; height: 100px; margin: 5px"
                                                fit="cover"></el-image>
                                        </div>
                                    </div>
                                </el-col>
                                <!-- 右边统计图区域 -->
                                <el-col :span="8" style="display: flex; align-items: center; justify-content: center;">
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
            <div v-if="currentModel.step === 1" style="align-items: center;text-align: center;">
                <h4>训练参数设置</h4>
                <el-form label-width="160px">
                    <el-form-item label="轮次(Epochs)">
                        <el-input v-model="training.epochs" type="number" placeholder="100" />
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
                        <el-input v-model="training.learningRate" type="number" step="0.00001" placeholder="0.00010" />
                        <div class="param-tip">学习率建议参考Batch Size进行同比例的调整</div>
                    </el-form-item>
                    <el-collapse>
                        <el-collapse-item title="高级配置">
                            <el-form-item label="断点训练权重">
                                <el-input v-model="training.resumeCheckpoint" placeholder="从训练中断保存的checkpoint继续训练" />
                            </el-form-item>
                            <el-form-item label="预训练权重">
                                <el-input v-model="training.pretrainedWeight" placeholder="从预训练的权重开始微调，提高训练效率" />
                            </el-form-item>
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
        </div>
        <div class="step-footer" style="position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%);">
            <el-button type="primary" @click="handleModelCfgNext" :disabled="processing">下一步</el-button>
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
                epochs: 100,
                batchSize: 8,
                classNum: 4,
                learningRate: 0.00010,
                resumeCheckpoint: '',
                pretrainedWeight: '',
                warmUpSteps: 100,
                logInterval: 10,
                trainEvalInterval: 1
            }
        }
    },
    mounted() {
        this.loadDatasets();  // 组件挂载后加载数据集数据
    },
    props: ['currentModel'],
    emits: ['update:currentModel'],
    emits: [],
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
        handleDatasetChange(value) {
            const selectedDataset = this.datasets.find(dataset => dataset.id === value);
            if (selectedDataset) {
                this.dataset_name = selectedDataset.name;
            }
        },
        async handleCheckDataset() {
            if (this.processing) return;
            this.processing = true;
            await this.$nextTick();
            try {
                const response = await axios.post(`/models/${this.currentModel.id}/check`, {
                    dataset_id: this.dataset_id
                });
                if (response.data.code === 200) {
                    this.checkResult = response.data.data;
                    this.checkPass = this.checkResult.check_pass;
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
            if (this.processing || !this.checkPass) return;
            this.processing = true;
            await this.$nextTick();
            try {
                const response = await axios.post(`/models/${this.currentModel.id}/copyds`, {
                    dataset_id: this.dataset_id
                });
                if (response.data.code === 200) {
                    this.$emit('update:currentModel', response.data.data);
                } else {
                    this.$message.error('数据集复制失败：' + response.data.message);
                }
            } catch (error) {
                this.$message.error('网络请求失败：' + error.message);
            } finally {
                this.processing = false;
            }

        },
        handleModelCfgNext() {
            switch (this.currentModel.step) {
                case 0:
                    if (this.checkPass) {
                        this.copyDS();
                    } else {
                        this.$message.error('请选择数据集并通过检查');
                    }
                    break;
                case 1:
                    this.currentModel.step = 2;
                    break;
            }
        }
    }
}
</script>