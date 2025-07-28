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
        <div class="sample-section train-section">
          <h4>训练集信息</h4>
          <div class="image-grid">
            <el-image v-for="(path, index) in checkResult.attributes.train_sample_paths" :key="path" :src="path"
              class="image-item" fit="cover" :preview-src-list="checkResult.attributes.train_sample_paths"
              :initial-index="index"></el-image>
          </div>
        </div>
        <div class="sample-section val-section">
          <h4>验证集信息</h4>
          <div class="image-grid">
            <el-image v-for="(path, index) in checkResult.attributes.val_sample_paths" :key="path" :src="path"
              class="image-item" fit="cover" :preview-src-list="checkResult.attributes.val_sample_paths"
              :initial-index="index"></el-image>
          </div>
        </div>
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
/**
 * CheckShowType 组件
 * 用于展示数据集检查结果，包括样本数量统计、样本图片预览和数据分布统计图
 */
export default {
  name: 'imageShowType',
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
  }
}
</script>

<style scoped>

.sample-row {
    height: 600px;
}

.sample-grid {
    display: flex;
    flex-direction: column;
    border-right: 1px solid #888888;
}
.sample-section {
    flex: 1;
}

.image-item {
    width: 100px;
    height: 100px;
    margin: 5px
}

.stat-chart-container {
  /* background-color: #f5f5f5; */
  padding: 15px;
  border-radius: 8px;
  height: 100%;
}
</style>