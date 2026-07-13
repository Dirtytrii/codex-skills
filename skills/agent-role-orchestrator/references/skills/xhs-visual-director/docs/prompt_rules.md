# 图像生成提示词规则

## 提示词必须包含

- 画幅比例：默认 3:4 竖版；多页图文必须写成 `1080x1440px, strict 3:4 vertical portrait canvas`。
- 比例禁止项：每条提示词必须明确写 `no square, no landscape, no crop, no extra border`。
- 背景风格：深色、白底、玻璃、网格、商务、截图标注等。
- 主体布局：标题区、主视觉区、辅助信息区。
- 文字区域规划：标题放在哪里，正文放在哪里，留白多少。
- 字体风格：无衬线、粗黑体、Inter、SF Pro、HarmonyOS Sans 风格。
- 色彩方案：主色、辅色、强调色。
- 视觉元素：卡片、网格、箭头、数据、截图、产品、地图等。
- 质感：玻璃、磨砂、金属、纸感、屏幕光等。
- 留白：明确写出保留清晰阅读区。
- 禁止项：不要文字变形、不要小字、不要廉价渐变、不要复杂噪声。

## 多页图文一致性硬规则

生成 2 页以上图文时，先输出“统一视觉母版”，再输出逐页提示词。每一页提示词必须重复同一个母版锁定前缀。

母版锁定前缀：

```text
Series visual master lock: create one page of the same Xiaohongshu carousel series, 1080x1440px, strict 3:4 vertical portrait canvas, no square, no landscape, no crop, no extra border. Keep identical canvas ratio, identical safe margins, identical typography system, identical page-number position, identical color tokens, identical card radius, identical line weight, and identical icon style across all pages. Use a 12-column grid and 8px spacing system. Keep text-safe zones clean and high contrast. This page belongs to the same visual series as the other pages; only the main visual and information structure may change.
```

每页只允许变化：

- 页面任务。
- 主视觉。
- 信息结构。
- 情绪强度。
- 局部强调元素。

每页不允许变化：

- 画布比例。
- 安全边距。
- 标题区规则。
- 页码 / 角标位置。
- 字体系统。
- 主色、辅助色、强调色。
- 卡片圆角、线条粗细、图标风格。

## 推荐结构

```text
[复制统一母版锁定前缀]

生成一张 1080x1440px、strict 3:4 vertical portrait 的小红书图文页面。
主题：[主题]
页面任务：[封面 / 痛点 / 方法 / 案例 / 总结]
风格：[风格名称]
布局：[标题区 + 主视觉区 + 信息区]
文字区域：[标题位置、正文位置、安全留白]
配色：[主色、辅色、强调色]
字体：[中文 / 英文字体风格]
视觉元素：[具体元素]
质感：[材质和光影]
比例限制：no square, no landscape, no crop, no extra border
一致性限制：no inconsistent margins, no different template, no random layout shift
限制：[其他负面要求]
```

## 文字生成注意

多数图像模型生成中文不稳定。如果用户需要可编辑文字，提示词应要求：

- 保留清晰标题区域。
- 只生成背景、构图和可替换文字占位。
- 重要文字后期排版添加。

可写为：

```text
不要生成真实中文正文，只保留清晰文字占位区和版式结构，标题和正文由后期排版添加。
```

## 负面提示词通用版

```text
不要廉价蓝紫渐变，不要随机霓虹线条，不要文字变形，不要小字堆积，不要 PPT bullet 列表，不要塑料质感，不要儿童卡通，不要低清晰度，不要过度装饰，不要元素遮挡标题，不要页码喧宾夺主，不要方图，不要横图，不要改变画幅比例，不要改变安全边距，不要每页换模板，不要随机改变页码位置。
```
