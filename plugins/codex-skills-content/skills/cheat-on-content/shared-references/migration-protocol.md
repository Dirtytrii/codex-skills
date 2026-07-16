# Migration Protocol（schema 演进哲学）

被 `cheat-migrate` skill / `cheat-init` / SessionStart hook / 维护者引用。规定如何安全演进 `.cheat-state.json` schema 而不让老用户被打断。

---

## 核心原则

1. **每个 release 必须能让老用户的旧 state 工作**——通过 migrate 升级，或通过 `state.get(field, default)` 兼容
2. **MINOR 改动 = 加字段 / 软化 enum**；老 state 不跑 migrate 也能工作（字段缺失用默认值），跑了让 state 完整
3. **MAJOR 改动 = 删字段 / 重命名 / 改语义**；老 state **必须**跑 migrate，否则 skill 读到不一致字段会出错
4. **不允许跳版**；多版升级必须按顺序应用每个 step。每步幂等
5. **失败停在原地**；不回滚，让用户在断点修复后继续
6. **schema_version 是单调递增**；不允许降级（如需降级，cp 历史 git 快照）

---

## 何时算 MINOR vs MAJOR

### MINOR 范围（不需要 migrate 也能跑老 state）

- 新增字段（默认值定义良好，老 skill 不读它也不出错）
- 软化 enum 取值（如 `"strict" / "lenient"` 加第三个 `"adaptive"`，老值仍合法）
- 给字段加新可选取值（如某个 list 字段加新元素）
- 改默认值（不改语义）

### MAJOR 范围（必须跑 migrate）

- **删除字段**——老 skill 仍写它，新 skill 不读它，会出歧义
- **重命名字段**——老/新 skill 看不到对方写的
- **改字段语义**（如 `mode` 从 enum 改为整数；`baseline_plays` 从 int 改为 list）
- **改 enum 取值**（如 `"opinion-video"` 改成 `"opinion_video"`，老值不再合法）
- **拆字段 / 合字段**

> 模糊地带建议**保守判定为 MAJOR**——多写一份 migration 文件比让用户的 state 出错更好。

---

## 维护者 checklist：bump schema 时必做的 4 件事

每次准备 release 时如果改了 state schema：

### 1. 改 cheat-init 写新 state 的硬编码 schema_version

```diff
- "schema_version": "1.1",
+ "schema_version": "1.2",
```

位置：`skills/cheat-init/SKILL.md` Phase 3 的 state 写入段。

### 2. 改 migrations/registry.md 的 LATEST_SCHEMA 标记位

```diff
- LATEST_SCHEMA = "1.1"
+ LATEST_SCHEMA = "1.2"
```

并在"版本链"表追加新行：

```
| 1.1 | 1.2 | NO/YES | [1.1-to-1.2.md](1.1-to-1.2.md) | 一句话描述 |
```

### 3. 写 migrations/<old>-to-<new>.md

4 段必填（参考 `1.0-to-1.1.md` 模板）：
- WHAT changed
- WHY
- HOW (Claude steps for /cheat-migrate)
- Manual fallback

> 写不出 4 段 = 改动太复杂没想清楚 = 不该 release 这次 schema bump。

### 4. CHANGELOG.md 标版本号 + 链接

```markdown
## [0.2.0] — YYYY-MM-DD

### BREAKING / MINOR

- schema_version 1.1 → 1.2: <一句话描述>。迁移指南：[migrations/1.1-to-1.2.md](migrations/1.1-to-1.2.md)
- ...
```

MINOR 用 `### MINOR`，MAJOR 用 `### BREAKING`，要醒目。

---

## skill 内部怎么读 state（防御式编程）

每个 skill 读 state 时**必须**用 `state.get(field, default)` 模式：

```python
# 好
target_cadence = state.get("target_publish_cadence_days", None)
benchmark_status = state.get("benchmark_status", "none")
shoots = state.get("shoots", [])

# 坏（老 state 没这字段会 KeyError）
target_cadence = state["target_publish_cadence_days"]
```

理由：
- MINOR 升级时老 state 缺新字段——`get` 模式让 skill 自动用默认值
- 用户手改 state 删了字段——同上
- 减少 skill 内"必须先迁移才能跑"的强依赖

**例外**：核心标识字段允许直接索引（如 `state["schema_version"]`、`state["rubric_version"]`）——这些缺失意味着 state 文件根本不合法，应该明确报错。

---

## SessionStart hook 的角色

hook 在每次会话开始时检测：

```bash
state_schema=$(jq -r '.schema_version // "unknown"' "$STATE_FILE")
if [[ "$state_schema" != "$LATEST_SCHEMA" ]]; then
  echo "⚠️ schema 版本不一致：state=$state_schema, skill 期望=$LATEST_SCHEMA"
  echo "   建议跑 /cheat-migrate 升级（不阻塞继续工作）"
fi
```

**非阻塞**：用户可以选择"先继续工作，回头再跑 migrate"。MINOR 不一致时大部分功能仍能跑；MAJOR 时部分 skill 可能报错——这时再跑 migrate 也来得及。

---

## 给开发者：避免 schema 频繁 bump 的实践

不是每个改动都需要 schema bump。下面是哲学：

- **优先 MINOR**：能加字段就加字段，少删字段。删字段让老用户不爽
- **批量 bump**：积攒 3-5 个 MINOR 一起 release 比每次小改都 bump 要友好
- **延迟 bump**：MINOR 字段如果 90% 用户用不到，**不**急着 bump schema——可以让该字段 `state.get(field, default)` 默默 work，等下次 release 顺路 bump
- **避免 MAJOR**：能用 MINOR 解决的绝不上 MAJOR。例：与其重命名字段，不如保留旧字段 + 加新字段（旧的标 deprecated，下个 MAJOR release 才删）

---

## 备份保留策略

`/cheat-migrate` 写之前会备份到 `.cheat-state.json.backup-<timestamp>`。

备份保留多久：
- 用户跑 `/cheat-status` 时，如果有备份 + state 已稳定运行 N 天 → 提示"可以清理 N 个旧备份"
- `/cheat-init` 重 init 时清理所有旧备份（既然要重 init，老备份意义不大）
- 用户手动 `rm .cheat-state.json.backup-*` 永远 OK

不入版本控制：`.cheat-state.json.backup-*` 应在 `.gitignore` 里（已含 `.cheat-state.json` 通配规则）。
