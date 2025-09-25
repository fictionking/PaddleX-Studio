<template>
    <template v-for="(value, key) in parameters_def" :key="key">
        <InputNumberProperty v-if="value.type === 'number'" :label="key" v-model="parameters_value[key]"
            :min="value.min" :max="value.max" :step="value.step" :readonly="!value.config_able"
            v-bind="handlePrefix ? { handleId: `${handlePrefix}${key}`, handleClass: `${handleClassPrefix}${key}` } : {}" />
        <SelectProperty v-else-if="value.type === 'enum' && value.enum" :label="key" v-model="parameters_value[key]"
            :options="value.enum" :readonly="!value.config_able"
            v-bind="handlePrefix ? { handleId: `${handlePrefix}${key}`, handleClass: `${handleClassPrefix}${key}` } : {}" />
        <TextProperty v-else-if="value.type === 'text'" :label="key" v-model="parameters_value[key]"
            :readonly="!value.config_able"
            v-bind="handlePrefix ? { handleId: `${handlePrefix}${key}`, handleClass: `${handleClassPrefix}${key}` } : {}" />
        <TextProperty v-else-if="value.type === 'dict'" v-model="parameters_value[key]"
            placeholder="请输入JSON格式的字典，例如: {&quot;key&quot;: &quot;value&quot;}" :readonly="!value.config_able"
            v-bind="handlePrefix ? { handleId: `${handlePrefix}${key}`, handleClass: `${handleClassPrefix}${key}` } : {}">
        </TextProperty>
        <TextProperty v-else-if="value.type === 'list'" v-model="parameters_value[key]"
            placeholder="请输入JSON格式的列表，例如: [&quot;value1&quot;, &quot;value2&quot;]" :readonly="!value.config_able"
            v-bind="handlePrefix ? { handleId: `${handlePrefix}${key}`, handleClass: `${handleClassPrefix}${key}` } : {}">
        </TextProperty>
        <BoolProperty v-else-if="value.type === 'bool'" :label="key" v-model="parameters_value[key]"
            :trueLabel="value.trueLabel" :falseLabel="value.falseLabel" :readonly="!value.config_able"
            v-bind="handlePrefix ? { handleId: `${handlePrefix}${key}`, handleClass: `${handleClassPrefix}${key}` } : {}" />
        <InputProperty v-else :label="key" v-model="parameters_value[key]" :readonly="!value.config_able"
            v-bind="handlePrefix ? { handleId: `${handlePrefix}${key}`, handleClass: `${handleClassPrefix}${key}` } : {}" />
    </template>
</template>

<script>
import InputNumberProperty from './InputNumberProperty.vue';
import SelectProperty from './SelectProperty.vue';
import TextProperty from './TextProperty.vue';
import BoolProperty from './BoolProperty.vue';
import InputProperty from './InputProperty.vue';

/**
 * 参数列表组件
 * 用于直接渲染参数列表，不包含外部的Group
 * 可以接收模型参数或推理参数等参数对象，并为每个参数创建对应的属性组件
 */
export default {
    components: {
        InputNumberProperty,
        SelectProperty,
        TextProperty,
        BoolProperty,
        InputProperty
    },
    props: {
        /**
         * 参数对象，包含所有需要渲染的参数
         * 格式: { key1: { type: 'xxx', value: 'xxx', ... }, key2: { ... } }
         */
        parameters_def: {
            type: Object,
            required: true,
            description: '参数定义，包含所有需要渲染的参数'
        },
        parameters_value: {
            type: Object,
            required: true,
            description: '参数值'
        },
        /**
         * 连接点ID前缀，用于生成唯一的连接点ID
         */
        handlePrefix: {
            type: String,
            default: null,
            description: '连接点ID前缀'
        },
        /**
         * 连接点样式类前缀
         */
        handleClassPrefix: {
            type: String,
            default: '',
            description: '连接点样式类前缀'
        }
    },
    /**
     * 组件挂载后执行初始化逻辑
     * 检查parameters_value是否包含parameters_def中定义的所有属性，如果没有则添加并赋值
     */
    mounted() {
        this.initializeParameters();
    },
    methods: {
        /**
         * 初始化参数值对象
         * 确保parameters_value中包含parameters_def中定义的所有属性
         */
        initializeParameters() {
            // 遍历parameters_def中的所有属性
            for (const key in this.parameters_def) {
                if (this.parameters_def.hasOwnProperty(key)) {
                    // 检查parameters_value中是否存在该属性
                    if (this.parameters_value[key] === undefined) {
                        // 如果不存在，则从parameters_def中获取默认值并设置
                        this.parameters_value[key] = this.parameters_def[key].value;
                    }
                }
            }
        }
    }
};
</script>