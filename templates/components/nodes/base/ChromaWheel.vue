<template>
    <div>
        <div class="color-picker-container" ref="colorPickerContainer" :style="{ backgroundColor: backgroundColor }">
            <!-- 网格背景 - 应用于整个颜色选择器 -->
            <div class="grid-background"></div>
            <!-- 颜色选择区域 - 亮度环和色盘叠放 -->
            <div class="color-selector" ref="colorSelector">
                <!-- 分段环弧容器 - 位于底层 -->
                <div class="ring-container" ref="ringContainer">
                    <!-- 分段环弧将通过JS生成 -->
                    <!-- 饱和度环弧标记 -->
                    <div class="ring-marker" title="饱和度" ref="saturationMarker"></div>
                    <!-- 亮度环弧标记 -->
                    <div class="ring-marker" title="亮度" ref="lightnessMarker"></div>
                    <!-- 透明度环弧标记 -->
                    <div class="ring-marker" title="透明度" ref="alphaMarker"></div>
                </div>
                <!-- 彩色圆盘 - 位于上层 -->
                <div class="color-wheel" ref="colorWheel">
                    <!-- 颜色圆盘将通过JS生成 -->
                    <!-- 颜色圆盘标记 -->
                    <div class="wheel-marker" title="色相" ref="wheelMarker"></div>
                </div>
            </div>
            <!-- 圆形颜色预览 - 位于左上角 -->
            <div class="color-preview" :style="{ backgroundColor: previewColor }"></div>
            <!-- 圆形初始颜色 - 位于左上角 -->
            <div class="color-start" :style="{ backgroundColor: initialColorStyle }"
                @click="resetToInitialColor"></div>
            <PreviewDecoration
                style="z-index: 11;position:absolute;left: -2px;top: -1px;filter: drop-shadow(0 0 2px rgba(0, 0, 0, 0.5));pointer-events: none;"
                width="83.6" height="123.5">
            </PreviewDecoration>
            <!-- 预定义颜色 - 右上角 -->
            <div class="preset-color teardrop-right-bottom" style="right:40px;top:5px;"
                :style="{ backgroundColor: presetColors[0].value }" @click="selectPresetColor(0)"></div>
            <div class="preset-color teardrop-left-bottom" style="right:5px;top:5px;"
                :style="{ backgroundColor: presetColors[1].value }" @click="selectPresetColor(1)"></div>
            <div class="preset-color teardrop-left-top" style="right:5px;top:40px;"
                :style="{ backgroundColor: presetColors[2].value }" @click="selectPresetColor(2)"></div>

            <!-- 预定义颜色 - 右下角 -->
            <div class="preset-color teardrop-left-bottom" style="right:5px;bottom: 40px;"
                :style="{ backgroundColor: presetColors[3].value }" @click="selectPresetColor(3)"></div>
            <div class="preset-color teardrop-left-top" style="right:5px;bottom: 5px;"
                :style="{ backgroundColor: presetColors[4].value }" @click="selectPresetColor(4)"></div>
            <div class="preset-color teardrop-right-top" style="right:40px;bottom: 5px;"
                :style="{ backgroundColor: presetColors[5].value }" @click="selectPresetColor(5)"></div>

            <!-- 预定义颜色 - 左下角 -->
            <div class="preset-color teardrop-left-top" style="left: 40px;bottom: 5px;"
                :style="{ backgroundColor: presetColors[6].value }" @click="selectPresetColor(6)"></div>
            <div class="preset-color teardrop-right-top" style="left: 5px;bottom: 5px;"
                :style="{ backgroundColor: presetColors[7].value }" @click="selectPresetColor(7)"></div>
            <div class="preset-color teardrop-right-bottom" style="left: 5px;bottom: 40px;"
                :style="{ backgroundColor: presetColors[8].value }" @click="selectPresetColor(8)"></div>
            <!-- 收藏的颜色-底部 -->
            <div class="favorite-colors-bottom">
                <div v-for="(color, index) in favoriteColors.slice(0, 5)" :key="'fav-bottom-' + index" class="fav-color"
                    :class="{ filled: color, notfill: !color }" :style="{ backgroundColor: color }"
                    @click="handleFavoriteClick(index)" @contextmenu.prevent="removeFavorite(index)"
                    :draggable="color !== null" @dragstart="handleDragStart($event, index)" @dragend="handleDragEnd"
                    @touchstart.prevent="handleTouchStart($event, index)" @touchmove.prevent="handleTouchMove($event)"
                    @touchend="handleTouchEnd($event, index)">
                    <svg v-if="!color" width="12px" height="12px" viewBox="0 0 448 512">
                        <path fill="currentColor"
                            d="M256 64c0-17.7-14.3-32-32-32s-32 14.3-32 32l0 160-160 0c-17.7 0-32 14.3-32 32s14.3 32 32 32l160 0 0 160c0 17.7 14.3 32 32 32s32-14.3 32-32l0-160 160 0c17.7 0 32-14.3 32-32s-14.3-32-32-32l-160 0 0-160z" />
                    </svg>
                </div>
            </div>
            <!-- 收藏的颜色-右侧 -->
            <div class="favorite-colors-right">
                <div v-for="(color, index) in favoriteColors.slice(5, 10)" :key="'fav-right-' + index" class="fav-color"
                    :class="{ filled: color, notfill: !color }" :style="{ backgroundColor: color }"
                    @click="handleFavoriteClick(index + 5)" @contextmenu.prevent="removeFavorite(index + 5)"
                    :draggable="color !== null" @dragstart="handleDragStart($event, index + 5)" @dragend="handleDragEnd"
                    @touchstart.prevent="handleTouchStart($event, index + 5)"
                    @touchmove.prevent="handleTouchMove($event)" @touchend="handleTouchEnd($event, index + 5)">
                    <svg v-if="!color" width="12px" height="12px" viewBox="0 0 448 512">
                        <path fill="currentColor"
                            d="M256 64c0-17.7-14.3-32-32-32s-32 14.3-32 32l0 160-160 0c-17.7 0-32 14.3-32 32s14.3 32 32 32l160 0 0 160c0 17.7 14.3 32 32 32s32-14.3 32-32l0-160 160 0c17.7 0 32-14.3 32-32s-14.3-32-32-32l-160 0 0-160z" />
                    </svg>
                </div>
            </div>

            <div title="锁定饱和度" class="lock-saturation" @click="toggleSaturationLock">
                <svg v-if="isSaturationLocked" width="8px" height="8px" viewBox="0 0 384 512" style="color: white;">
                    <path fill="currentColor"
                        d="M128 96l0 64 128 0 0-64c0-35.3-28.7-64-64-64s-64 28.7-64 64zM64 160l0-64C64 25.3 121.3-32 192-32S320 25.3 320 96l0 64c35.3 0 64 28.7 64 64l0 224c0 35.3-28.7 64-64 64L64 512c-35.3 0-64-28.7-64-64L0 224c0-35.3 28.7-64 64-64z" />
                </svg>
                <svg v-if="!isSaturationLocked" width="8px" height="8px" viewBox="0 0 576 512" style="color: white;">
                    <path fill="currentColor"
                        d="M384 96c0-35.3 28.7-64 64-64s64 28.7 64 64l0 32c0 17.7 14.3 32 32 32s32-14.3 32-32l0-32c0-70.7-57.3-128-128-128S320 25.3 320 96l0 64-160 0c-35.3 0-64 28.7-64 64l0 224c0 35.3 28.7 64 64 64l256 0c35.3 0 64-28.7 64-64l0-224c0-35.3-28.7-64-64-64l-32 0 0-64z" />
                </svg>
            </div>
            <!-- 背景色切换区域 -->
            <div class="bg-color-slider"
                style="position: absolute;height: 64px;width: 16px;top: 140px;left: 10px;" @click="handleBgColorClick"
                @touchstart.prevent="handleBgColorTouchStart"></div>
        </div>
        <!-- 颜色输入区 -->
        <div class="color-input-section">
            <div class="input-container">
                <select class="color-format-select" v-model="colorFormat"
                    @change="handleColorFormatChange">
                    <option value="hex">HEX</option>
                    <option value="rgb">RGB</option>
                    <option value="rgba">RGBA</option>
                    <option value="hsl">HSL</option>
                    <option value="hsla">HSLA</option>
                </select>
                <input type="text" v-model="colorValue" class="color-value-input"
                    @input="handleColorValueInput" />
                <button class="copy-color-btn" @click="copyColorToClipboard">
                    <svg width="12px" height="12px" viewBox="0 0 448 512">
                        <path fill="currentColor"
                            d="M192 0c-35.3 0-64 28.7-64 64l0 256c0 35.3 28.7 64 64 64l192 0c35.3 0 64-28.7 64-64l0-200.6c0-17.4-7.1-34.1-19.7-46.2L370.6 17.8C358.7 6.4 342.8 0 326.3 0L192 0zM64 128c-35.3 0-64 28.7-64 64L0 448c0 35.3 28.7 64 64 64l192 0c35.3 0 64-28.7 64-64l0-16-64 0 0 16-192 0 0-256 16 0 0-64-16 0z" />
                    </svg>
                </button>
            </div>
        </div>

        <!-- 复制成功提示 -->
        <div class="copy-toast" :class="{ visible: copyToastVisible }">
            已复制到剪贴板
        </div>
    </div>
</template>

<script setup>
// 引入Vue相关的hooks
import { ref, reactive, computed, onMounted, onBeforeUnmount, nextTick, watch, markRaw, defineComponent } from 'vue';

// 监听组件可见性变化的IntersectionObserver实例
const visibilityObserver = ref(null);

// 定义预览装饰件组件
const PreviewDecoration = markRaw(defineComponent({
    name: 'PreviewDecoration',
    __name: "preview-decoration",
    setup() {
        // 生成全局唯一ID
        const timestamp = Date.now();
        const random = Math.random().toString(36).substr(2, 9);
        const gradientId = 'gradient_' + timestamp + '_' + random;
        return {
            gradientId
        };
    },
    template: `<svg viewBox="0 0 83.6 123.5"  xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient :id="gradientId" x1="-1.0936279296875" y1="32.566619873046875" 
        x2="78.64790344238281" y2="79.79045104980469" gradientUnits="userSpaceOnUse">
        <stop offset="0" stop-color="#CCCCCC" />
        <stop offset="0.2838" stop-color="#F2F2F2" stop-opacity="1" />
        <stop offset="0.5698" stop-color="#393939" stop-opacity="1" />
        <stop offset="0.8342" stop-color="#A6A6A6" stop-opacity="1" />
        <stop offset="1" stop-color="#E0E0E0" />
      </linearGradient>
    </defs>
    <g>
    <path 
      d="M41.823 5C62.1614 5 78.6479 21.448 78.6479 41.737C78.6479 54.418 72.2079 65.598 62.412 72.2L58.961 74.07L54.0405 76.08C50.828 78.11 47.9152 81.555 46.0588 85.938C44.2025 90.318 43.7605 94.807 44.5413 98.52L44.6205 100.142L44.5533 103.003C42.7371 111.86 34.8798 118.527 25.4628 118.527C14.6987 118.527 5.9753 109.821 5.9753 99.085C5.9753 96.399 6.52058 93.84 7.50786 91.514L8.413 90.176L9.55165 88.817C12.1978 86.092 14.2206 82.062 14.9953 77.369C16.158 70.33 13.9749 65.288 10.3626 60.524L7.89476 56.037C6.02938 51.642 5 46.809 5 41.737C5 21.448 21.4875 5 41.823 5ZM42.0324 11.8275C25.6214 11.8275 12.3184 25.0995 12.3184 41.4715C12.3184 57.8435 25.6214 71.1155 42.0324 71.1155C58.4424 71.1155 71.7454 57.8435 71.7454 41.4715C71.7454 25.0995 58.4424 11.8275 42.0324 11.8275ZM25.5844 84.6255C17.8804 84.6255 11.6354 90.8555 11.6354 98.5415C11.6354 106.228 17.8804 112.459 25.5844 112.459C33.2884 112.459 39.5334 106.228 39.5334 98.5415C39.5334 90.8555 33.2884 84.6255 25.5844 84.6255Z" 
      stroke="rgba(100, 100, 100, 0.5)" stroke-width="2" fill-rule="evenodd" :fill="'url(#' + gradientId + ')'">
    </path>
    </g>
  </svg>`
}));

// 定义props
const props = defineProps({
    initialColor: {
        type: Object,
        default: () => ({
            h: 240,
            s: 100,
            l: 50,
            a: 100,
            r: 0,
            g: 0,
            b: 255
        })
    },
    modelValue: {
        type: String,
        default: '#0000FF'
    }
});

// 定义emits
const emit = defineEmits(['color-change', 'update:modelValue']);

// 颜色转换工具函数
const ColorUtils = {
    // HSL 转 RGB
    hslToRgb: (h, s, l) => {
        s /= 100;
        l /= 100;

        let r, g, b;

        if (s === 0) {
            r = g = b = l; // 灰色
        } else {
            const hue2rgb = (p, q, t) => {
                if (t < 0) t += 1;
                if (t > 1) t -= 1;
                if (t < 1 / 6) return p + (q - p) * 6 * t;
                if (t < 1 / 2) return q;
                if (t < 2 / 3) return p + (q - p) * (2 / 3 - t) * 6;
                return p;
            };

            const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
            const p = 2 * l - q;

            r = hue2rgb(p, q, h / 360 + 1 / 3);
            g = hue2rgb(p, q, h / 360);
            b = hue2rgb(p, q, h / 360 - 1 / 3);
        }

        return {
            r: Math.round(r * 255),
            g: Math.round(g * 255),
            b: Math.round(b * 255)
        };
    },

    // RGB 转 HEX
    rgbToHex: (r, g, b) => {
        return `#${[r, g, b]
            .map(x => Math.round(x).toString(16).padStart(2, '0'))
            .join('')
            .toUpperCase()}`;
    },

    // RGB 转 HSL
    rgbToHsl: (r, g, b) => {
        r /= 255;
        g /= 255;
        b /= 255;

        const max = Math.max(r, g, b);
        const min = Math.min(r, g, b);
        let h, s, l = (max + min) / 2;

        if (max === min) {
            h = s = 0; // 灰色
        } else {
            const d = max - min;
            s = l > 0.5 ? d / (2 - max - min) : d / (max + min);

            switch (max) {
                case r: h = (g - b) / d + (g < b ? 6 : 0); break;
                case g: h = (b - r) / d + 2; break;
                case b: h = (r - g) / d + 4; break;
            }

            h *= 60;
        }

        return {
            h: Math.round(h),
            s: Math.round(s * 100),
            l: Math.round(l * 100)
        };
    },

    // HEX 转 RGB
    hexToRgb: (hex) => {
        const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return result ? {
            r: parseInt(result[1], 16),
            g: parseInt(result[2], 16),
            b: parseInt(result[3], 16)
        } : null;
    },

    // RGB 转 RGBA
    rgbToRgba: (rgb, a = 100) => {
        return {
            r: rgb.r,
            g: rgb.g,
            b: rgb.b,
            a: a
        };
    },

    // RGBA 转字符串
    rgbaToString: (r, g, b, a) => {
        return `rgba(${r}, ${g}, ${b}, ${a / 100})`;
    },

    // 字符串转 RGBA
    stringToRgba: (str) => {
        const match = str.match(/^rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(0|1|0\.\d+)\s*\)$/);
        if (match) {
            const r = parseInt(match[1]);
            const g = parseInt(match[2]);
            const b = parseInt(match[3]);
            const a = Math.round(parseFloat(match[4]) * 100);
            return { r, g, b, a };
        }
        return null;
    },

    // HSL 转 HSLA
    hslToHsla: (hsl, a = 100) => {
        return {
            h: hsl.h,
            s: hsl.s,
            l: hsl.l,
            a: a
        };
    },

    // HSLA 转字符串
    hslaToString: (h, s, l, a) => {
        return `hsla(${h}, ${s}%, ${l}%, ${a / 100})`;
    },

    // 字符串转 HSLA
    stringToHsla: (str) => {
        const match = str.match(/^hsla\(\s*(\d+)\s*,\s*(\d+)%\s*,\s*(\d+)%\s*,\s*(0|1|0\.\d+)\s*\)$/);
        if (match) {
            const h = parseInt(match[1]);
            const s = parseInt(match[2]);
            const l = parseInt(match[3]);
            const a = Math.round(parseFloat(match[4]) * 100);
            return { h, s, l, a };
        }
        return null;
    },

    // 从圆盘位置计算HSL颜色
    positionToHsl: (x, y, centerX, centerY, radius) => {
        const dx = x - centerX;
        const dy = centerY - y;
        const distance = Math.min(Math.sqrt(dx * dx + dy * dy), radius);
        // 修正色相角度计算，使圆盘与滑块保持一致
        const angle = (Math.atan2(-dy, dx) * 180 / Math.PI + 360) % 360;

        return {
            h: angle,
            s: (distance / radius) * 100,
            l: 50
        };
    },

    // 通用颜色字符串解析函数，支持HEX、RGB、RGBA、HSL、HSLA格式
    // 确保返回包含完整的h、s、l、r、g、b、a属性的对象
    colorStringToObject: (colorStr) => {
        if (!colorStr || typeof colorStr !== 'string') {
            return null;
        }

        // 去除空格，便于解析
        colorStr = colorStr.trim().replace(/\s+/g, '');

        // 确保所有返回值都包含完整的属性
        const result = {
            h: 0,
            s: 0,
            l: 0,
            r: 0,
            g: 0,
            b: 0,
            a: 100
        };

        // 尝试解析HEX格式
        if (/^#[0-9A-Fa-f]{3,6}$/.test(colorStr)) {
            const rgb = ColorUtils.hexToRgb(colorStr);
            if (rgb) {
                const hsl = ColorUtils.rgbToHsl(rgb.r, rgb.g, rgb.b);
                if (hsl) {
                    return {
                        h: hsl.h || 0,
                        s: hsl.s || 0,
                        l: hsl.l || 0,
                        r: rgb.r || 0,
                        g: rgb.g || 0,
                        b: rgb.b || 0,
                        a: 100
                    };
                }
            }
        }

        // 尝试解析RGB格式
        const rgbMatch = colorStr.match(/^rgb\((\d+),(\d+),(\d+)\)$/i);
        if (rgbMatch) {
            const r = parseInt(rgbMatch[1]) || 0;
            const g = parseInt(rgbMatch[2]) || 0;
            const b = parseInt(rgbMatch[3]) || 0;
            const hsl = ColorUtils.rgbToHsl(r, g, b);
            if (hsl) {
                return {
                    h: hsl.h || 0,
                    s: hsl.s || 0,
                    l: hsl.l || 0,
                    r: r,
                    g: g,
                    b: b,
                    a: 100
                };
            }
        }

        // 尝试解析RGBA格式
        const rgbaMatch = colorStr.match(/^rgba\((\d+),(\d+),(\d+),(0|1|0\.\d+)\)$/i);
        if (rgbaMatch) {
            const r = parseInt(rgbaMatch[1]) || 0;
            const g = parseInt(rgbaMatch[2]) || 0;
            const b = parseInt(rgbaMatch[3]) || 0;
            const a = Math.round(parseFloat(rgbaMatch[4]) * 100) || 100;
            const hsl = ColorUtils.rgbToHsl(r, g, b);
            if (hsl) {
                return {
                    h: hsl.h || 0,
                    s: hsl.s || 0,
                    l: hsl.l || 0,
                    r: r,
                    g: g,
                    b: b,
                    a: a
                };
            }
        }

        // 尝试解析HSL格式
        const hslMatch = colorStr.match(/^hsl\((\d+),(\d+)%?,(\d+)%?\)$/i);
        if (hslMatch) {
            const h = parseInt(hslMatch[1]) || 0;
            const s = parseInt(hslMatch[2]) || 0;
            const l = parseInt(hslMatch[3]) || 0;
            const rgb = ColorUtils.hslToRgb(h, s, l);
            if (rgb) {
                return {
                    h: h,
                    s: s,
                    l: l,
                    r: rgb.r || 0,
                    g: rgb.g || 0,
                    b: rgb.b || 0,
                    a: 100
                };
            }
        }

        // 尝试解析HSLA格式
        const hslaMatch = colorStr.match(/^hsla\((\d+),(\d+)%?,(\d+)%?,(0|1|0\.\d+)\)$/i);
        if (hslaMatch) {
            const h = parseInt(hslaMatch[1]) || 0;
            const s = parseInt(hslaMatch[2]) || 0;
            const l = parseInt(hslaMatch[3]) || 0;
            const a = Math.round(parseFloat(hslaMatch[4]) * 100) || 100;
            const rgb = ColorUtils.hslToRgb(h, s, l);
            if (rgb) {
                return {
                    h: h,
                    s: s,
                    l: l,
                    r: rgb.r || 0,
                    g: rgb.g || 0,
                    b: rgb.b || 0,
                    a: a
                };
            }
        }

        return null;
    },

    // 从HSL计算圆盘位置
    // l参数当前未使用，仅为保持函数名与参数的一致性及未来扩展
    hslToPosition: (h, s, l, centerX, centerY, radius) => {
        const radians = h * Math.PI / 180;
        const distance = (s / 100) * radius;

        // 修正Y轴方向，使圆盘与滑块保持一致
        return {
            x: centerX + distance * Math.cos(radians),
            y: centerY - distance * Math.sin(-radians)
        };
    }
};

// DOM引用
const colorPickerContainer = ref(null);
const colorSelector = ref(null);
const colorWheel = ref(null);
const ringContainer = ref(null);
const wheelMarker = ref(null);
const saturationMarker = ref(null);
const lightnessMarker = ref(null);
const alphaMarker = ref(null);

// 状态变量
const currentColor = reactive({ ...props.initialColor });
const initialColor = ref({ ...props.initialColor });
const backgroundColor = ref('transparent');
const isSaturationLocked = ref(false);
const isDraggingWheel = ref(false);
const isDraggingRing = ref(false);
const currentDraggingSegmentType = ref(null);
const wheelData = ref(null);
const ringData = ref(null);
const colorFormat = ref('hex'); // 默认颜色格式为HEX
const colorValue = ref(''); // 颜色值文本
const copyToastVisible = ref(false); // 复制成功提示的可见性

// 预定义颜色
const presetColors = [
    { value: '#FF0000', name: '红色' },             // HEX格式
    { value: 'rgb(0, 255, 0)', name: '绿色' },       // RGB格式
    { value: 'rgb(0, 0, 255)', name: '蓝色' }, // RGBA格式
    { value: 'hsl(60, 100%, 50%)', name: '黄色' },   // HSL格式
    { value: 'hsl(300, 100%, 50%)', name: '品红' }, // HSLA格式
    { value: 'hsl(180, 100%, 50%)', name: '青色' },  // 改为HSL字符串格式
    { value: 'hsl(45, 100%, 50%)', name: '橙色' },   // 改为HSL字符串格式
    { value: 'hsl(90, 100%, 50%)', name: '黄绿色' }, // 改为HSL字符串格式
    { value: 'hsl(270, 100%, 50%)', name: '紫色' }   // 改为HSL字符串格式
];

// 背景色选项
const bgColors = ['transparent', '#ffffff', '#808080', '#000000'];

// 收藏颜色相关
const favoriteColors = ref([]);
const STORAGE_KEY = 'colorPickerFavoriteColors';
const touchStartX = ref(0);
const touchStartY = ref(0);
const isDragging = ref(false);
const draggedColorIndex = ref(null);
const DRAG_THRESHOLD = 50; // 拖出阈值

// 定义三个分段环弧的起始角度和占用角度
const segments = [
    { startAngle: 160, arcAngle: 100, type: 'saturation' },  // 160度到260度
    { startAngle: 280, arcAngle: 100, type: 'lightness' },   // -80度到20度（280度到380度，即280度到20度）
    { startAngle: 40, arcAngle: 100, type: 'alpha' }         // 40度到140度
];

// 计算属性
const previewColor = computed(() => {
    const { r, g, b, a } = currentColor;
    return `rgba(${r}, ${g}, ${b}, ${a / 100})`;
});

const initialColorStyle = computed(() => {
    const { r, g, b, a } = initialColor.value;
    return `rgba(${r}, ${g}, ${b}, ${a / 100})`;
});

/**
 * 创建色彩选择器的环形控件
 * @param {HTMLElement} element - 要渲染环形的DOM元素
 * @param {Object} currentColor - HSLA格式的基础颜色对象，包含.h, .s, .l, .a属性
 * @returns {Object} 返回包含canvas信息的对象
 */
const createRing = (element, currentColor = null) => {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    const size = 220;
    const scale = 2;
    canvas.width = size * scale;
    canvas.height = size * scale;
    canvas.style.width = `${size}px`;
    canvas.style.height = `${size}px`;
    canvas.className = 'lightness-ring';
    canvas.style.zIndex = '0'; // 确保亮度环位于色盘下层

    // 只删除已经存在的canvas元素，保留其他元素如ring-marker
    const existingCanvases = element.querySelectorAll('canvas');
    existingCanvases.forEach(canvasEl => {
        element.removeChild(canvasEl);
    });
    element.appendChild(canvas);

    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const outerRadius = canvas.width / 2;
    const innerRadius = outerRadius * 0.87; // 环的宽度，设置为外半径的0.9倍，使内径大于色盘的外径

    // 为每个分段绘制环弧
    segments.forEach(segment => {
        if (ctx.createConicGradient) {
            // 使用圆锥渐变创建环弧
            const gradient = ctx.createConicGradient(segment.startAngle * Math.PI / 180, centerX, centerY);

            // 声明起始颜色和结束颜色变量
            let startColor, endColor;

            // 根据环弧类型设置不同的渐变颜色
            if (segment.type === 'saturation') {
                // 饱和度环弧：从基于当前h值的基色（固定s=100%）到灰色的渐变
                // 为饱和度弧创建基于当前h值的基色（固定s=100%，l=50%）
                const saturationBaseColor = ColorUtils.hslToRgb(currentColor.h, 100, 50);
                startColor = `rgba(${saturationBaseColor.r}, ${saturationBaseColor.g}, ${saturationBaseColor.b}, 1)`;
                endColor = 'rgba(128, 128, 128, 1)';
                gradient.addColorStop(0, startColor);
                gradient.addColorStop(segment.arcAngle / 360, endColor);
                gradient.addColorStop((segment.arcAngle + 20) / 360, endColor);
                gradient.addColorStop(1, startColor);
            } else if (segment.type === 'lightness') {
                // 亮度环弧：从白色到黑色的渐变
                const lightnessBaseColor = ColorUtils.hslToRgb(currentColor.h, currentColor.s, 50)
                startColor = 'rgba(255, 255, 255, 1)'
                endColor = 'rgba(0, 0, 0, 1)'
                gradient.addColorStop(0, startColor);
                gradient.addColorStop(segment.arcAngle / 720, `rgba(${lightnessBaseColor.r}, ${lightnessBaseColor.g}, ${lightnessBaseColor.b}, 1)`);
                gradient.addColorStop(segment.arcAngle / 360, endColor);
                gradient.addColorStop((segment.arcAngle + 20) / 360, endColor);
                gradient.addColorStop(1, startColor);
            } else if (segment.type === 'alpha') {
                // 透明度环弧：从透明到基色的渐变
                startColor = `rgba(${currentColor.r}, ${currentColor.g}, ${currentColor.b}, 0)`
                endColor = `rgba(${currentColor.r}, ${currentColor.g}, ${currentColor.b}, 1)`
                gradient.addColorStop(0, startColor);
                gradient.addColorStop(segment.arcAngle / 360, endColor);
                gradient.addColorStop((segment.arcAngle + 20) / 360, endColor);
                gradient.addColorStop(1, startColor);
            }

            // 创建一个封闭的圆角环弧图形
            const ringWidth = outerRadius - innerRadius;
            const circleRadius = ringWidth / 2; // 圆的半径为环宽度的一半
            const midRadius = innerRadius + circleRadius; // 圆心位于内外半径之间的中点

            // 计算起始点和结束点的角度（弧度）
            const startAngleRad = segment.startAngle * Math.PI / 180;
            const endAngleRad = (segment.startAngle + segment.arcAngle) * Math.PI / 180;

            // 计算起始点和结束点的圆心坐标
            const startPointX = centerX + midRadius * Math.cos(startAngleRad);
            const startPointY = centerY + midRadius * Math.sin(startAngleRad);
            const endPointX = centerX + midRadius * Math.cos(endAngleRad);
            const endPointY = centerY + midRadius * Math.sin(endAngleRad);

            // 创建一个封闭的路径
            ctx.beginPath();

            // 1. 绘制外圆弧（顺时针方向）
            ctx.arc(centerX, centerY, outerRadius, startAngleRad, endAngleRad);

            // 2. 绘制结束点的圆角（连接外圆和内圆）
            ctx.arc(endPointX, endPointY, circleRadius, endAngleRad, endAngleRad + Math.PI);

            // 3. 绘制内圆弧（逆时针方向）
            ctx.arc(centerX, centerY, innerRadius, endAngleRad, startAngleRad, true);

            // 4. 绘制起始点的圆角（连接内圆和外圆）
            ctx.arc(startPointX, startPointY, circleRadius, startAngleRad + Math.PI, startAngleRad);

            // 封闭路径
            ctx.closePath();

            // 应用渐变和模糊效果并填充
            ctx.fillStyle = gradient;
            ctx.fill();
        }
    });

    return {
        canvas,
        centerX: centerX / scale,
        centerY: centerY / scale,
        outerRadius: outerRadius / scale,
        innerRadius: innerRadius / scale
    };
};

// 创建颜色圆盘
const createColorWheel = (element) => {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    // 确保size始终为正数，即使元素尚未完全渲染样式
    const size = 200;
    const scale = 2;
    canvas.width = size * scale;
    canvas.height = size * scale;
    canvas.style.width = `${size}px`;
    canvas.style.height = `${size}px`;
    element.appendChild(canvas);

    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = canvas.width / 2 * 0.8; // 缩小色盘，为色相环留出空间

    const imageData = ctx.createImageData(canvas.width, canvas.height);
    const pixels = imageData.data;

    for (let y = 0; y < canvas.height; y++) {
        for (let x = 0; x < canvas.width; x++) {
            const dx = x - centerX;
            const dy = centerY - y;
            const distance = Math.sqrt(dx * dx + dy * dy);

            if (distance <= radius) {
                // 复用positionToHsl函数计算HSL颜色值
                const hsl = ColorUtils.positionToHsl(x, y, centerX, centerY, radius);

                const rgb = ColorUtils.hslToRgb(hsl.h, hsl.s, hsl.l);
                const index = (y * canvas.width + x) * 4;
                pixels[index] = rgb.r;
                pixels[index + 1] = rgb.g;
                pixels[index + 2] = rgb.b;
                pixels[index + 3] = 255;
            }
        }
    }

    ctx.putImageData(imageData, 0, 0);
    ctx.filter = 'blur(1px)';
    ctx.drawImage(canvas, 0, 0);
    ctx.filter = 'none';

    return {
        canvas,
        centerX: centerX / scale,
        centerY: centerY / scale,
        radius: radius / scale
    };
};

// 根据当前颜色创建亮度环
const createRingWithCurrentColor = () => {
    if (ringContainer.value) {
        ringData.value = createRing(ringContainer.value, currentColor);
    }
};

// 更新颜色显示
/**
 * 更新颜色显示
 * 包括环形控件、标记位置和颜色值显示
 */
const updateColorDisplay = () => {
    createRingWithCurrentColor();
    updateMarkerPositions();
    emit('color-change', { ...currentColor });

    // 根据当前选择的颜色格式更新颜色值显示
    updateColorValue();

    // 同时触发update:modelValue事件，使用当前格式的颜色字符串值
    emit('update:modelValue', colorValue.value);
};

/**
 * 根据当前选择的颜色格式更新颜色值显示
 */
const updateColorValue = () => {
    const { r, g, b, a, h, s, l } = currentColor;

    switch (colorFormat.value) {
        case 'hex':
            colorValue.value = ColorUtils.rgbToHex(r, g, b);
            break;
        case 'rgb':
            colorValue.value = `rgb(${r}, ${g}, ${b})`;
            break;
        case 'rgba':
            colorValue.value = `rgba(${r}, ${g}, ${b}, ${a / 100})`;
            break;
        case 'hsl':
            colorValue.value = `hsl(${h}, ${s}%, ${l}%)`;
            break;
        case 'hsla':
            colorValue.value = `hsla(${h}, ${s}%, ${l}%, ${a / 100})`;
            break;
    }
};

/**
 * 根据颜色字符串检测并设置颜色格式
 * @param {string} colorStr - 颜色字符串
 */
const detectAndSetColorFormat = (colorStr) => {
    if (!colorStr || typeof colorStr !== 'string') {
        return;
    }

    // 去除空格，便于解析
    const cleanValue = colorStr.trim().replace(/\s+/g, '');

    // 检测颜色格式
    if (/^#[0-9A-Fa-f]{3,6}$/.test(cleanValue)) {
        colorFormat.value = 'hex';
    } else if (/^rgb\(\d+,\d+,\d+\)$/i.test(cleanValue)) {
        colorFormat.value = 'rgb';
    } else if (/^rgba\(\d+,\d+,\d+,(0|1|0\.\d+)\)$/i.test(cleanValue)) {
        colorFormat.value = 'rgba';
    } else if (/^hsl\(\d+,\d+%?,(\d+)%?\)$/i.test(cleanValue)) {
        colorFormat.value = 'hsl';
    } else if (/^hsla\(\d+,\d+%?,(\d+)%?,(0|1|0\.\d+)\)$/i.test(cleanValue)) {
        colorFormat.value = 'hsla';
    }
};

/**
 * 处理modelValue变化并更新内部颜色状态
 * @param {string} colorStr - 颜色字符串
 */
const handleModelValueChange = (colorStr) => {
    if (!colorStr) return;

    const parsedColor = ColorUtils.colorStringToObject(colorStr);
    if (parsedColor) {
        detectAndSetColorFormat(colorStr);
        initialColor.value = { ...parsedColor };
        Object.assign(currentColor, parsedColor);
        updateColorDisplay();
    }
};

/**
 * 处理颜色格式选择变化
 * 当颜色格式改变时，更新颜色值显示并触发v-model更新
 */
const handleColorFormatChange = () => {
    updateColorValue();
    // 触发update:modelValue事件，使v-model绑定的值也随着格式变化而更新
    emit('update:modelValue', colorValue.value);
};

/**
 * 处理颜色值输入变化
 */
const handleColorValueInput = () => {
    try {
        const parsedColor = ColorUtils.colorStringToObject(colorValue.value);
        if (parsedColor) {
            // 检测并设置颜色格式
            detectAndSetColorFormat(colorValue.value);
            // 更新currentColor的所有属性
            currentColor.h = parsedColor.h;
            currentColor.s = parsedColor.s;
            currentColor.l = parsedColor.l;
            currentColor.r = parsedColor.r;
            currentColor.g = parsedColor.g;
            currentColor.b = parsedColor.b;
            currentColor.a = parsedColor.a || 100;

            // 更新UI显示
            updateColorDisplay();
        }
    } catch (error) {
        // 忽略无效的颜色格式输入
    }
};

/**
 * 复制颜色值到剪贴板
 */
const copyColorToClipboard = async () => {
    try {
        await navigator.clipboard.writeText(colorValue.value);
        copyToastVisible.value = true;
        setTimeout(() => {
            copyToastVisible.value = false;
        }, 2000);
    } catch (error) {
        console.error('复制到剪贴板失败:', error);
    }
};

// 更新标记位置
const updateMarkerPositions = () => {
    if (!wheelData.value || !ringData.value) return;

    const { h, s, l, a } = currentColor;

    // 颜色圆盘标记
    const pos = ColorUtils.hslToPosition(
        h, s, l,
        wheelData.value.centerX, wheelData.value.centerY,
        wheelData.value.radius
    );
    if (wheelMarker.value) {
        wheelMarker.value.style.left = `${pos.x}px`;
        wheelMarker.value.style.top = `${pos.y}px`;
        wheelMarker.value.style.display = 'block';
        const wheelRgb = ColorUtils.hslToRgb(h, s, 50); // 使用固定亮度值50%，与色盘一致
        wheelMarker.value.style.backgroundColor = `rgb(${wheelRgb.r}, ${wheelRgb.g}, ${wheelRgb.b})`;
    }

    // 饱和度环弧标记 - 根据当前饱和度值计算角度位置
    if (saturationMarker.value) {
        const saturationAngle = 160 + (100 - s);
        const saturationDistanceFromCenter = (ringData.value.innerRadius + ringData.value.outerRadius) / 2;
        const saturationPosX = ringData.value.centerX + Math.cos(saturationAngle * Math.PI / 180) * saturationDistanceFromCenter;
        const saturationPosY = ringData.value.centerY + Math.sin(saturationAngle * Math.PI / 180) * saturationDistanceFromCenter;

        saturationMarker.value.style.left = `${saturationPosX}px`;
        saturationMarker.value.style.top = `${saturationPosY}px`;
        saturationMarker.value.style.display = 'block';
    }

    // 亮度环弧标记 - 根据当前亮度值计算角度位置
    if (lightnessMarker.value) {
        let lightnessAngle = 280 + (100 - l);
        if (lightnessAngle > 360) {
            lightnessAngle -= 360;
        }
        const lightnessDistanceFromCenter = (ringData.value.innerRadius + ringData.value.outerRadius) / 2;
        const lightnessPosX = ringData.value.centerX + Math.cos(lightnessAngle * Math.PI / 180) * lightnessDistanceFromCenter;
        const lightnessPosY = ringData.value.centerY + Math.sin(lightnessAngle * Math.PI / 180) * lightnessDistanceFromCenter;

        lightnessMarker.value.style.left = `${lightnessPosX}px`;
        lightnessMarker.value.style.top = `${lightnessPosY}px`;
        lightnessMarker.value.style.display = 'block';
    }

    // 透明度环弧标记 - 根据当前透明度值计算角度位置
    if (alphaMarker.value) {
        const alphaAngle = 40 + a;
        const alphaDistanceFromCenter = (ringData.value.innerRadius + ringData.value.outerRadius) / 2;
        const alphaPosX = ringData.value.centerX + Math.cos(alphaAngle * Math.PI / 180) * alphaDistanceFromCenter;
        const alphaPosY = ringData.value.centerY + Math.sin(alphaAngle * Math.PI / 180) * alphaDistanceFromCenter;

        alphaMarker.value.style.left = `${alphaPosX}px`;
        alphaMarker.value.style.top = `${alphaPosY}px`;
        alphaMarker.value.style.display = 'block';
    }

    // 为所有标记设置当前最终输出颜色
    const rgb = ColorUtils.hslToRgb(h, s, l);
    // 复用已声明的变量，不再重复声明
    if (saturationMarker.value) {
        saturationMarker.value.style.backgroundColor = `rgb(${rgb.r}, ${rgb.g}, ${rgb.b})`;
    }
    if (lightnessMarker.value) {
        lightnessMarker.value.style.backgroundColor = `rgb(${rgb.r}, ${rgb.g}, ${rgb.b})`;
    }
    if (alphaMarker.value) {
        alphaMarker.value.style.backgroundColor = `rgb(${rgb.r}, ${rgb.g}, ${rgb.b})`;
    }
};

// 处理颜色圆盘交互
const handleWheelInteraction = (clientX, clientY) => {
    if (!wheelData.value) return;

    const rect = wheelData.value.canvas.getBoundingClientRect();
    const x = clientX - rect.left;
    const y = clientY - rect.top;

    const hsl = ColorUtils.positionToHsl(
        x, y,
        wheelData.value.centerX, wheelData.value.centerY,
        wheelData.value.radius
    );

    // 同时更新HSL和RGB值
    const h = Math.round(hsl.h);
    const s = Math.round(hsl.s);
    const l = currentColor.l; // 保持当前亮度值
    currentColor.h = h;
    if (!isSaturationLocked.value) {
        currentColor.s = s; // 只有在饱和度未锁定时才更新s值
    }
    // 从HSL转换为RGB并更新
    const rgb = ColorUtils.hslToRgb(h, currentColor.s, l);
    currentColor.r = rgb.r;
    currentColor.g = rgb.g;
    currentColor.b = rgb.b;

    updateColorDisplay();
};

// 从色盘位置检测是否在色彩区域内
const isPositionInColorWheel = (clientX, clientY) => {
    if (!wheelData.value) return false;

    const rect = wheelData.value.canvas.getBoundingClientRect();
    const x = clientX - rect.left;
    const y = clientY - rect.top;

    const dx = x - wheelData.value.centerX;
    const dy = y - wheelData.value.centerY;
    const distance = Math.sqrt(dx * dx + dy * dy);

    // 检查是否在色盘半径范围内
    return distance <= wheelData.value.radius * 1.1; // 添加一些容差范围
};

/**
 * 处理颜色选择器的交互事件（同时支持鼠标和触摸）
 * @param {Event} e - 事件对象
 * @param {boolean} isTouch - 是否为触摸事件
 */
const handleColorSelectorInteraction = (e, isTouch) => {
    let clientX, clientY;

    if (isTouch) {
        if (e.touches.length === 0) return;
        const touch = e.touches[0];
        clientX = touch.clientX;
        clientY = touch.clientY;
    } else {
        clientX = e.clientX;
        clientY = e.clientY;
    }

    // 只有当鼠标按下位置在色盘色彩区域内时，才触发交互
    if (isPositionInColorWheel(clientX, clientY)) {
        isDraggingWheel.value = true;
        handleWheelInteraction(clientX, clientY);
        e.preventDefault();
        e.stopPropagation();
    } else {
        // 分段环弧交互
        if (ringData.value) {
            const rect = ringData.value.canvas.getBoundingClientRect();
            const x = clientX - rect.left;
            const y = clientY - rect.top;

            if (handleRingInteraction(x, y)) {
                e.preventDefault();
                e.stopPropagation(); // 阻止事件冒泡到色盘
            }
        }
    }
};

/**
 * 统一处理色盘选择器的移动事件（鼠标和触摸）
 * @param {Event} e - 事件对象
 * @param {boolean} isTouch - 是否为触摸事件
 */
const handleColorSelectorMove = (e, isTouch) => {
    if (!wheelData.value) return;

    // 根据事件类型获取坐标
    const clientX = isTouch ? e.touches[0].clientX : e.clientX;
    const clientY = isTouch ? e.touches[0].clientY : e.clientY;

    if (isDraggingWheel.value) {
        // 处理色盘交互
        handleWheelInteraction(clientX, clientY);
        e.preventDefault();
        e.stopPropagation();
    } else if (isDraggingRing.value && currentDraggingSegmentType.value) {
        // 处理分段环弧交互
        if (ringData.value) {
            const rect = ringData.value.canvas.getBoundingClientRect();
            const x = clientX - rect.left;
            const y = clientY - rect.top;
            updateColorByRingPostion(x, y, currentDraggingSegmentType.value);
            e.preventDefault();
            e.stopPropagation();
        }
    }
};

// 统一处理鼠标/触摸释放事件，重置拖拽状态
const handleColorSelectorRelease = () => {
    isDraggingWheel.value = false;
    isDraggingRing.value = false;
    currentDraggingSegmentType.value = null;
};

// 检查点击位置是否在某个环弧上，并返回对应的环弧类型
const getSegmentTypeAtPosition = (x, y) => {
    if (!ringData.value) return null;

    const centerX = ringData.value.centerX;
    const centerY = ringData.value.centerY;
    const dx = x - centerX;
    const dy = y - centerY;
    const distance = Math.sqrt(dx * dx + dy * dy);

    // 检查是否在环的宽度范围内
    if (distance < ringData.value.innerRadius * 0.9 || distance > ringData.value.outerRadius * 1.1) {
        return null;
    }

    // 计算点击位置的角度
    let angle = Math.atan2(dy, dx) * 180 / Math.PI;
    if (angle < 0) angle += 360;

    // 检查点击位置属于哪个环弧
    for (const segment of segments) {
        const endAngle = segment.startAngle + segment.arcAngle;

        // 处理跨越360度边界的情况
        if (endAngle > 360) {
            // 对于跨越360度边界的环弧（如亮度弧：280度到380度即280度到20度）
            if ((angle >= segment.startAngle - 5 && angle <= 360) || (angle >= 0 && angle <= endAngle - 360 + 5)) {
                return segment.type;
            }
        } else {
            // 普通环弧（不跨越360度边界）
            if (angle >= segment.startAngle - 5 && angle <= endAngle + 5) {
                return segment.type;
            }
        }
    }

    return null;
};

// 从环弧位置计算对应的值
const getValueFromSegmentPosition = (x, y, segmentType) => {
    if (!ringData.value) return null;

    const centerX = ringData.value.centerX;
    const centerY = ringData.value.centerY;
    const dx = x - centerX;
    const dy = y - centerY;
    let angle = Math.atan2(dy, dx) * 180 / Math.PI;
    if (angle < 0) angle += 360;

    // 根据不同的环弧类型计算值
    for (const segment of segments) {
        if (segment.type === segmentType) {
            // 计算在当前环弧中的相对位置
            let relativePosition;
            const endAngle = segment.startAngle + segment.arcAngle;

            // 处理跨越360度边界的情况
            if (endAngle > 360) {
                if (angle >= segment.startAngle) {
                    // 角度在起始角度到360度之间
                    relativePosition = (angle - segment.startAngle) / segment.arcAngle;
                } else {
                    // 角度在0度到结束角度减去360度之间
                    if (angle < segment.startAngle && angle <= 180) {
                        angle += 360;
                    }
                    relativePosition = (angle - segment.startAngle) / segment.arcAngle;
                }
            } else {
                // 普通环弧（不跨越360度边界）
                let ag = angle - segment.startAngle;
                if (ag > 280) { //超过半个圆设为反方向
                    ag -= 360;
                }
                relativePosition = ag / segment.arcAngle;
            }
            // 确保相对位置在0-1范围内
            const clampedPosition = Math.max(0, Math.min(1, relativePosition));

            // 根据环弧类型返回不同的值
            if (segmentType === 'saturation') {
                return Math.round((1 - clampedPosition) * 100); // 饱和度从100%到0%
            } else if (segmentType === 'lightness') {
                return Math.round((1 - clampedPosition) * 100); // 亮度从100%到0%
            } else if (segmentType === 'alpha') {
                return Math.round(clampedPosition * 100); // 透明度从0%到100%
            }
        }
    }

    return null;
};

const updateColorByRingPostion = (x, y, currentDraggingSegmentType) => {
    // 根据鼠标按下时确定的环弧类型和当前角度计算值
    const value = getValueFromSegmentPosition(x, y, currentDraggingSegmentType);
    if (value !== null) {
        // 获取当前颜色的HSL值
        const { h, s, l } = currentColor;

        if (currentDraggingSegmentType === 'saturation') {
            currentColor.s = value;
            // 更新RGB值
            const rgb = ColorUtils.hslToRgb(h, value, l);
            currentColor.r = rgb.r;
            currentColor.g = rgb.g;
            currentColor.b = rgb.b;
        } else if (currentDraggingSegmentType === 'lightness') {
            currentColor.l = value;
            // 更新RGB值
            const rgb = ColorUtils.hslToRgb(h, s, value);
            currentColor.r = rgb.r;
            currentColor.g = rgb.g;
            currentColor.b = rgb.b;
        } else if (currentDraggingSegmentType === 'alpha') {
            currentColor.a = value;
            // 透明度不影响RGB值
        }
        updateColorDisplay();
    }
};

/**
 * 处理环弧交互的函数
 * @param {number} x - 相对于canvas的x坐标
 * @param {number} y - 相对于canvas的y坐标
 * @returns {boolean} - 是否处理了交互
 */
const handleRingInteraction = (x, y) => {
    // 检查点击位置属于哪个环弧
    const segmentType = getSegmentTypeAtPosition(x, y);

    if (segmentType) {
        isDraggingRing.value = true;
        currentDraggingSegmentType.value = segmentType;
        updateColorByRingPostion(x, y, segmentType);
        return true;
    }
    return false;
};

// 切换饱和度锁定状态
const toggleSaturationLock = () => {
    isSaturationLocked.value = !isSaturationLocked.value;
};

// 更新背景色
const updateBackgroundColor = (index) => {
    if (index === 0) {
        const elementStyles = getComputedStyle(colorPickerContainer.value);
        backgroundColor.value = elementStyles.getPropertyValue('--bg-color').trim();
    } else {
        backgroundColor.value = bgColors[index];
    }
};

// 计算点击位置对应的索引
// 注意：DOM事件对象中没有直接提供相对于元素的坐标值
// 需要通过getBoundingClientRect()计算获得元素内部坐标
const getBgColorIndex = (element, clientY) => {
    if (!colorPickerContainer.value || !element) return 0;

    // 使用getBoundingClientRect()获取元素位置信息
    const rect = element.getBoundingClientRect();
    // 计算事件位置相对于元素顶部的y坐标（元素内部y值）
    const localY = clientY - rect.top;
    const relativeY = Math.max(0, Math.min(1, localY / rect.height));
    return Math.floor(relativeY * bgColors.length);
};

// 处理背景色滑块点击
const handleBgColorClick = (e) => {
    // 在事件处理函数中，可以使用currentTarget获取当前绑定事件的元素
    const bgColorSlider = e.currentTarget;
    // 使用clientY和currentTarget计算元素内部的y值
    const index = getBgColorIndex(bgColorSlider, e.clientY);
    updateBackgroundColor(index);
};

// 处理背景色滑块触摸
const handleBgColorTouchStart = (e) => {
    if (e.touches.length > 0) {
        // 在触摸事件中，同样可以使用currentTarget获取事件绑定的元素
        const bgColorSlider = e.currentTarget;
        // 使用触摸点的clientY计算元素内部的y值
        const index = getBgColorIndex(bgColorSlider, e.touches[0].clientY);
        updateBackgroundColor(index);
        e.preventDefault();
    }
};

// 选择预定义颜色
const selectPresetColor = (index) => {
    if (index < presetColors.length) {
        const presetColor = presetColors[index];

        // 解析字符串格式的颜色值
        const parsedColor = ColorUtils.colorStringToObject(presetColor.value);
        if (parsedColor) {
            // 更新currentColor的所有属性
            currentColor.h = parsedColor.h;
            currentColor.s = parsedColor.s;
            currentColor.l = parsedColor.l;
            currentColor.r = parsedColor.r;
            currentColor.g = parsedColor.g;
            currentColor.b = parsedColor.b;
            currentColor.a = parsedColor.a || 100;
        }

        updateColorDisplay();
    }
};

// 重置到初始颜色
const resetToInitialColor = () => {
    // 复制初始颜色到当前颜色
    Object.assign(currentColor, { ...initialColor.value });
    // 更新显示
    updateColorDisplay();
};

// 从localStorage加载收藏颜色
const loadFavoriteColorsFromStorage = () => {
    try {
        const storedColors = localStorage.getItem(STORAGE_KEY);
        if (storedColors) {
            const parsedColors = JSON.parse(storedColors);
            for (let i = 0; i < 10; i++) {
                favoriteColors.value[i] = parsedColors[i] || null;
            }
        } else {
            // 首次使用，初始化为空
            for (let i = 0; i < 10; i++) {
                favoriteColors.value[i] = null;
            }
        }
    } catch (error) {
        console.error('加载收藏颜色失败:', error);
        // 出错时全部初始化为空
        for (let i = 0; i < 10; i++) {
            favoriteColors.value[i] = null;
        }
    }
};

// 保存收藏颜色到localStorage
const saveFavoriteColorsToStorage = () => {
    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(favoriteColors.value));
    } catch (error) {
        console.error('保存收藏颜色失败:', error);
    }
};

// 处理收藏颜色点击
const handleFavoriteClick = (index) => {
    if (favoriteColors.value[index]) {
        // 点击有收藏色的收藏位，应用该颜色
        const parsedColor = ColorUtils.colorStringToObject(favoriteColors.value[index]);
        if (parsedColor) {
            // 更新currentColor的所有属性
            currentColor.h = parsedColor.h;
            currentColor.s = parsedColor.s;
            currentColor.l = parsedColor.l;
            currentColor.r = parsedColor.r;
            currentColor.g = parsedColor.g;
            currentColor.b = parsedColor.b;
            currentColor.a = parsedColor.a || 100;
            updateColorDisplay();
        }
    } else {
        // 点击空白收藏位，收藏当前颜色
        const rgb = ColorUtils.hslToRgb(currentColor.h, currentColor.s, currentColor.l);
        favoriteColors.value[index] = ColorUtils.rgbToHex(rgb.r, rgb.g, rgb.b);
        saveFavoriteColorsToStorage();
    }
};

// 移除收藏颜色
const removeFavorite = (index) => {
    if (favoriteColors.value[index]) {
        favoriteColors.value[index] = null;
        saveFavoriteColorsToStorage();
    }
};

// 处理收藏颜色拖拽开始
const handleDragStart = (e, index) => {
    if (favoriteColors.value[index]) {
        e.dataTransfer.setData('text/plain', index.toString());
        // 设置拖拽时的透明度，提供视觉反馈
        e.target.style.opacity = '0.5';
    }
};

// 处理收藏颜色拖拽结束
const handleDragEnd = (e) => {
    // 恢复元素透明度
    e.target.style.opacity = '1';
};

// 处理触摸开始
const handleTouchStart = (e, index) => {
    // e.preventDefault();
    if (favoriteColors.value[index]) {
        const touch = e.touches[0];
        touchStartX.value = touch.clientX;
        touchStartY.value = touch.clientY;
        isDragging.value = false;
        draggedColorIndex.value = index;
        // 记录当前元素的初始位置
        e.target.dataset.originalTransform = e.target.style.transform || '';
    } else {
        handleFavoriteClick(index);
    }
};

// 处理触摸移动
const handleTouchMove = (e) => {
    if (draggedColorIndex.value !== null && favoriteColors.value[draggedColorIndex.value]) {
        const touch = e.touches[0];
        const dx = touch.clientX - touchStartX.value;
        const dy = touch.clientY - touchStartY.value;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance > 10) {
            isDragging.value = true;
            // 防止页面滚动
            // e.preventDefault();
            // 跟随手指移动元素
            e.target.style.transform = `translate(${dx}px, ${dy}px)`;
            // 提供视觉反馈
            e.target.style.opacity = '0.5';
            e.target.style.zIndex = '100'; // 确保在最上层
        }
    }
};

// 处理触摸结束
const handleTouchEnd = (e, index) => {
    if (draggedColorIndex.value !== null && favoriteColors.value[draggedColorIndex.value]) {
        const touch = e.changedTouches[0];
        const dx = touch.clientX - touchStartX.value;
        const dy = touch.clientY - touchStartY.value;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (isDragging.value && distance > DRAG_THRESHOLD) {
            // 拖出范围，删除该收藏色
            removeFavorite(draggedColorIndex.value);
        }

        // 恢复元素原始状态
        e.target.style.transform = e.target.dataset.originalTransform || '';
        e.target.style.opacity = '1';
        e.target.style.zIndex = '1';

        // 重置状态
        isDragging.value = false;
        draggedColorIndex.value = null;
    }
};

// 全局拖拽事件处理函数
const handleGlobalDragOver = (e) => {
    e.preventDefault(); // 允许放置
};

const handleGlobalDrop = (e) => {
    e.preventDefault();
    const colorIndex = e.dataTransfer.getData('text/plain');
    if (colorIndex !== '' && !isNaN(parseInt(colorIndex))) {
        // 从收藏位置删除颜色
        favoriteColors.value[parseInt(colorIndex)] = null;
        saveFavoriteColorsToStorage(); // 保存到本地存储
    }
};

// 初始化事件监听器
const initializeEventListeners = () => {
    if (!colorSelector.value || !colorWheel.value || !ringContainer.value) return;

    // 色盘交互 - 鼠标事件
    colorSelector.value.addEventListener('mousedown', (e) => handleColorSelectorInteraction(e, false));
    document.addEventListener('mousemove', (e) => handleColorSelectorMove(e, false));
    document.addEventListener('mouseup', handleColorSelectorRelease);

    // 色盘交互 - 触摸事件
    colorSelector.value.addEventListener('touchstart', (e) => handleColorSelectorInteraction(e, true));
    document.addEventListener('touchmove', (e) => handleColorSelectorMove(e, true), { passive: false });
    document.addEventListener('touchend', handleColorSelectorRelease);
    document.addEventListener('touchcancel', handleColorSelectorRelease);

    // 添加全局拖拽相关事件监听器
    document.addEventListener('dragover', handleGlobalDragOver);
    document.addEventListener('drop', handleGlobalDrop);
};

// 生命周期钩子
onMounted(() => {
    nextTick(() => {
        updateBackgroundColor(0);
        if (colorWheel.value) {
            wheelData.value = createColorWheel(colorWheel.value);
        }
        if (ringContainer.value) {
            ringData.value = createRing(ringContainer.value, currentColor);
        }
        initializeEventListeners();
        updateMarkerPositions();
        loadFavoriteColorsFromStorage();

        // 初始化颜色值显示
        updateColorValue();

        // 如果有modelValue传入，使用它来初始化颜色
        if (props.modelValue) {
            handleModelValueChange(props.modelValue);
        }

        // 设置IntersectionObserver来监测组件可见性变化
        setupVisibilityObserver();
    });
});

onBeforeUnmount(() => {
    document.removeEventListener('mousemove', (e) => handleColorSelectorMove(e, false));
    document.removeEventListener('mouseup', handleColorSelectorRelease);
    document.removeEventListener('touchmove', (e) => handleColorSelectorMove(e, true));
    document.removeEventListener('touchend', handleColorSelectorRelease);
    document.removeEventListener('touchcancel', handleColorSelectorRelease);

    // 移除全局拖拽相关事件监听器
    document.removeEventListener('dragover', handleGlobalDragOver);
    document.removeEventListener('drop', handleGlobalDrop);

    // 断开可见性观察器
    if (visibilityObserver.value) {
        visibilityObserver.value.disconnect();
    }
});

/**
 * 设置IntersectionObserver来监测组件可见性变化
 * 当组件从不可见变为可见时，重新读取存储的收藏色
 */
const setupVisibilityObserver = () => {
    if ('IntersectionObserver' in window && colorPickerContainer.value) {
        visibilityObserver.value = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                // 当组件变为可见时
                if (entry.isIntersecting) {
                    loadFavoriteColorsFromStorage();
                }
            });
        }, {
            threshold: 0.1 // 当至少10%的组件可见时触发
        });

        // 开始观察组件根元素
        visibilityObserver.value.observe(colorPickerContainer.value);
    }
};

// 监听props变化，更新当前颜色
const { initialColor: newInitialColor } = props;
if (JSON.stringify(newInitialColor) !== JSON.stringify(initialColor.value)) {
    initialColor.value = { ...newInitialColor };
    Object.assign(currentColor, { ...newInitialColor });
    updateColorDisplay();
}

// 监听modelValue变化，更新内部颜色
watch(() => props.modelValue, (newValue) => {
    if (newValue && newValue !== colorValue.value) {
        handleModelValueChange(newValue);
    }
}, { immediate: false });
</script>

<style>
/* 全局CSS变量定义 - 可在外部覆盖 */
:root {
    --chromawheel-bg-color: transparent;
}
</style>

<style scoped>
/* 亮度环样式 */
.lightness-ring {
    position: absolute;
    width: 100%;
    height: 100%;
    border-radius: 50%;
    pointer-events: auto;
}

/* 亮度环标记 - 调整大小与环的宽度匹配 */
.ring-marker {
    position: absolute;
    width: 14px;
    height: 14px;
    border: 2px solid white;
    border-radius: 50%;
    transform: translate(-50%, -50%);
    box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.3);
    pointer-events: auto;
    z-index: 10;
}

/* 颜色圆盘标记 */
.wheel-marker {
    position: absolute;
    width: 14px;
    height: 14px;
    border: 2px solid white;
    border-radius: 50%;
    box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.3);
    transform: translate(-50%, -50%);
    pointer-events: auto;
    z-index: 10;
}

/* 泪滴形状样式 */
.teardrop-left-bottom {
    width: 30px;
    height: 30px;
    border-radius: 50% 50% 50% 0;
    overflow: hidden;
}

.teardrop-right-bottom {
    width: 30px;
    height: 30px;
    border-radius: 50% 50% 0 50%;
    overflow: hidden;
}

.teardrop-left-top {
    width: 30px;
    height: 30px;
    border-radius: 0 50% 50% 50%;
    overflow: hidden;
}

.teardrop-right-top {
    width: 30px;
    height: 30px;
    border-radius: 50% 0 50% 50%;
    overflow: hidden;
}

/* 预定义颜色 */
.preset-color {
    position: absolute;
    cursor: pointer;
    transition: transform 0.2s ease;
    box-shadow: 0 0 2px 2px rgba(0, 0, 0, 0.2);
    border: 1px solid rgba(0, 0, 0, 0.5);
    z-index: 10;
}

.preset-color:hover {
    transform: scale(1.1);
}

/* 收藏颜色 */
.fav-color.filled {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    cursor: pointer;
    transition: transform 0.2s ease;
    box-shadow: 0 0 2px 2px rgba(0, 0, 0, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.5);
    pointer-events: auto;
}

.fav-color.filled:hover {
    transform: scale(1.1);
}

.fav-color.notfill {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #9ca3af;
    font-size: 12px;
    cursor: pointer;
    transition: border-color 0.2s ease;
    box-shadow: 0 0 2px 2px rgba(0, 0, 0, 0.2);
    border: 1px dashed #ffffff;
    pointer-events: auto;
}

.fav-color.notfill:hover {
    border-color: #9ca3af;
}

/* 颜色选择器容器 */
.color-picker-container {
    position: relative;
    width: 300px;
    height: 300px;
    margin: 0 auto;
    overflow: hidden;
    --bg-color: var(--chromawheel-bg-color);
}

/* 网格背景 */
.grid-background {
    position: absolute;
    inset: 0;
    background-image: repeating-conic-gradient(#000000 0deg 90deg, #FFFFFF 90deg 180deg);
    background-size: 8px 8px;
    opacity: 0.05;
    z-index: 0;
}

/* 颜色选择器 */
.color-selector {
    z-index: 5;
    position: absolute;
    left: 40px;
    top: 40px;
    filter: drop-shadow(0 0 6px rgba(0, 0, 0, 0.5));
}

/* 分段环弧容器 */
.ring-container {
    position: absolute;
    left: 0;
    top: 0;
    width: 220px;
    height: 220px;
}

/* 彩色圆盘 */
.color-wheel {
    position: absolute;
    left: 10px;
    top: 10px;
    width: 200px;
    height: 200px;
}

/* 颜色预览 */
.color-preview {
    position: absolute;
    top: 8px;
    left: 7px;
    width: 66px;
    height: 66px;
    border-radius: 50%;
    z-index: 10;
    border: 0px solid #808080;
}

/* 初始颜色 */
.color-start {
    position: absolute;
    top: 81px;
    left: 7px;
    width: 34px;
    height: 34px;
    border-radius: 50%;
    z-index: 10;
    border: 0px solid #808080;
}

/* 收藏颜色容器 */
.favorite-colors-bottom {
    position: absolute;
    left: 50%;
    bottom: 8px;
    transform: translateX(-50%);
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    z-index: 10;
}

.favorite-colors-right {
    position: absolute;
    top: 50%;
    right: 8px;
    transform: translateY(-50%);
    display: flex;
    flex-direction: column;
    gap: 6px;
    z-index: 10;
}

/* 饱和度锁定按钮 */
.lock-saturation {
    position: absolute;
    top: 30px;
    left: 142px;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 16px;
    height: 16px;
    color: #fff;
    background-color: #1f2937;
    border-radius: 50%;
    cursor: pointer;
    transition: transform 0.2s ease;
    pointer-events: auto;
    box-shadow: 0 0 2px 2px rgba(0, 0, 0, 0.2);
    z-index: 10;
}

.lock-saturation:hover {
    transform: scale(1.5);
}

/* 背景色切换区域 */
.bg-color-slider {
    border-radius: 8px;
    cursor: pointer;
    background: linear-gradient(to bottom,
            var(--chromawheel-bg-color) 0%, var(--chromawheel-bg-color) 25%,
            #ffffff 25%, #ffffff 50%,
            #808080 50%, #808080 75%,
            #000000 75%, #000000 100%);
    box-shadow: 0 0 2px 2px rgba(0, 0, 0, 0.2);
    z-index: 10;
    transition: opacity 0.2s ease;
}

/* 颜色输入区 */
.color-input-section {
    padding: 8px 16px 12px 16px;
}

.input-container {
    display: flex;
}

/* 颜色格式选择器 */
.color-format-select {
    width: 80px;
    padding: 6px 8px;
    border: none;
    background-color: #1f2937;
    border-radius: 6px 0 0 6px;
    outline: none;
    font-size: 12px;
    color: #ffffff;
}

/* 移除焦点边框 */
.color-format-select:focus {
    box-shadow: none;
    outline: none;
    border-color: transparent;
}

/* 颜色值输入框 */
.color-value-input {
    flex: 1;
    padding: 6px 8px;
    border-left: none;
    border: 1px solid #374151;
    background-color: #1f2937;
    outline: none;
    font-size: 12px;
    color: #ffffff;
}

.color-value-input:focus {
    box-shadow: none;
    outline: none;
    border-color: transparent;
}

/* 复制按钮 */
.copy-color-btn {
    background-color: #1f2937;
    border: 1px solid #374151;
    border-left: none;
    padding: 6px 8px;
    border-radius: 0 6px 6px 0;
    cursor: pointer;
    transition: background-color 0.3s ease;
    font-size: 12px;
    color: #d1d5db;
}

.copy-color-btn:hover {
    background-color: #4b5563;
}

/* 复制成功提示 */
.copy-toast {
    position: absolute;
    top: 300px;
    right: 16px;
    background-color: #1E293B;
    color: #ffffff;
    padding: 6px 12px;
    border-radius: 8px;
    box-shadow: 0 3px 6px rgba(0, 0, 0, 0.15), 0 2px 4px rgba(0, 0, 0, 0.12);
    opacity: 0;
    transition: opacity 0.3s ease;
    pointer-events: none;
    font-size: 12px;
    z-index: 100;
}

/* 复制成功提示显示状态 */
.copy-toast.visible {
    opacity: 1;
}
</style>