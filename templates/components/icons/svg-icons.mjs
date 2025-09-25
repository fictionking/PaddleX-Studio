// SVG图标库 - 集中管理所有自定义SVG图标
// 版本: 1.0.0
// 最后更新: "+new Date().toLocaleDateString('zh-CN')+"

// 从Vue实例获取所需功能
const { markRaw, defineComponent } = Vue;

// 存储所有图标定义的对象
const iconDefinitions = {
  'add-node-icon': {
    viewBox: '0 0 32 32',
    content: `<symbol id="add-node-icon" viewBox="0 0 32 32">
      <path fill="currentColor"
        d="M23.52,0a8.45,8.45,0,0,0-7.8,5.22l-.09.27H4a4,4,0,0,0-4,4v3.43H16.28l.22.4.85,1.05H0V28a4,4,0,0,0,4,4H19.86a4,4,0,0,0,4-4V17.07l1.39-.14A8.56,8.56,0,0,0,23.52,0ZM3.63,23.55a1.45,1.45,0,1,1,1.43-1.44A1.44,1.44,0,0,1,3.63,23.55Zm16.57,0a1.45,1.45,0,1,1,1.44-1.44A1.44,1.44,0,0,1,20.2,23.55ZM23.58,16A7.46,7.46,0,1,1,31,8.56,7.43,7.43,0,0,1,23.58,16Z" />
      <polygon fill="currentColor"
        points="28.66 7.58 28.66 9.96 24.8 9.96 24.8 13.86 22.43 13.86 22.43 9.96 18.57 9.96 18.57 7.58 22.43 7.58 22.43 3.68 24.8 3.68 24.8 7.58 28.66 7.58" />
    </symbol>`
  },

  'disk-icon': {
    viewBox: '0 0 256 256',
    content: `<symbol id="disk-icon" viewBox="0 0 256 256">
      <path fill="currentColor"
        d="M127.86,255.88h-101c-4.72,0-9.23-.33-13.59-2.51A22.3,22.3,0,0,1,.64,236.69,51.31,51.31,0,0,1,0,227.43Q0,127.59,0,27.72c0-3.89.07-7.78,1.32-11.54A22.6,22.6,0,0,1,22.4.55C28.1.29,33.81.25,39.48.32c6.13,0,7.91,1.78,8,7.81.06,6.73,0,13.49-.07,20.21q0,27.19,0,54.4c0,9.79.36,10.05,10,10.05q66.06,0,132.1-.06c4.41,0,8.8.19,13.18-.07,3.73-.2,5-1.68,5.31-5.37.13-1.55.07-3.1.07-4.65q0-36.15,0-72.27c0-3.36-.56-7.21,2.9-9.09,3.92-2.11,8.18-1.19,11.87,1.05a54.56,54.56,0,0,1,8.67,6.56c5.27,5,10.28,10.22,15.39,15.36,1.09,1.12,1.95,2.41,3,3.6,4.45,5.07,6.13,10.81,6.1,17.77-.23,59.83-.1,119.67-.07,179.5v6.23c0,10.85-6.19,17.67-14.9,22.81-2.73,1.62-6,1.62-9.1,1.62-10.88.06-21.75.13-32.63.13Q163.59,255.91,127.86,255.88Zm-.6-18.56v.06h83.08a31.53,31.53,0,0,0,4.65-.26,4.48,4.48,0,0,0,4.09-4,37.49,37.49,0,0,0,.26-5.41q.19-44.66.4-89.27a23,23,0,0,0-.14-3.1c-.59-5.28-2.17-6.79-7.38-6.89-3.1,0-6.2.13-9.33.13q-78.42,0-156.85-.07c-9.63,0-10.22.56-10.22,10q-.06,44.66,0,89.31a36.2,36.2,0,0,0,.3,5.41c.33,2.4,1.61,3.62,4.12,3.89,2.3.23,4.65.23,7,.23Z">
      </path>
      <path fill="currentColor"
        d="M128.22.52H177.9c3.1,0,6.2-.13,9.3-.23,9.2-.3,10.55.89,10.62,9.82.06,6-.14,11.9-.14,17.87q0,20.57.07,41.14c0,1.55,0,3.1,0,4.65-.2,7.38-1.75,8.93-9.36,8.93-18.37,0-36.76-.16-55.12-.13-22,0-44,.2-66,.26a20.83,20.83,0,0,1-5.34-.65,4.76,4.76,0,0,1-3.73-4.46c-.13-2-.2-4.12-.2-6.19q0-31.45,0-62.9c0-6.89,1.41-8.34,8-8.34,2.61,0,5.18.13,7.75.16h54.36A.11.11,0,0,1,128.22.52Zm45.2,41.21c0-7.26.1-14.51,0-21.76,0-4.91-1.55-6.56-6.43-6.83S157.17,13,152.26,13c-4.39.1-5.94,1.65-6.5,6.07a18.32,18.32,0,0,0-.1,2.34c0,14-.06,27.95,0,41.93,0,4.58,1.51,6.13,6,6.3,4.91.2,9.82.26,14.73.13,5.24-.13,6.89-1.81,7-7.12C173.52,55.7,173.42,48.71,173.42,41.73Z">
      </path>
    </symbol>`
  },

  'sun-icon': {
    viewBox: '0 0 24 24',
    content: `<symbol id="sun-icon" viewBox="0 0 24 24">
      <path d="M6.05 4.14l-.39-.39a.993.993 0 0 0-1.4 0l-.01.01a.984.984 0 0 0 0 1.4l.39.39c.39.39 1.01.39 1.4 0l.01-.01a.984.984 0 0 0 0-1.4zM3.01 10.5H1.99c-.55 0-.99.44-.99.99v.01c0 .55.44.99.99.99H3c.56.01 1-.43 1-.98v-.01c0-.56-.44-1-.99-1zm9-9.95H12c-.56 0-1 .44-1 .99v.96c0 .55.44.99.99.99H12c.56.01 1-.43 1-.98v-.97c0-.55-.44-.99-.99-.99zm7.74 3.21c-.39-.39-1.02-.39-1.41-.01l-.39.39a.984.984 0 0 0 0 1.4l.01.01c.39.39 1.02.39 1.4 0l.39-.39a.984.984 0 0 0 0-1.4zm-1.81 15.1l.39.39a.996.996 0 1 0 1.41-1.41l-.39-.39a.993.993 0 0 0-1.4 0c-.4.4-.4 1.02-.01 1.41zM20 11.49v.01c0 .55.44.99.99.99H22c.55 0 .99-.44.99-.99v-.01c0-.55-.44-.99-.99-.99h-1.01c-.55 0-.99.44-.99.99zM12 5.5c-3.31 0-6 2.69-6 6s2.69 6 6 6s6-2.69 6-6s-2.69-6-6-6zm-.01 16.95H12c.55 0 .99-.44.99-.99v-.96c0-.55-.44-.99-.99-.99h-.01c-.55 0-.99.44-.99.99v.96c0 .55.44.99.99.99zm-7.74-3.21c.39.39 1.02.39 1.41 0l.39-.39a.993.993 0 0 0 0-1.4l-.01-.01a.996.996 0 0 0-1.41 0l-.39.39c-.38.4-.38 1.02.01 1.41z" fill="currentColor"></path>
    </symbol>`
  },

  'moon-icon': {
    viewBox: '0 0 24 24',
    content: `<symbol id="moon-icon" viewBox="0 0 24 24">
      <path d="M11.01 3.05C6.51 3.54 3 7.36 3 12a9 9 0 0 0 9 9c4.63 0 8.45-3.5 8.95-8c.09-.79-.78-1.42-1.54-.95A5.403 5.403 0 0 1 11.1 7.5c0-1.06.31-2.06.84-2.89c.45-.67-.04-1.63-.93-1.56z" fill="currentColor"></path>
    </symbol>`
  },

  'thermo-icon': {
    viewBox: '0 0 256 256',
    content: `<symbol id="thermo-icon" viewBox="0 0 256 256">
      <path fill="currentColor" d="M128,256A66.28,66.28,0,0,1,86.2,138.29V41.56A41.61,41.61,0,0,1,127.76,0h.48A41.61,41.61,0,0,1,169.8,41.56v96.73A66.28,66.28,0,0,1,128,256Zm-.24-238.9a24.49,24.49,0,0,0-24.45,24.46v101a8.57,8.57,0,0,1-3.62,7,49.18,49.18,0,1,0,56.63,0,8.55,8.55,0,0,1-3.62-7v-101A24.49,24.49,0,0,0,128.24,17.1Z"></path>
      <path fill="currentColor" d="M128,211.58a22.29,22.29,0,1,0-22.29-22.29A22.29,22.29,0,0,0,128,211.58Z"></path>
      <path fill="currentColor" d="M128,224.8a35.51,35.51,0,1,1,35.51-35.51A35.54,35.54,0,0,1,128,224.8Zm0-44.57a9.07,9.07,0,1,0,9.07,9.07A9.08,9.08,0,0,0,128,180.23Z"></path>
      <path fill="currentColor" d="M135.52,177.12a7.52,7.52,0,0,1-15,0V118.86a7.52,7.52,0,0,1,15,0Z"></path>
      <path fill="currentColor" d="M128,188.52a11.41,11.41,0,0,1-11.4-11.4V118.86a11.4,11.4,0,1,1,22.8,0v58.26A11.41,11.41,0,0,1,128,188.52Zm0-73.29a3.64,3.64,0,0,0-3.63,3.63v58.26a3.63,3.63,0,0,0,7.26,0V118.86A3.64,3.64,0,0,0,128,115.23Z"></path>
      <path fill="currentColor" d="M111,94.93H94.75a8.56,8.56,0,0,1,0-17.11H111a8.56,8.56,0,0,1,0,17.11Z"></path>
      <path fill="currentColor" d="M111,58.93H94.75a8.56,8.56,0,0,1,0-17.11H111a8.56,8.56,0,0,1,0,17.11Z"></path>
    </symbol>`
  },

  'palette-icon': {
    viewBox: '0 0 256 256',
    content: `<symbol id="palette-icon" viewBox="0 0 256 256">
      <g transform="matrix(0.31212232,0,0,0.31212232,-31.806642,-31.808307)">
        <g>
          <path
            style="fill: #f4ce8c; stroke: #5a2714; stroke-linecap: round; stroke-linejoin: round; stroke-width: 10px;"
            d="M896.33,406.6C840.66,235.27,621.7,152.86,407.26,222.53s-343.15,265-287.48,436.38a268.49,268.49,0,0,0,61.51,102.52,8.69,8.69,0,0,0,13.79-1.68c10.55-18,25.75-35.62,44.91-50.77,55.75-44.07,123.92-50.74,152.25-14.9s6.1,100.62-49.65,144.7l-.14.11a8.71,8.71,0,0,0,3.19,15.3c79.94,20.55,172,18.43,263.21-11.21C823.29,773.31,952,577.93,896.33,406.6ZM478.18,648.44c-45.68,0-82.72-27.33-82.72-61s37-61,82.72-61,82.73,27.32,82.73,61S523.87,648.44,478.18,648.44Z">
          </path>
          <path fill="url(#palette-gradient)"
            style="stroke: #5a2714; stroke-linecap: round; stroke-linejoin: round; stroke-width: 10px;"
            d="M904.22,365.08C848.55,193.75,629.59,111.34,415.15,181S72,446.06,127.67,617.39a268.49,268.49,0,0,0,61.51,102.52A8.69,8.69,0,0,0,203,718.23c10.55-18,25.75-35.62,44.91-50.77,55.75-44.07,123.92-50.74,152.25-14.9s6.1,100.62-49.65,144.7l-.14.11a8.71,8.71,0,0,0,3.19,15.3c79.94,20.55,172,18.43,263.21-11.21C831.18,731.79,959.89,536.41,904.22,365.08ZM486.07,606.92c-45.68,0-82.72-27.33-82.72-61s37-61,82.72-61,82.73,27.32,82.73,61S531.76,606.92,486.07,606.92Z">
          </path>
          <circle
            style="fill: #ed7373; stroke: #5a2714; stroke-linecap: round; stroke-linejoin: round; stroke-width: 10px;"
            cx="233.08" cy="507.35" r="68.94"></circle>
          <ellipse
            style="fill: #5dc5f0; stroke: #5a2714; stroke-linecap: round; stroke-linejoin: round; stroke-width: 10px;"
            rx="89.23" cx="442.56" ry="68.94" cy="356.33"></ellipse>
          <ellipse
            style="fill: #5dc5f0; stroke: #5a2714; stroke-linecap: round; stroke-linejoin: round; stroke-width: 10px;"
            rx="72.38" cx="738.22" ry="55.92" cy="594.29"></ellipse>
          <ellipse
            style="fill: #5dc5f0; stroke: #5a2714; stroke-linecap: round; stroke-linejoin: round; stroke-width: 10px;"
            rx="42.51" cx="650.14" ry="32.84" cy="319.26"></ellipse>
          <path
            style="fill: #ed7373; stroke: #5a2714; stroke-linecap: round; stroke-linejoin: round; stroke-width: 10px;"
            d="M786.12,438.39c0,.31,0,.61,0,.91a41.38,41.38,0,0,1-82.75-.89,41.09,41.09,0,0,1,3.17-15.9,86.72,86.72,0,0,0,5.77-43,53,53,0,0,1-.33-5.94,54.22,54.22,0,1,1,85,44.51A24.79,24.79,0,0,0,786.12,438.39Z">
          </path>
        </g>
      </g>
    </symbol>`
  },

  'stop-icon': {
    viewBox: '0 0 256 256',
    content: `<symbol id="stop-icon" viewBox="0 0 128 128">
      <path  fill="currentColor" d="M64.084 128C28.3512 128 0 99.481 0 64.755C0 28.8545 28.3512 0 64.084 0C99.8165 0 128 28.8545 128 64.755C128 99.481 99.8165 128 64.084 128ZM64.084 12.2464C35.9005 12.2464 12.0787 36.236 12.0787 64.755C12.0787 93.6095 35.9005 116.09 64.084 116.09C92.2675 116.09 116.09 93.6095 116.09 64.755C116.09 36.236 92.2675 12.2464 64.084 12.2464ZM80.524 85.8925C58.604 85.8925 47.6437 85.8925 47.6437 85.8925C44.6239 85.8925 41.7719 84.383 41.7719 79.8535C41.7719 58.9395 41.7719 48.4826 41.7719 48.4826C41.7719 45.4627 44.6239 42.2754 47.6437 42.2754C69.564 42.2754 80.524 42.2754 80.524 42.2754C83.376 42.2754 86.396 45.4627 86.396 48.4826C86.396 69.3965 86.396 79.8535 86.396 79.8535C86.396 84.383 83.376 85.8925 80.524 85.8925Z" fill-rule="evenodd" />
    </symbol>`
  }
};

// 已经加载的图标集合
const loadedIcons = new Set();

/**
 * 创建全局SVG图标定义容器
 * 只创建容器，不加载具体图标
 */
function createGlobalSvgDefs() {
  // 检查是否已创建过全局SVG
  if (document.getElementById('global-svg-icons')) {
    return;
  }

  // 创建隐藏的SVG容器，用于存放所有图标定义
  const svgContainer = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svgContainer.id = 'global-svg-icons';
  svgContainer.style.position = 'absolute';
  svgContainer.style.width = '0';
  svgContainer.style.height = '0';
  svgContainer.style.overflow = 'hidden';
  svgContainer.style.display = 'none';

  // 添加渐变定义
  const defsContent = `
    <defs>
      <!-- 调色板图标的渐变定义 -->
      <linearGradient id="palette-gradient" gradientUnits="userSpaceOnUse" x1="114.7" x2="917.19" y1="491.24" y2="491.24">
        <stop offset="0" stop-color="#fff"/>
        <stop offset="1" stop-color="#fff" stop-opacity="0"/>
      </linearGradient>
    </defs>
  `;

  svgContainer.innerHTML = defsContent;

  // 将SVG容器添加到文档中
  document.body.appendChild(svgContainer);
}

/**
 * 动态添加特定图标到全局定义中
 * @param {string} iconId - 图标的ID
 */
function addIconToGlobalDefs(iconId) {
  // 如果图标已经加载过，直接返回
  if (loadedIcons.has(iconId)) {
    return;
  }

  // 确保全局SVG容器已创建
  createGlobalSvgDefs();

  // 获取图标定义
  const iconDef = iconDefinitions[iconId];
  if (!iconDef) {
    console.warn(`图标 ${iconId} 未找到定义`);
    return;
  }

  // 获取SVG容器
  const svgContainer = document.getElementById('global-svg-icons');

  // 创建临时容器来解析图标内容
  const tempContainer = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  tempContainer.innerHTML = iconDef.content;

  // 将图标添加到SVG容器
  const symbolElement = tempContainer.firstElementChild;
  svgContainer.appendChild(symbolElement);

  // 标记为已加载
  loadedIcons.add(iconId);
}

/**
 * 创建图标组件的通用函数
 * @param {string} name - 图标的名称
 * @param {string} viewBox - viewBox属性值
 * @returns {Object} Vue组件
 */
function createIconComponent(name, viewBox) {
  return markRaw(defineComponent({
    name: name.charAt(0).toUpperCase() + name.slice(1).replace(/-([a-z])/g, g => g[1].toUpperCase()),
    __name: name,
    setup() {
      // 只加载当前需要的图标
      if (typeof document !== 'undefined') {
        addIconToGlobalDefs(name);
      }
    },
    template: `<svg :viewBox="viewBox" fill="currentColor">
      <use :href="'#' + name"></use>
    </svg>`,
    data() {
      return {
        name,
        viewBox
      };
    }
  }));
}

/**
 * 自定义SVG图标库
 * 所有图标都以Vue组件形式导出，便于在项目中复用
 * 使用<use>标签引用全局SVG定义，提高性能和可维护性
 */
export const SvgIcons = {
  /**
   * 添加节点图标
   */
  AddNodeIcon: createIconComponent('add-node-icon', '0 0 32 32'),

  /**
   * 磁盘图标
   */
  DiskIcon: createIconComponent('disk-icon', '0 0 256 256'),

  /**
   * 太阳图标
   */
  SunIcon: createIconComponent('sun-icon', '0 0 24 24'),

  /**
   * 月亮图标
   */
  MoonIcon: createIconComponent('moon-icon', '0 0 24 24'),

  /**
   * 温度计图标
   */
  ThermoIcon: createIconComponent('thermo-icon', '0 0 256 256'),

  /**
   * 调色板图标(彩色)
   */
  PaletteIcon: createIconComponent('palette-icon', '0 0 256 256'),

  /**
   * 停止图标
   */
  StopIcon: createIconComponent('stop-icon', '0 0 256 256')
};

export default SvgIcons;

// 将SvgIcons挂载到全局window对象上，以便在非模块脚本中访问
if (typeof window !== 'undefined') {
  window.SvgIcons = SvgIcons;
}

// 按需加载机制，不再在文档加载时自动创建所有图标定义
// 图标会在组件首次使用时通过addIconToGlobalDefs动态添加