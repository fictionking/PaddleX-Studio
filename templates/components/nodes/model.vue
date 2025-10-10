<template>
    <WorkflowNode v-bind="$props">
        <template #properties>
            <ValueProperty label="模型类别" :value="data.params.module_name" />
            <ValueProperty v-if="data.params.is_local" label="模型名称" :value="data.params.model_name" />
            <el-popover v-else placement="right" width="310" trigger="click" :show-after="500" popper-style="padding:5px;"
                :persistent="false">
                <template #reference>
                    <div style="display: flex;align-items: center;justify-content: space-between;">
                        <ValueProperty label="模型名称" :value="data.params.model_name" />
                        <el-icon>
                            <CaretBottom />
                        </el-icon>
                    </div>
                </template>
                <div class="menu-scroll-container">
                    <el-menu>
                        <el-menu-item v-for="value, key in currentModuleModels" :index="key" @click="changeModel(key)"
                            class="node-menu">
                            {{ value.name }}
                            <el-icon v-if="value.rate" style="color:goldenrod">
                                <CollectionTag />
                            </el-icon><el-icon v-if="cachedModels.includes(value.name)" style="color:#00c58d;">
                                <SuccessFilled />
                            </el-icon>
                        </el-menu-item>
                    </el-menu>
                </div>
            </el-popover>
            <ValueProperty label="模型路径" :value="data.params.model_dir" />
            <GroupProperty label="模型参数" v-if="data.params?.model_params">
                <PropertyList :parameters_def="data.params.model_params_def"
                    :parameters_value="data.params.model_params" />
            </GroupProperty>
            <GroupProperty label="推理参数" v-if="data.params?.infer_params">
                <PropertyList :parameters_def="data.params.infer_params_def"
                    :parameters_value="data.params.infer_params" :handle-prefix="'params.infer_params.'"
                    :handle-class-prefix="'infer_params_'" />
            </GroupProperty>
        </template>
    </WorkflowNode>
</template>

<script>
import { ValueProperty, GroupProperty, WorkflowNode, PropertyList } from './base/WorkflowNode.mjs'
import { inject, computed } from 'vue'

/**
 * 模型节点组件
 * 用于展示和配置模型相关参数
 */
export default {
    components: {
        WorkflowNode,
        ValueProperty,
        GroupProperty,
        PropertyList
    },
    // mixins: [WorkflowNondes],
    props: {
        id: {
            type: String,
            required: true,
        },
        type: {
            type: String,
            required: true,
        },
        data: {
            type: Object,
            required: true,
        }
    },
    setup(props) {
        // 注入父组件提供的 models 数据
        const models = inject('models', [])

        // 根据 data.params.module_name 查找对应的模块
        const currentModule = computed(() => {
            // 遍历 models 数组查找对应的模块
            for (const category of models.value) {
                if (category?.modules && Array.isArray(category.modules)) {
                    const module = category.modules.find(mod => mod.id === props.data.params.module_name)
                    if (module) {
                        return module
                    }
                }
            }
            return null
        })

        // 获取当前模块下的所有模型
        const currentModuleModels = computed(() => {
            if (!currentModule.value || !currentModule.value.models) return {}
            return currentModule.value.models
        })
        // 注入父组件提供的 cachedModels 数据
        const cachedModels = inject('cachedModels', [])
        return {
            currentModuleModels,
            cachedModels
        }
    },
    methods: {
        changeModel(key) {
            this.data.params.model_name = key
            this.data.params.model_dir = 'weights\\' + key + '\\inference'
        }
    }
};
</script>
<style scoped>
/* 节点菜单样式 */
.node-menu {
    border: none;
    width: auto;
    --el-menu-item-height: 32px;
    --el-menu-sub-item-height: 32px;
}

/* 滚动菜单容器样式 */
.menu-scroll-container {
    max-height: 400px;
    /* 设置最大高度，超出部分显示滚动条 */
    overflow-y: auto;
    /* 垂直方向滚动 */
    padding: 0px;
    min-width: 250px;
}

/* 自定义滚动条样式 */
.menu-scroll-container::-webkit-scrollbar {
    width: 8px;
    /* 滚动条宽度 */
    height: 8px;
    /* 滚动条高度 */
}

.menu-scroll-container::-webkit-scrollbar-track {
    background: transparent;
    /* 滚动条轨道背景 */
}

.menu-scroll-container::-webkit-scrollbar-thumb {
    background: #a8a8a8;
    /* 滚动条滑块颜色 */
    border-radius: 4px;
    /* 滚动条滑块圆角 */
}

.menu-scroll-container::-webkit-scrollbar-thumb:hover {
    background: #888;
    /* 滚动条滑块悬停颜色 */
}
</style>
