# 新增 Skill 流程

## 1. 放置目录

将完整 skill 目录放到：

```text
skills/<skill-name>/
```

目录名必须和 `SKILL.md` frontmatter 的 `name` 一致。

## 2. 必备文件

每个 skill 至少需要：

```text
skills/<skill-name>/SKILL.md
```

推荐但非必须：

```text
skills/<skill-name>/agents/openai.yaml
skills/<skill-name>/references/
skills/<skill-name>/scripts/
skills/<skill-name>/assets/
```

## 3. 更新清单

在 `registry/skills.json` 添加条目：

```json
{
  "name": "example-skill",
  "path": "skills/example-skill",
  "status": "active",
  "origin_type": "local|external-github|hermes",
  "upstream_url": null,
  "maintenance": "local-owned|vendored-upstream|vendored-adapted|hermes-owned",
  "consumed_by_roles": ["架构"],
  "summary": "一句话说明用途"
}
```

来源字段说明见 `docs/source-policy.md`。

## 4. 公开前检查

运行：

```bash
python3 scripts/validate_public_skills.py
```

再按 `docs/publication-checklist.md` 检查敏感信息和许可证。

## 5. 提交

提交信息用中文，说明新增了什么 skill、来源是什么、跑过什么校验。
