<template>
    <div class="property-group">
        <div class="group-label">{{ label }}</div>
        <slot></slot>
    </div>
</template>

<script>
/**
 * 组属性组件
 * 用于对属性进行分组展示
 */
export default {
    props: {
        label: {
            type: String,
            required: true,
            description: '组标题'
        }
    }
};
</script>

<style scoped>
.property-group {
    margin-top: 0px;
}

.group-label {
    font-weight: bold;
    margin-bottom: 5px;
    color: hsl(150, 47%, 49%);
}
</style>