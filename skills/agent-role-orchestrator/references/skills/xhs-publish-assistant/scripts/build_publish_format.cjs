#!/usr/bin/env node
const fs = require("fs");
const path = require("path");

const arg = process.argv[2];

if (!arg || arg === "-h" || arg === "--help") {
  console.error('Usage: node build_publish_format.cjs "<article-or-reedit-directory>"');
  process.exit(arg ? 0 : 1);
}

const targetDir = path.resolve(arg);

function exists(filePath) {
  try {
    return fs.existsSync(filePath);
  } catch (_) {
    return false;
  }
}

function readUtf8(filePath) {
  return fs.readFileSync(filePath, "utf8");
}

function normalizeLine(line) {
  return line.replace(/\r/g, "").trim();
}

function stripFence(text) {
  const trimmed = text.trim();
  const match = trimmed.match(/^```(?:text|markdown|md)?\s*\n([\s\S]*?)\n```$/i);
  return (match ? match[1] : trimmed).trim();
}

function section(markdown, headingPatterns) {
  const lines = markdown.replace(/\r/g, "").split("\n");
  for (let i = 0; i < lines.length; i += 1) {
    const line = normalizeLine(lines[i]);
    if (!/^#{2,4}\s+/.test(line)) continue;
    const title = line.replace(/^#{2,4}\s+/, "").trim();
    if (!headingPatterns.some((pattern) => pattern.test(title))) continue;

    const body = [];
    for (let j = i + 1; j < lines.length; j += 1) {
      if (/^#{2,4}\s+/.test(normalizeLine(lines[j]))) break;
      body.push(lines[j]);
    }
    return stripFence(body.join("\n"));
  }
  return "";
}

function firstMeaningfulLine(text) {
  for (const raw of text.split("\n")) {
    const line = normalizeLine(raw);
    if (!line) continue;
    if (/^(首推|推荐|首选标题|备选标题)[:：]$/.test(line)) continue;
    if (/^[-*]\s*/.test(line)) return line.replace(/^[-*]\s*/, "").trim();
    if (/^>\s*/.test(line)) return line.replace(/^>\s*/, "").trim();
    if (!line.startsWith("```")) return line;
  }
  return "";
}

function visibleLength(text) {
  return Array.from(text || "").length;
}

function normalizeTags(text) {
  const tags = [];
  const seen = new Set();
  const matches = text.match(/#[\p{Script=Han}A-Za-z0-9_]+/gu) || [];
  for (const tag of matches) {
    if (!seen.has(tag)) {
      seen.add(tag);
      tags.push(tag);
    }
  }
  return tags;
}

function findSource(dir) {
  const reeditNote = path.join(dir, "reedit-note.md");
  if (exists(reeditNote)) return { file: reeditNote, reeditDir: dir, articleDir: path.dirname(dir), isReedit: true };

  const contentPack = path.join(dir, "content-pack.md");
  if (exists(contentPack)) return { file: contentPack, reeditDir: null, articleDir: dir, isReedit: false };

  const reeditDirs = exists(dir)
    ? fs.readdirSync(dir, { withFileTypes: true })
      .filter((entry) => entry.isDirectory() && /^reedit-\d{4}-\d{2}-\d{2}$/.test(entry.name))
      .map((entry) => entry.name)
      .sort()
    : [];
  if (reeditDirs.length) {
    const latest = path.join(dir, reeditDirs[reeditDirs.length - 1]);
    const latestNote = path.join(latest, "reedit-note.md");
    if (exists(latestNote)) return { file: latestNote, reeditDir: latest, articleDir: dir, isReedit: true };
  }

  throw new Error(`No content-pack.md or reedit-note.md found under ${dir}`);
}

function pngSize(filePath) {
  const buffer = fs.readFileSync(filePath);
  if (buffer.length < 24) return null;
  const signature = buffer.subarray(0, 8).toString("hex");
  if (signature !== "89504e470d0a1a0a") return null;
  return {
    width: buffer.readUInt32BE(16),
    height: buffer.readUInt32BE(20),
  };
}

function inspectImages(outputDir) {
  if (!exists(outputDir)) {
    return { count: 0, status: "未找到 output 目录", details: [] };
  }
  const files = fs.readdirSync(outputDir)
    .filter((name) => /^xhs-.*\.png$/i.test(name))
    .sort();

  const details = files.map((name) => {
    const size = pngSize(path.join(outputDir, name));
    return { name, size };
  });

  if (!details.length) return { count: 0, status: "未找到 xhs-*.png", details };
  const allExpected = details.every((item) => item.size?.width === 1080 && item.size?.height === 1440);
  const uniqueSizes = [...new Set(details.map((item) => item.size ? `${item.size.width}x${item.size.height}` : "unknown"))];
  return {
    count: details.length,
    status: allExpected ? "全部 1080x1440" : `尺寸不一致：${uniqueSizes.join(", ")}`,
    details,
  };
}

function findAccount(markdown, articleDir) {
  const accountMatch = markdown.match(/(?:account|账号)[:：]\s*([A-Za-z0-9_-]+)/i);
  if (accountMatch) return accountMatch[1];

  let cursor = articleDir;
  for (let i = 0; i < 8; i += 1) {
    const accountsFile = path.join(cursor, "content", "xhs", "accounts.md");
    if (exists(accountsFile)) {
      const text = readUtf8(accountsFile);
      const current = text.match(/^###\s+(.+)$/m);
      if (current) return current[1].trim();
    }
    const parent = path.dirname(cursor);
    if (parent === cursor) break;
    cursor = parent;
  }
  return "待确认";
}

function outputDirFor(sourceInfo) {
  return path.join(sourceInfo.isReedit ? sourceInfo.reeditDir : sourceInfo.articleDir, "output") + path.sep;
}

function phaseBaseline(markdown) {
  const snapshot = markdown.match(/pre_edit_data[:：]\s*(.+)/i)?.[1]
    || markdown.match(/编辑前基线[:：]\s*(.+)/)?.[1]
    || "";
  if (snapshot.trim()) return snapshot.trim();

  const fields = [
    ["观看", markdown.match(/^-\s*views[:：]\s*(.+)$/im)?.[1]],
    ["评论", markdown.match(/^-\s*comments[:：]\s*(.+)$/im)?.[1]],
    ["点赞", markdown.match(/^-\s*likes[:：]\s*(.+)$/im)?.[1]],
    ["收藏", markdown.match(/^-\s*favorites[:：]\s*(.+)$/im)?.[1]],
    ["分享", markdown.match(/^-\s*shares[:：]\s*(.+)$/im)?.[1]],
  ].filter(([, value]) => value);

  return fields.map(([label, value]) => `${label} ${String(value).trim()}`).join("；");
}

const sourceInfo = findSource(targetDir);
const markdown = readUtf8(sourceInfo.file);
const outputDir = outputDirFor(sourceInfo);

const titleSection = section(markdown, [/^(建议|正式)?标题$/, /^标题建议$/, /^正式标题$/]);
const title = firstMeaningfulLine(titleSection)
  || firstMeaningfulLine(section(markdown, [/^标题池$/]))
  || "";

const body = section(markdown, [/^建议正文$/, /^发布正文$/, /^正文笔记/, /^正文$/]);
const tagsSection = section(markdown, [/^话题标签$/, /^标签$/, /^话题$/]);
const tags = normalizeTags(tagsSection || body);
const imageInfo = inspectImages(outputDir);
const account = findAccount(markdown, sourceInfo.articleDir);
const baseline = phaseBaseline(markdown);
const titleLength = visibleLength(title);

const titleJudgment = title
  ? titleLength <= 20
    ? `${titleLength}/20；需人工确认：是否覆盖人群 + 场景 + 系统识别关键词`
    : `${titleLength}/20；标题超长，需要压缩到 20 字以内`
  : "缺标题";
const coverJudgment = imageInfo.count
  ? "需人工确认：首图是否有情绪冲突 + 点击理由"
  : "缺配图";
const ready = title && titleLength <= 20 && body && tags.length <= 10 && imageInfo.count > 0 ? "可发布" : "需补齐";

const sections = [];
sections.push(`**标题**\n\`\`\`text\n${title || "（缺标题）"}\n\`\`\``);
sections.push(`**正文**\n\`\`\`text\n${body || "（缺正文）"}\n\`\`\``);
sections.push(`**标签**\n\`\`\`text\n${tags.length ? tags.join(" ") : "（缺标签）"}\n\`\`\``);
sections.push(`**配图目录**\n\`\`\`text\n${outputDir}\n\`\`\``);
sections.push(`**发布前检查**\n\`\`\`text\n账号：${account}\n图片数量：${imageInfo.count}\n图片尺寸：${imageInfo.status}\n标题长度：${titleLength} / 20\n标签数量：${tags.length} / 10\n文案去 AI 味：待确认（输出前应已运行 humanizer-zh）\n标题覆盖：${titleJudgment}\n封面职责：${coverJudgment}\n图片顺序：按 output 目录内 xhs-*.png 文件名顺序上传\n状态：${ready}\n\`\`\``);

if (sourceInfo.isReedit) {
  sections.push(`**二次编辑记录**\n\`\`\`text\n这是已发布笔记二次编辑。\n编辑前基线：${baseline || "待补"}\n编辑后请告诉我实际保存时间，我会登记为 reedit_phase。\n\`\`\``);
}

console.log(sections.join("\n\n"));
