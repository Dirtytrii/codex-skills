# Adapter: whisper（视频/音频转录）

被 `/cheat-learn-from` 在 Way b（用户提供视频文件，让工具转录）时调用。

> **优先 Way a**（用户直接粘 script 文本——简单 + 准确）。Way b（whisper）只在用户**找不到 script 只有视频**时用。

---

## 这个 adapter 是干嘛的

把 mp4 / mov / mp3 等媒体文件转成文字 transcript，让 Claude 能读对标账号的稿子。

抖音 / B站 / YouTube 大多数视频**没有官方字幕**——拿稿子绕不开 ASR（语音转录）。这是为什么本 adapter 存在。

---

## 安装（一次性）

### 选项 A：whisper-cpp（**推荐**——快、轻、纯 C++）

Mac M 系列芯片上一条 3 分钟视频转录 30-60 秒。

```bash
# 1. 装 whisper-cpp
brew install whisper-cpp

# 2. 装 ffmpeg（whisper-cpp 依赖，从视频里抽音频）
brew install ffmpeg

# 3. 下载模型（中文推荐 medium 或 large-v3，准确度够 + 速度还行）
# whisper-cpp 第一次运行会自动下载，或手动：
mkdir -p ~/.whisper-cpp/models
cd ~/.whisper-cpp/models
# medium 模型 (~1.5GB)
curl -L -O https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-medium.bin
```

### 选项 B：openai-whisper（Python 版，更慢但有 API 兼容性）

```bash
pip install openai-whisper
brew install ffmpeg

# 模型自动下载
```

### 选项 C：用云端 API（不需要本地模型）

`/cheat-learn-from` 暂不直接支持云端 API——如果你有 OpenAI / Azure / 阿里云的 ASR API key，可以自己改 `run.sh` 走云端。

---

## 用法

cheat-learn-from 自动调用，你不需要手动跑。但如果想手动测试：

```bash
# 转录单个视频
bash run.sh <video_path> <output_dir>

# 例：
bash run.sh ~/Desktop/对标账号/某视频.mp4 ~/my-channel/samples/对标账号/abc123/
# → 输出 ~/my-channel/samples/对标账号/abc123/transcript.md
```

## 输出格式

`transcript.md`：

```markdown
# Transcript: <video filename>

**Source**: <video file path>
**Transcribed at**: <ISO timestamp>
**Engine**: whisper-cpp medium / openai-whisper large / etc.
**Duration**: <video length>

---

[纯文本转录，按段落分（不是字幕格式）]
```

> 注意 whisper 输出的字幕是按 **句子** 分行的（每句换行 + 时间戳）。
> run.sh 会去掉时间戳 + 把短句合并成段落，让 Claude 读起来像稿子，不是字幕表。

## 失败模式

| 症状 | 原因 | 处理 |
|---|---|---|
| `whisper-cpp: command not found` | 没装 | 跑 `brew install whisper-cpp` |
| `ffmpeg: command not found` | 没装 ffmpeg | 跑 `brew install ffmpeg` |
| 转录乱码 / 大量错字 | 视频是英文但用了中文模型，反之亦然 | 改 `run.sh` 里 `--language` 参数 |
| 转录慢（>10 分钟） | 用了 large 模型 + 没有 GPU/M-chip 加速 | 换 medium 模型 |
| Disk full | 模型文件大（large-v3 ~3GB） | 用 medium（~1.5GB）够用 |

## 稳定性等级

★★★★ — whisper 是开源标准 ASR，不会突然失效。模型更新自由，pin 版本无虞。

## 风险提示

- **TOS**：你转录**自己下载的对标账号视频**用于个人学习参考是合理使用；**不要**把转录结果再发布
- **隐私**：whisper 全部本地运行，不传任何数据到云端

## 文件清单

```
adapters/script-extraction/whisper/
├── README.md           # 本文件
└── run.sh              # cheat-learn-from 调用的 wrapper
```

## 与其他 adapter 的关系

- 同 `adapters/perf-data/douyin-session/`、`adapters/trend-sources/*` 一样，是 cheat-on-content 的可选 adapter
- 只在 `/cheat-learn-from --way b` 时调用——Way a（粘文本）不需要

## 用户自己下载视频的说明

工具**不直接抓视频**——避免 TOS 风险 + 反爬维护成本。建议用：

- **抖音**：第三方下载器 / 抖音 PC 版 → 复制视频链接 → 粘进下载器
- **B站**：[BBDown](https://github.com/nilaoda/BBDown) / [you-get](https://github.com/soimort/you-get)
- **YouTube**：[yt-dlp](https://github.com/yt-dlp/yt-dlp)（最强大）
- **小红书**：[xhs-downloader](https://github.com/JoeanAmier/XHS-Downloader)

下载后扔到 `samples/<benchmark-name>/<video-id>/source.mp4` 即可——cheat-learn-from 会自动找到。
