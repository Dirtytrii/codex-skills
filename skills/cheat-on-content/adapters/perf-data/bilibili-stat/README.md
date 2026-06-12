# bilibili-stat — B站 perf-data adapter

回收**自己（或任意）B站视频**的播放数据 + 热门评论，供 `/cheat-retro` 复盘。

被 `/cheat-retro` 调用：当 `state.data_collection=adapter` 且 `Platform: bilibili` 时。

## 为什么它比抖音/小红书 adapter 简单

B站的视频统计（`view`）与评论（`reply`）都是**公开接口**：

- 不需要登录（没有 `crawler.py login` 步骤、不碰 `.auth/`）
- 不需要 wbi 签名（`view` 接口免签名；评论走 `x/v2/reply` 老接口，按热度 `sort=2`）
- 不需要浏览器（纯 `httpx`，无 playwright）

所以 **clone 下来装个 `httpx` 就能用**，零配置。

## 安装

```bash
pip install -r requirements.txt
```

（若你的内容项目根有 `.venv`，run.sh 会优先用它；否则用系统 `python3`/`python`。）

## 用法

`/cheat-retro` 会自动按下面的契约调用，一般你不用手动跑：

```bash
bash run.sh <bvid_or_url> <video_folder> [<script_path>]
```

- `<bvid_or_url>`：`BV1cUoUY9Ecr`，或任意含 BV 号的链接（如 `https://www.bilibili.com/video/BV1cUoUY9Ecr`）
- `<video_folder>`：输出目录，`report.md` 会写进这里
- `<script_path>`：可选，原始稿子，会并入 report.md 供复盘 diff

也可直接调底层：

```bash
python review.py video BV1cUoUY9Ecr           # 抓数据 → 写 videos/<auto>/report.md
python review.py login                        # B站无需登录，仅打印说明（接口一致性）
```

## 输出（report.md）

与 douyin-session 同格式，含：

- 视频元信息（标题 / UP主 / 发布时间 / 时长 / 链接）
- **播放数据**：播放、点赞、投币、收藏、分享、评论、弹幕，并附派生比率（赞播比 / 投币率 / 收藏率 / 分播比）——B站「三连率」尤其能反映硬核认可度
- 原始稿子（若提供）
- **热门评论**（按点赞降序，带 IP 属地）

## 接口

| 数据 | 接口 |
|---|---|
| 视频统计 | `GET https://api.bilibili.com/x/web-interface/view?bvid=<BV号>` |
| 评论 | `GET https://api.bilibili.com/x/v2/reply?type=1&oid=<aid>&sort=2&pn=&ps=20` |

`oid` 取自 view 接口返回的 `aid`。评论按热度（`sort=2`）翻页，默认取 top 50。

## 退出码

`0` 成功 · `2` 缺依赖（httpx 未装）· `3` 其他失败（网络 / 解析 / BV 号错误）。任何失败时 `/cheat-retro` 会优雅降级到 manual 模式。

## 字段随接口改版的维护

`view` 的 `stat` 字段名（view/like/coin/favorite/share/reply/danmaku）和评论的 `replies[].{like,content.message,member.uname,rcount,reply_control.location}` 都已按 2026-06 真实返回校准。若 B站改版导致某项为 0，对照 `crawler.py` 的 `fetch_video` / `_normalize_comment` 调整 key 即可。
