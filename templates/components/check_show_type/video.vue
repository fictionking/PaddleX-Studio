<template>
  <div>
    <el-row>
      <el-col :span="8">
        <el-statistic title="训练样本数量" :value="checkResult.attributes.train_samples" />
      </el-col>
      <el-col :span="8">
        <el-statistic title="验证样本数量" :value="checkResult.attributes.val_samples" />
      </el-col>
      <el-col :span="8" v-if="checkResult?.attributes?.num_classes">
        <el-statistic title="类别数量" :value="checkResult.attributes.num_classes" />
      </el-col>
    </el-row>

    <el-row :gutter="20" class="sample-row">
      <!-- 左边图片区域 -->
      <el-col :span="16" class="sample-grid">
        <el-row :gutter="20" class="sample-row">
          <!-- 左边视频区域 -->
          <el-col :span="12" class="sample-grid">
            <div class="sample-section">
              <h4>训练集信息</h4>
              <div class="video-grid">
                <div v-for="(path, index) in checkResult.attributes.train_sample_paths" :key="index" class="video-item">
                  <video :src="path" class="video-thumbnail" controls preload="metadata"></video>
                  <div class="video-name">{{ getFileName(path) }}</div>
                </div>
              </div>
            </div>
          </el-col>
          <el-col :span="12" class="sample-grid">
            <div class="sample-section">
              <h4>验证集信息</h4>
              <div class="video-grid">
                <div v-for="(path, index) in checkResult.attributes.val_sample_paths" :key="index" class="video-item">
                  <video :src="path" class="video-thumbnail" controls preload="metadata"></video>
                  <div class="video-name">{{ getFileName(path) }}</div>
                </div>
              </div>
            </div>
          </el-col>
        </el-row>
      </el-col>
      <!-- 右边统计图区域 -->
      <el-col :span="8" class="stat-chart-container">
        <div style="width: 100%;">
          <h4>数据分布统计图</h4>
          <el-image :src="checkResult.analysis.histogram" style="max-width: 100%;" fit="contain"></el-image>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script>
export default {
  name: 'videoShowType',
  props: {
    /**
     * 数据集检查结果对象
     * @type {Object}
     * @property {Object} attributes - 包含训练样本数、验证样本数等属性
     * @property {Object} analysis - 包含数据分布统计图表等分析结果
     */
    checkResult: {
      type: Object,
      required: true
    }
  },
  methods: {
    /**
     * 从路径中提取文件名
     * @param {string} path - 文件路径
     * @returns {string} 文件名
     */
    getFileName(path) {
      return path.split('/').pop().split('\\').pop();
    }
  }
}
</script>
<style scoped>
.video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
  margin-top: 16px;
  height: 500px;
  /* 固定高度 */
  overflow-y: auto;
  /* 启用垂直滚动 */
  padding: 10px;
}

.video-item {
  cursor: pointer;
  transition: transform 0.2s;
}

.video-item:hover {
  transform: scale(1.02);
}

.video-thumbnail {
  width: 100%;
  height: 140px;
  object-fit: cover;
  border-radius: 4px;
}

.video-name {
  margin-top: 8px;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: #606266;
}

.video-player-container {
  width: 100%;
  height: 0;
  padding-bottom: 56.25%;
  /* 16:9 比例 */
  position: relative;
}

.video-player {
  position: absolute;
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.sample-row {
  height: 600px;
}

.sample-grid {
  border-right: 1px solid #888888;
}

.sample-section {
  flex: 1;
}

.stat-chart-container {
  /* background-color: #f5f5f5; */
  padding: 15px;
  border-radius: 8px;
  height: 100%;
}
</style>