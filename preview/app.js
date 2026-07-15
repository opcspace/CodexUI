const catalogUrl = "/skills/redesign-codex-ui/assets/theme-library/catalog.json";
const defaultPortraitUrl = "/skills/redesign-codex-ui/assets/default-identity/opcspace-ip-avatar.png";
const portraitStorageKey = "redesign-codex-ui.custom-portrait";
const icons = { explore: "&lt;/&gt;", build: "✦", review: "✓", fix: "⌁" };
const copy = {
  "keepsake-olive": { signature: "Momo", title: "我们该构建什么？", body: "把灵感交给 Codex，一起创造无限可能。", eyebrow: "A PERSONAL KEEPSAKE", project: "Momo 星球" },
  "midnight-stage": { signature: "MIDNIGHT / 06", title: "今晚，代码登场。", body: "把每一次构建都变成值得记住的现场。", eyebrow: "BACKSTAGE COMMAND CENTER", project: "Midnight Tour" },
  "editorial-muse": { signature: "CODEX — ISSUE 06", title: "Ideas, edited into form.", body: "Research the system. Shape the feature. Refine every line.", eyebrow: "THE WORKING EDITION", project: "Editorial Desk" },
  "pixel-companion": { signature: "COMPANION ONLINE", title: "新任务已解锁！", body: "扫描代码地图，和你的伙伴一起完成今天的任务。", eyebrow: "PLAYER 01 · READY", project: "Pixel Quest" },
  "storybook-garden": { signature: "A little chapter", title: "今天写哪一页？", body: "沿着代码的小径，让一个温柔的想法慢慢生长。", eyebrow: "CHAPTER SIX · THE MAKING", project: "Garden Stories" },
  "quiet-monogram": { signature: "M", title: "Make the work clear.", body: "A quiet workspace for deliberate thinking and durable software.", eyebrow: "MOMO / CODEX", project: "Momo Studio" },
  "red-carpet-noir": { signature: "PREMIERE / 06", title: "The next scene starts here.", body: "Scout the system, shape the performance, and refine the final cut.", eyebrow: "A FAN-MADE CINEMA EDITION", project: "Premiere Archive" },
  "cinema-contact-sheet": { signature: "FRAME 06A", title: "选择值得留下的一帧。", body: "浏览素材、搭建场景、检查每一次修改。", eyebrow: "CONTACT SHEET · TAKE 04", project: "Filmography Index" },
  "vinyl-archive": { signature: "SIDE A · TRACK 06", title: "Drop the needle. Build.", body: "Turn a codebase into a back catalog worth returning to.", eyebrow: "PERSONAL LISTENING ARCHIVE", project: "Discography Shelf" },
  "celestial-fanclub": { signature: "made under the same stars", title: "点亮下一颗星。", body: "把项目、收藏与每一次创作连接成你的专属星图。", eyebrow: "FAN-MADE CONSTELLATION · NO. 06", project: "Celestial Fanclub" }
};

const fontMap = {
  "elegant-serif": 'Georgia, "Times New Roman", serif',
  "condensed-sans": '"Arial Narrow", "Avenir Next Condensed", sans-serif',
  "high-contrast-serif": 'Didot, Bodoni 72, "Times New Roman", serif',
  "rounded-display": '"Trebuchet MS", "Avenir Next", sans-serif',
  "storybook-serif": 'Palatino, "Book Antiqua", serif',
  "book-serif": 'Baskerville, Georgia, serif',
  "cinematic-serif": 'Didot, "Bodoni 72", serif',
  "film-serif": 'Rockwell, "American Typewriter", serif',
  "record-serif": '"Cooper Black", Georgia, serif',
  "celestial-serif": 'Baskerville, "Iowan Old Style", serif'
};

async function loadJson(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`Failed to load ${url}: ${response.status}`);
  return response.json();
}

function setCssVars(preset) {
  const root = document.documentElement.style;
  const p = preset.palette;
  root.setProperty("--canvas", p.canvas);
  root.setProperty("--surface", p.surface);
  root.setProperty("--raised", p.surfaceRaised);
  root.setProperty("--ink", p.ink);
  root.setProperty("--muted", p.mutedInk);
  root.setProperty("--accent", p.accent);
  root.setProperty("--accent-soft", p.accentSoft);
  root.setProperty("--line", p.line);
  root.setProperty("--focus", p.focus);
  root.setProperty("--panel-radius", `${preset.shape.panelRadius}px`);
  root.setProperty("--control-radius", `${preset.shape.controlRadius}px`);
  root.setProperty("--display", fontMap[preset.typography.display] || fontMap["book-serif"]);
}

function renderActions(actions) {
  const container = document.querySelector("#quickActions");
  container.innerHTML = actions.map((action) => `
    <button class="action-card" data-action="${action.id}">
      <span class="action-icon">${icons[action.id]}</span>
      <b>${action.label}</b>
      <small>♥</small>
    </button>`).join("");
  container.querySelectorAll(".action-card").forEach((button) => {
    button.addEventListener("click", () => {
      const input = document.querySelector("#composerInput");
      input.value = `${button.querySelector("b").textContent}：`;
      input.focus();
    });
  });
}

function setPortrait(source, custom = false) {
  const image = document.querySelector("#ipPortrait");
  const wrapper = image.closest(".portrait-wrap");
  const avatar = document.querySelector(".avatar");
  wrapper.classList.remove("image-failed");
  image.src = source;
  avatar.textContent = "";
  avatar.style.backgroundImage = `url("${source}")`;
  avatar.style.backgroundSize = "cover";
  avatar.style.backgroundPosition = "center 20%";
  document.body.dataset.customPortrait = custom ? "true" : "false";
}

function setupPortraitControls() {
  const input = document.querySelector("#portraitInput");
  const reset = document.querySelector("#resetPortrait");
  const image = document.querySelector("#ipPortrait");
  image.addEventListener("error", () => image.closest(".portrait-wrap").classList.add("image-failed"));
  const stored = localStorage.getItem(portraitStorageKey);
  setPortrait(stored || defaultPortraitUrl, Boolean(stored));

  input.addEventListener("change", () => {
    const file = input.files?.[0];
    if (!file) return;
    if (!/^image\/(png|jpeg|webp)$/.test(file.type) || file.size > 5 * 1024 * 1024) {
      const toast = document.querySelector("#toast");
      toast.textContent = "请选择 5MB 以内的 PNG、JPEG 或 WebP 图片";
      toast.classList.add("show");
      setTimeout(() => toast.classList.remove("show"), 1600);
      input.value = "";
      return;
    }
    const reader = new FileReader();
    reader.addEventListener("load", () => {
      try {
        localStorage.setItem(portraitStorageKey, reader.result);
      } catch {
        const toast = document.querySelector("#toast");
        toast.textContent = "图片已用于当前会话，但浏览器空间不足，无法长期保存";
        toast.classList.add("show");
        setTimeout(() => toast.classList.remove("show"), 1800);
      }
      setPortrait(reader.result, true);
    });
    reader.readAsDataURL(file);
  });

  reset.addEventListener("click", () => {
    localStorage.removeItem(portraitStorageKey);
    input.value = "";
    setPortrait(defaultPortraitUrl, false);
  });
}

async function applyTheme(id, entry) {
  const preset = await loadJson(`/skills/redesign-codex-ui/assets/theme-library/${entry.path}`);
  const themeCopy = copy[id];
  document.body.dataset.theme = id;
  document.body.dataset.category = preset.category;
  setCssVars(preset);
  document.querySelector("#editionName").textContent = `${preset.label} · Codex Edition`;
  document.querySelector("#editionTagline").textContent = preset.concept.thesis;
  document.querySelector("#profileEdition").textContent = preset.label;
  document.querySelector("#signature").textContent = themeCopy.signature;
  document.querySelector("#heroTitle").textContent = themeCopy.title;
  document.querySelector("#heroBody").textContent = themeCopy.body;
  document.querySelector("#eyebrow").textContent = themeCopy.eyebrow;
  document.querySelector("#projectName").textContent = themeCopy.project;
  document.querySelector("#composerInput").value = "";
  renderActions(preset.quickActions);
  history.replaceState({}, "", `?theme=${id}`);
  document.dispatchEvent(new CustomEvent("theme-ready", { detail: { id } }));
}

async function init() {
  setupPortraitControls();
  const catalog = await loadJson(catalogUrl);
  const select = document.querySelector("#themeSelect");
  catalog.presets.forEach((entry) => select.add(new Option(entry.label, entry.id)));
  const requested = new URLSearchParams(location.search).get("theme");
  const active = catalog.presets.find((entry) => entry.id === requested) || catalog.presets[0];
  select.value = active.id;
  await applyTheme(active.id, active);
  select.addEventListener("change", async () => {
    const entry = catalog.presets.find((item) => item.id === select.value);
    await applyTheme(entry.id, entry);
  });

  document.querySelector("#sendButton").addEventListener("click", () => {
    const input = document.querySelector("#composerInput");
    const toast = document.querySelector("#toast");
    toast.textContent = input.value.trim() ? "任务已发送给 Codex" : "先写下想构建的内容";
    toast.classList.add("show");
    setTimeout(() => toast.classList.remove("show"), 1200);
  });
}

init().catch((error) => {
  console.error(error);
  document.body.dataset.loadError = "true";
});
