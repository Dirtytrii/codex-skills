# 多页图文视觉一致性协议

这个协议用于解决多页小红书图文生成时常见的两个问题：比例不一致、版式不统一。

## 强制原则

- 多页图文必须先建立统一视觉母版，再生成 1 张视觉确认图；用户确认后再生成整套最终图片。
- 统一母版不是总说明，而是每一页提示词都必须重复的硬约束。
- 提示词是图片生成记录，不是最终交付物；用户要图文时必须交付图片文件。
- 页面可以有节奏变化，但不能改变画布比例、边距、字体系统、页码位置、主色和组件语言。
- 图像模型容易忽略“默认 3:4”，所以每条提示词都要写 `1080x1440px, strict 3:4 vertical portrait canvas`。
- 负面提示词必须明确禁止：square、landscape、different template、inconsistent margins、random layout shift。

## 统一视觉母版字段

```text
画布：1080x1440px, strict 3:4 vertical portrait canvas, no square, no landscape.
安全边距：左右 72px，上下 80px；任何文字、页码、核心图形不得越界。
网格：12 列网格，8px spacing system，所有卡片和节点对齐网格。
标题区：固定在顶部 18%-32% 区域，封面可占 35%-45%，内页不超过 30%。
正文区：每页正文最多 2-4 行，说明文字最多 3 个短模块。
页码 / 角标：统一放在右下角或左下角，尺寸小，不抢标题。
色彩令牌：背景色、主文字、辅助文字、强调色固定；强调色只用于关键词、连线、编号或状态标签。
字体令牌：中文标题粗黑体，正文中等字重无衬线，英文注释 Inter / SF Pro 风格。
组件语言：统一卡片圆角、线条粗细、箭头样式、标签样式、图标风格。
节奏规则：每页只能改变主视觉和信息结构，不改变母版系统。
```

## 母版锁定前缀

每一页图像生成提示词开头都要复制下面这段，再追加本页内容。确认图和最终图都必须使用同一段前缀：

```text
Series visual master lock: create one page of the same Xiaohongshu carousel series, 1080x1440px, strict 3:4 vertical portrait canvas, no square, no landscape, no crop, no extra border. Keep identical canvas ratio, identical safe margins, identical typography system, identical page-number position, identical color tokens, identical card radius, identical line weight, and identical icon style across all pages. Use a 12-column grid and 8px spacing system. Keep text-safe zones clean and high contrast. This page belongs to the same visual series as the other pages; only the main visual and information structure may change.
```

## 单页提示词结构

```text
[母版锁定前缀]

Page [页码] / [页面任务]
主题：[主题]
本页标题占位：[标题]
本页信息结构：[对比 / 流程 / 架构 / 清单 / 案例 / 总结]
沿用元素：[背景、色彩、角标、网格、字体、卡片、线条]
本页变化：[只写本页独有主视觉和信息结构]
构图：[标题区、主视觉区、正文区、页码区]
文字区域：[明确安全区和最大行数]
色彩：[固定令牌 + 本页强调色使用位置]
质感：[统一材质语言]
禁止：[比例和一致性负面提示词]
```

## 系列一致性自检

- [ ] 是否先生成了 1 张视觉确认图。
- [ ] 用户是否确认视觉方向。
- [ ] 是否已经生成最终图片文件，而不是只输出提示词。
- [ ] 每条提示词都写了 `1080x1440px`。
- [ ] 每条提示词都写了 `strict 3:4 vertical portrait`。
- [ ] 每条提示词都禁止 square 和 landscape。
- [ ] 每条提示词都复制了同一段母版锁定前缀。
- [ ] 每页边距、页码、角标位置一致。
- [ ] 每页字体系统一致。
- [ ] 每页背景和色彩令牌一致。
- [ ] 每页卡片圆角、线条粗细、图标风格一致。
- [ ] 页面之间只有主视觉和信息结构变化。
- [ ] 没有某一页突然像另一个模板。

