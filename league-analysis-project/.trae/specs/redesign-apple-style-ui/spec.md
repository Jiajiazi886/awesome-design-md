# 界面重构 (Apple 现代化设计风格) Spec

## 为什么 (Why)
用户反馈当前的“暗黑武侠风”设计不符合期望，审美过时。系统需要采用 Apple 设计风格或现代化顶级公司的设计风格（如类似 Awesome 级的高质感极简设计），通过使用大圆角、细腻的阴影、明亮的背景层级、通透的毛玻璃效果（Backdrop Blur）、清新的强调色以及优良的排版层级，来提供高品质的生产级前端界面。

## 变更内容 (What Changes)
- 移除所有现有的暗黑系配色方案（如 `#141413`、`#1c1c1a`、`#2a2a28` 等深灰色和暗红色强调色）。
- 重置全局字体栈为现代化、干净的无衬线字体（如 `-apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", sans-serif`）。
- 引入符合 Web Design Guidelines 的明亮主题配色：白底、浅灰背景层级、精致的高对比文字以及生动清新的强调色（如 Apple Blue、Green 等）。
- 优化空间结构，引入更大的留白、卡片化布局（Card-based layout）、平滑的过渡动画与细腻的悬浮/焦点（Hover/Focus）反馈。
- **BREAKING**: 原有针对深色模式配置的 ECharts 选项需全部替换为适配浅色卡片的现代化、极简数据可视化配色（移除厚重的坐标轴和网格线，改用淡灰虚线与高饱和度的数据线）。

## 影响范围 (Impact)
- 影响的规范：前端设计规范、全局 CSS 变量。
- 影响的代码：
  - `src/style.css` (全局样式与 Element Plus 覆盖)
  - `src/App.vue` (整体布局、导航菜单)
  - `src/pages/*.vue` (所有页面的 UI 组件结构与样式类)

## 新增需求 (ADDED Requirements)
### Requirement: 现代化明亮主题 UI
系统必须提供一套拥有极致细节、视觉层级清晰的明亮风格界面。

#### Scenario: 浏览与交互体验
- **WHEN** 用户在各页面间导航并与卡片、列表、拖拽排表交互时
- **THEN** 界面应呈现清爽的白底或浅灰底、轻量级的阴影（Drop Shadow）、毛玻璃质感的顶栏/侧栏，同时交互元素（如拖拽块、按钮）应具有灵敏的平滑动画与明确的焦点反馈。
