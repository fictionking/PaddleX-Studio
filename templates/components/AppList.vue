<template>
    <div id="applist">
        <el-row :gutter="20" class="list-container">
            <el-col :span="24">
                <el-card class="list-card" v-for="(app, index) in apps" :key="index" @click="handleAppClick(app.id)">
                    <div class="listcard content">
                        <!-- 左侧内容 -->
                        <div class="listcard left-section">
                            <div class="listcard base">
                                <h3 class="listcard base h3" v-text="app.name"></h3>
                                <el-tag type="info" effect="plain" style="font-size: 14px;" v-text="app.id"></el-tag>
                            </div>
                            <p class="listcard desc" v-text="app.description"></p>
                            <div class="listcard category">
                                <el-tag type="success" v-text="app.type === 'module' ? '模型' : '产线'"></el-tag>
                                <el-tag type="success" v-for="tag in app.tags" :key="tag">{{ tag }}</el-tag>
                            </div>
                        </div>
                        <!-- 右侧内容 -->
                        <div class="listcard right-section">
                            <el-tag :class="app.status === 'running' ? 'status_running' : 'status_stopped'"
                                :type="app.status == 'stopped' ? 'primary' : 'success'"
                                v-text="app.status === 'running' ? '运行中' : '未运行'"></el-tag>
                            <div class="listcard actions">
                                <el-button v-if="app.status == 'stopped'" type="primary" size="small"
                                    @click.stop="handleAppStart(app.id)">启动</el-button>
                                <el-button v-if="app.status == 'running'" type="danger" size="small"
                                    @click.stop="handleAppStop(app.id)">停止</el-button>
                                <el-button type="text" @click.stop="handleAppDelete(app.id)">删除</el-button>
                            </div>
                        </div>
                    </div>
                </el-card>
            </el-col>
        </el-row>
    </div>
</template>
<style>
.status_running {
    background-color: rgba(0, 197, 141, 0.1);
    border-color: #00c58d;
    color: #00c58d;
    font-weight: bolder;
}

.status_stopped {
    background-color: rgba(0, 91, 170, 0.1);
    border-color: #005baa;
    color: #005baa;
    font-weight: bolder;
}
</style>
<script type="module">

/**
 * 应用列表组件
 * 用于展示和管理已部署的应用
 */
export default {
    data() {
        return {
            apps: [],
            appsPollingTimer: null
        }
    },
    mounted() {
        this.autofresh();  // 自动刷新应用数据
    },
    beforeUnmount() {
        // 组件卸载时清除定时器
        if (this.appsPollingTimer) {
            clearInterval(this.appsPollingTimer);
            this.appsPollingTimer = null;
        }
    },
    methods: {
        /**
         * 设置定时刷新应用列表
         */
        autofresh() {
            this.appsPollingTimer = setInterval(() => {
                this.loadApps();
            }, 10000);
            this.loadApps();
        },
        /**
         * 从后端API加载应用列表
         */
        loadApps() {
            // 调用appMgr.py中定义的应用列表API
            axios.get('/apps')
                .then(response => {
                    // 确保data为数组，避免v-for错误
                    this.apps = Array.isArray(response.data) ? response.data : [];
                })
                .catch(error => {
                    console.error('获取应用数据失败:', error);
                    // 保持apps为数组
                    this.apps = [];
                });
        },
        /**
         * 处理应用卡片点击事件
         * @param {string} appId - 应用ID
         */
        handleAppClick(appId) {
            this.$router.push(`/app/${appId}`);
        },
        /**
         * 处理应用删除操作
         * @param {string} appId - 应用ID
         */
        handleAppDelete(appId) {
            this.$confirm('确定要删除该应用吗？', '提示', {
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                type: 'warning'
            }).then(() => {
                axios.delete(`/apps/delete/${appId}`)
                    .then(response => {
                        if (response.status === 204) {
                            this.loadApps();  // 删除成功后刷新应用列表
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
        /**
         * 处理应用启动操作
         * @param {string} appId - 应用ID
         */
        handleAppStart(appId) {
            // 显示加载中模态框
            const loading = this.$loading({
                lock: true,
                text: '应用启动中，请稍候...',
                background: 'rgba(0, 0, 0, 0.7)'
            });
            axios.get(`/apps/start/${appId}`)
                .then(response => {
                    this.$message.success('应用启动成功');
                    this.loadApps();  // 启动成功后刷新应用列表
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
        handleAppStop(appId) {
            // 显示加载中模态框
            const loading = this.$loading({
                lock: true,
                text: '应用停止中，请稍候...',
                background: 'rgba(0, 0, 0, 0.7)'
            });
            axios.get(`/apps/stop`)
                .then(response => {
                    this.$message.success('应用停止成功');
                    this.loadApps();  // 停止成功后刷新应用列表
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
