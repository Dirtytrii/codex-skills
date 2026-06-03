# 公开发布检查清单

提交或推送前确认：

- [ ] `SKILL.md` frontmatter 有 `name` 和 `description`。
- [ ] 目录名和 `name` 一致。
- [ ] 不包含真实 token、密钥、账号密码、cookie、session、私钥。
- [ ] 不包含生产凭据、内网 IP、私有日志、客户数据、真实个人信息。
- [ ] 不包含本机绝对路径，除非它是示例且不会泄露隐私。
- [ ] 不包含 `.backup-*`、临时文件、生成缓存、录屏、记忆文件。
- [ ] 第三方来源保留 LICENSE、README 或 provenance。
- [ ] 外部 GitHub 来源已在 `registry/skills.json` 标注 `origin_type=external-github`。
- [ ] 已记录 `consumed_by_roles`，说明哪些角色会默认调用该 skill。
- [ ] `python3 scripts/validate_public_skills.py` 通过。
- [ ] README 或 `registry/skills.json` 已更新。

安全类 skill 额外确认：

- [ ] 明确授权边界。
- [ ] 默认低影响或只读。
- [ ] 禁止 DDoS、撞库、真实密码猜测、未授权破坏性写入。
- [ ] 报告输出要求脱敏。
