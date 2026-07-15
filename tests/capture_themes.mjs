#!/usr/bin/env node
/** Exercise every local skin and capture deterministic README screenshots. */

import { mkdir, readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
const playwrightModule = process.env.PLAYWRIGHT_MODULE || "playwright";
const { chromium } = await import(playwrightModule);

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const output = join(root, "docs", "screenshots");
const defaultPortrait = join(root, "skills", "redesign-codex-ui", "assets", "default-identity", "opcspace-ip-avatar.png");
const catalog = JSON.parse(await readFile(join(root, "skills", "redesign-codex-ui", "assets", "theme-library", "catalog.json"), "utf8"));
const themes = catalog.presets.map((preset) => preset.id);
await mkdir(output, { recursive: true });

const launchOptions = { headless: true };
if (process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH) {
  launchOptions.executablePath = process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH;
}
const browser = await chromium.launch(launchOptions);
const page = await browser.newPage({ viewport: { width: 1440, height: 960 }, deviceScaleFactor: 1 });
const errors = [];
page.on("console", (message) => {
  if (message.type() === "error") errors.push(`console:${message.text()}`);
});
page.on("pageerror", (error) => errors.push(`pageerror:${error.message}`));

for (const theme of themes) {
  await page.goto(`http://127.0.0.1:4173/preview/?theme=${theme}`, { waitUntil: "networkidle" });
  await page.waitForFunction((expected) => document.body.dataset.theme === expected, theme);
  if (await page.locator(".action-card").count() !== 4) throw new Error(`${theme}: expected four action cards`);
  if (!await page.locator("#composerInput").isVisible()) throw new Error(`${theme}: composer is hidden`);
  if (!await page.locator(".sidebar").isVisible()) throw new Error(`${theme}: sidebar is hidden`);
  await page.locator("#ipPortrait").evaluate((image) => image.complete || new Promise((resolve) => image.addEventListener("load", resolve, { once: true })));
  const portraitWidth = await page.locator("#ipPortrait").evaluate((image) => image.naturalWidth);
  if (portraitWidth < 1) throw new Error(`${theme}: default IP portrait failed to load`);
  const portraitSource = await page.locator("#ipPortrait").getAttribute("src");
  if (!portraitSource?.endsWith("opcspace-ip-avatar.png")) throw new Error(`${theme}: transparent default portrait is not active`);
  const titleSize = Number.parseFloat(await page.locator("#heroTitle").evaluate((element) => getComputedStyle(element).fontSize));
  const minimumTitleSize = theme === "editorial-muse" ? 14 : 32;
  if (titleSize < minimumTitleSize) throw new Error(`${theme}: hero title is too small (${titleSize}px)`);
  await page.locator(".action-card").first().click();
  if (!(await page.locator("#composerInput").inputValue()).trim()) throw new Error(`${theme}: action did not populate composer`);
  await page.locator("#composerInput").fill("");
  await page.screenshot({ path: join(output, `${theme}.png`), fullPage: true });
  if (theme === themes[0]) {
    await page.locator("#portraitInput").setInputFiles(defaultPortrait);
    await page.waitForFunction(() => document.body.dataset.customPortrait === "true");
    await page.locator("#resetPortrait").click();
    await page.waitForFunction(() => document.body.dataset.customPortrait === "false");
  }
}

await browser.close();
if (errors.length) throw new Error(`Browser errors:\n${errors.join("\n")}`);
console.log(`Captured and tested ${themes.length} themes in ${output}`);
