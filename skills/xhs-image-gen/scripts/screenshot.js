#!/usr/bin/env node
// 小红书卡片 HTML → PNG 批量截图脚本
// 用法: node screenshot.js xhs_card_*.html [--clean] [--output-dir <dir>]

const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

function parseArgs(argv) {
  const args = argv.slice(2);
  const files = [];
  let outputDir = null;
  let clean = false;

  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--output-dir" && args[i + 1]) {
      outputDir = args[++i];
    } else if (args[i] === "--clean") {
      clean = true;
    } else if (!args[i].startsWith("--")) {
      files.push(args[i]);
    }
  }

  return { files, outputDir, clean };
}

// 从 HTML 中解析 body 的 width/height（默认 1080x1440）
function parseViewportSize(html) {
  let width = 1080;
  let height = 1440;

  // 匹配 body { ... width: Npx; ... height: Npx; ... }
  const bodyMatch = html.match(/body\s*\{[^}]*\}/s);
  if (bodyMatch) {
    const body = bodyMatch[0];
    const wMatch = body.match(/width\s*:\s*(\d+)px/);
    const hMatch = body.match(/height\s*:\s*(\d+)px/);
    if (wMatch) width = parseInt(wMatch[1], 10);
    if (hMatch) height = parseInt(hMatch[1], 10);
  }

  return { width, height };
}

async function screenshotFile(browser, htmlPath, outputDir) {
  const absolutePath = path.resolve(htmlPath);
  const html = fs.readFileSync(absolutePath, "utf-8");
  const { width, height } = parseViewportSize(html);

  const baseName = path.basename(htmlPath, path.extname(htmlPath));
  const dir = outputDir || path.dirname(absolutePath);
  const pngPath = path.join(dir, `${baseName}.png`);

  const page = await browser.newPage();
  await page.setViewportSize({ width, height });
  await page.goto(`file://${absolutePath}`, { waitUntil: "networkidle" });
  await page.screenshot({ path: pngPath, fullPage: true });
  await page.close();

  return { htmlPath, pngPath, width, height };
}

async function main() {
  const { files, outputDir, clean } = parseArgs(process.argv);

  if (files.length === 0) {
    console.error("用法: node screenshot.js <html-files...> [--clean] [--output-dir <dir>]");
    process.exit(1);
  }

  // 验证所有文件存在
  for (const f of files) {
    if (!fs.existsSync(f)) {
      console.error(`文件不存在: ${f}`);
      process.exit(1);
    }
  }

  // 创建输出目录
  if (outputDir) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  console.log(`正在启动浏览器...`);
  const browser = await chromium.launch();

  console.log(`正在处理 ${files.length} 个文件...\n`);
  const results = await Promise.all(
    files.map((f) => screenshotFile(browser, f, outputDir))
  );

  await browser.close();

  // 输出结果摘要
  console.log("截图完成:\n");
  for (const r of results) {
    console.log(`  ${r.pngPath}  (${r.width}x${r.height})`);
  }

  // 清理 HTML 文件
  if (clean) {
    console.log("\n正在清理 HTML 文件...");
    for (const r of results) {
      fs.unlinkSync(path.resolve(r.htmlPath));
      console.log(`  已删除: ${r.htmlPath}`);
    }
  }

  console.log(`\n完成! 共生成 ${results.length} 张 PNG 图片。`);
}

main().catch((err) => {
  console.error("截图失败:", err.message);
  process.exit(1);
});
