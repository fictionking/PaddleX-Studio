<template>
  <div>
    <el-row>
      <el-col :span="8">
        <el-statistic title="训练样本数量" :value="checkResult.attributes?.train_samples" :formatter="statisticFormatter" />
      </el-col>
      <el-col :span="8">
        <el-statistic title="验证样本数量" :value="checkResult.attributes?.val_samples" :formatter="statisticFormatter" />
      </el-col>
      <el-col :span="8" v-if="checkResult?.attributes?.num_classes">
        <el-statistic title="类别数量" :value="checkResult.attributes?.num_classes" :formatter="statisticFormatter" />
      </el-col>
    </el-row>
    <el-row :gutter="20" class="sample-row">
      <!-- 左边文本区域 -->
      <el-col :span="16" class="sample-grid">
        <el-row :gutter="20">
          <el-col :span="12">
            <div>
              <h4>训练集信息</h4>
              <div class="txt-box">
                <pre>{{ checkResult.attributes.train_sample_paths }}</pre>
              </div>
            </div>
          </el-col>
          <el-col :span="12">
            <div>
              <h4>验证集信息</h4>
              <div class="txt-box">
                <pre>{{ checkResult.attributes.val_sample_paths }}</pre>
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
/**
 * CheckShowType 组件
 * 用于展示数据集检查结果，包括样本数量统计、样本图片预览和数据分布统计图
 */
export default {
  name: 'txtShowType',
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
    statisticFormatter(value) {
      if (value) {
        return value.toLocaleString();
      }
      return '--';
    }
  }
}
</script>

<style scoped>

.sample-row {
    height: 600px;
}

.sample-grid {
    border-right: 1px solid #888888;
}
.txt-box {
    height: 90%;
    overflow: auto;
    border: 1px solid #5b5b5b;
    border-radius: 8px;
}

.stat-chart-container {
  /* background-color: #f5f5f5; */
  padding: 15px;
  border-radius: 8px;
  height: 100%;
}
</style>