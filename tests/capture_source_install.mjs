#!/usr/bin/env node
/** Verify and capture a skin that was installed into an editable source checkout. */

import { mkdir } from "node:fs/promises";
import { dirname, resolve } from "node:path";
const playwrightModule = process.env.PLAYWRIGHT_MODULE || "playwright";
const { chromium } = await import(playwrightModule);

const url = process.env.SOURCE_FIXTURE_URL || "http://127.0.0.1:4174/";
const output = resolve(process.env.SOURCE_SCREENSHOT || "docs/screenshots/local-source-applied.png");
await mkdir(dirname(output), { recursive: true });
const options = { headless: true };
if (process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH) options.executablePath = process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH;
const browser = await chromium.launch(options);
const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
const errors = [];
page.on("console", (message) => { if (message.type() === "error") errors.push(message.text()); });
page.on("pageerror", (error) => errors.push(error.message));
await page.goto(url, { waitUntil: "networkidle" });
if (await page.locator("body").getAttribute("data-codex-skin") !== "keepsake-olive") throw new Error("Theme attribute was not installed");
if (await page.locator("link[data-codex-skin-stylesheet]").count() !== 1) throw new Error("Installed stylesheet is not linked");
const portrait = page.locator("img[data-codex-ip-portrait]");
await portrait.evaluate((image) => image.complete || new Promise((resolve) => image.addEventListener("load", resolve, { once: true })));
if (await portrait.evaluate((image) => image.naturalWidth) < 1) throw new Error("Installed transparent portrait did not load");
const background = await page.locator("body").evaluate((element) => getComputedStyle(element).backgroundColor);
if (background !== "rgb(244, 241, 232)") throw new Error(`Theme CSS is not active: ${background}`);
await page.screenshot({ path: output, fullPage: true });
await browser.close();
if (errors.length) throw new Error(`Browser errors:\n${errors.join("\n")}`);
console.log(`Verified installed source UI and captured ${output}`);
