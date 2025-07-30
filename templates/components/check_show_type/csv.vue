<template>
  <div>
    <el-row>
      <el-col :span="12">
        <el-statistic title="训练样本数量" :value="checkResult.attributes?.train_samples" :formatter="statisticFormatter" />
      </el-col>
      <el-col :span="12">
        <el-statistic title="验证样本数量" :value="checkResult.attributes?.val_samples" :formatter="statisticFormatter" />
      </el-col>
    </el-row>
    <el-row :gutter="20" class="sample-row">
      <!-- 左边表格区域 -->
      <el-col :span="12" class="sample-grid">
        <div>
          <h4>训练集信息</h4>
          <div class="txt-box">
            <el-table v-if="checkResult.attributes.train_table" :data="formattedTrainData"
              :border="true" style="width: 100%" height="500">
              <el-table-column v-for="(column, index) in checkResult.attributes.train_table[0]" :prop="column"
                :label="column"></el-table-column>
            </el-table>
          </div>
        </div>
      </el-col>
      <el-col :span="12" class="sample-grid">
        <div>
          <h4>验证集信息</h4>
          <div class="txt-box">
            <el-table v-if="checkResult.attributes.val_table" :data="formattedValData"
              :border="true" style="width: 100%"  height="500">
              <el-table-column v-for="(column, index) in checkResult.attributes.val_table[0]" :prop="column"
                :label="column"></el-table-column>
            </el-table>
          </div>
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
  name: 'csvShowType',
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
  computed: {
    // 将数组数据转换为el-table支持的对象数组格式
    formattedTrainData() {
      if (!this.checkResult?.attributes?.train_table) return [];
      const headers = this.checkResult.attributes.train_table[0];
      return this.checkResult.attributes.train_table.slice(1).map(row => {
        const rowObj = {};
        headers.forEach((header, index) => {
          rowObj[header] = row[index];
        });
        return rowObj;
      });
    },
    formattedValData() {
      if (!this.checkResult?.attributes?.val_table) return [];
      const headers = this.checkResult.attributes.val_table[0];
      return this.checkResult.attributes.val_table.slice(1).map(row => {
        const rowObj = {};
        headers.forEach((header, index) => {
          rowObj[header] = row[index];
        });
        return rowObj;
      });
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

</style>