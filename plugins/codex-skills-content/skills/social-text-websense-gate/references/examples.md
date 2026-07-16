# Social Text Websense Examples

These examples are style patterns, not fixed phrases. Do not copy them blindly. Use them to learn how the absurd point is identified and grounded in a real technical behavior.

## AI coding / Agent over-freedom

Weak:

```text
AI Agent 需要更好的边界管理。
```

Better:

```text
AI 不是不聪明。是太自由。
自由到你让它修一个按钮，它把半个项目翻新，然后告诉你这是遵循一致性设计。
```

Why it works:

- The technical issue is scope control.
- The human scene is a junior worker over-helping.
- The joke is grounded by a plausible engineering excuse.

## Prompt fatigue → Skill

Weak:

```text
Prompt 不够可复用，所以需要沉淀为 Skill。
```

Better:

```text
搬 prompt 搬到第三个月会有点绷不住。
以前到处搬史喂群友，现在到处搜 prompt 喂 AI。
最抽象的是不给它喂还不行，不然每次开新会话都要重新解释一遍人类社会的基本秩序。
```

Why it works:

- It starts from a repeatable fatigue, not an abstract concept.
- It keeps the technical point: repeated context and boundaries.
- It translates prompt reuse into a social scene: feeding and onboarding.

## Non-CS / AI product building

Weak:

```text
非科班用 AI 做项目需要注意部署和工程化问题。
```

Better:

```text
非科班用 AI 做项目，最危险的不是它不会写。
是它真的写出来了。
页面能打开，按钮能点，你会短暂地产生一种“我是不是会做产品了”的幻觉。
然后一部署，环境变量、鉴权、数据库、支付回调、CORS、日志、异常兜底，全从地板缝里爬出来。
```

Why it works:

- It respects the real engineering boundary.
- It names the emotional trap: local demo confidence.
- It makes invisible infrastructure feel physical.

## Repo promotion

Weak:

```text
这是一个开源的角色化 Agent 工作流仓库，欢迎 star。
```

Better:

```text
我把“别动线上”“改前先确认范围”“校验不过就关掉”这些破事写成 skill 给 Codex 自己读。
不是为了显得高级，是不想每次都当 AI 的入职培训讲师。
有用就 star，没用就拿你的大 Codex 来抽打我的小 skill。
```

Why it works:

- It shows what the repo actually controls.
- It keeps the CTA builder-like, not corporate.
- It turns star/fork into stress testing, not begging.

## Anti-pattern: internet-word stuffing

Bad:

```text
这个 Agent 疑似有点抽象，绷不住了，太离谱了家人们。
```

Fix:

```text
它不是抽象。它是你让它解释报错，它不解释，开始讲这个技术选型的历史沿革。
```

The fix removes generic internet words and replaces them with a concrete situation.
