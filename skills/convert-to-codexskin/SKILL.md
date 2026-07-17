---
name: convert-to-codexskin
description: Safely inspect and migrate an existing Codex skin or theme that is not in `.codexskin` format into a Codex Skin Manager package. Use when the user provides a `.command` launcher, CSS and image folder, ZIP, legacy theme JSON, copied runtime, or other custom skin and asks to convert, import, migrate, package, or make it work with Codex Skin Manager.
---

# Convert to `.codexskin`

Convert legacy skin inputs into the manager's restricted data-only format. Treat all supplied scripts, CSS, archives, and binaries as untrusted input.

## Required safety boundary

- Never execute a supplied `.command`, Shell, JavaScript, Python, binary, installer, or embedded app.
- Never import package-provided CSS or scripts into `.codexskin`.
- Never extract an unknown ZIP into the repository or user home.
- Never modify, unpack, or re-sign `/Applications/ChatGPT.app`.
- Never infer public redistribution rights from possession of a file.
- Preserve the original source and unrelated worktree changes.

## Workflow

### 1. Locate the source and project tools

Require an explicit source path or attached artifact. Locate:

- this Skill's `scripts/inspect_legacy_skin.py`;
- `docs/codex-cdp-skin-launcher.md` when available;
- the `CodexSkinManager` repository and `scripts/build_codexskin.py`;
- the current project `AGENTS.md` and `.ai-context/`.

If the manager repository is unavailable, finish the read-only migration report and tell the user what repository/tool is missing. Do not invent a packager.

### 2. Inspect without executing

Run:

```bash
python3 "<skill-directory>/scripts/inspect_legacy_skin.py" \
  --source "/absolute/path/to/legacy-skin"
```

Read the JSON report. Confirm:

- input kind: directory, file, or ZIP;
- raster images already compatible with the manager;
- images requiring conversion to PNG/JPEG;
- CSS requiring template review;
- legacy theme data that can inform tokens;
- licenses or missing rights evidence;
- active content that must be excluded.

Do not treat the inventory as proof that an asset is licensed or visually correct.

### 3. Present a migration brief

Before writing the converted skin, report:

| Decision | Required content |
| --- | --- |
| Source | Absolute input path and detected kind |
| Reusable | PNG/JPEG, usable metadata, license text |
| Excluded | Scripts, CSS inside the package, binaries, fonts, nested archives |
| Conversion | WebP/GIF/SVG/HEIC or other unsupported assets |
| Template | Existing template match or reason a new manager template is required |
| Rights | Private, public non-commercial, commercial, or unknown |
| Output | Proposed skin ID, version, source directory, and `.codexskin` path |

Continue without another question when the source and rights are unambiguous. Ask for the smallest missing choice when rights, identity, or a genuinely different template direction would change the result.

### 4. Choose the conversion route

Use this order:

1. **Already `.codexskin`**: do not convert; validate and import it with the manager.
2. **Images plus JSON, no CSS dependency**: map supported values into `skin.json`.
3. **CSS or `.command` runtime**: use CSS only as a visual reference. Map it to `nightblade-v1`, `red-lotus-v1`, or `undying-phoenix-v1`.
4. **Layout cannot fit an existing template**: add a manager-owned allowlisted template with failing tests first, then rebuild the manager.
5. **Unsupported images**: preserve originals outside the package and create PNG/JPEG derivatives without overwriting originals.
6. **Missing license or unclear rights**: create a private local package with `redistributionAllowed: false` only after accurately recording the unknown/private boundary.

Never promise pixel-perfect automatic conversion from arbitrary CSS. CSS selectors and layout behavior require visual review against current Codex.

Treat the lower-left Codex account row as a reserved interaction safe area. If legacy CSS places a theme name, avatar, badge, ornament, or generated `nav::after` content at the end or bottom of the sidebar, do not preserve that placement. Move theme identity above native navigation content. For current Codex Skin Manager sidebar templates, keep the decorative title, theme name, and native content in Flex order `-2 / -1 / 0`.

### 5. Build the declarative source

Create a new directory without changing the legacy input:

```text
skins/<skin-id>/
├── skin.json
├── assets/
│   ├── background.png
│   ├── hero.png
│   └── avatar.png
├── LICENSES/
│   └── assets.txt
└── skin-brief.md
```

Follow `CodexSkinManager/docs/skin-manager/AUTHORING.md` for the exact schema. Copy only approved raster derivatives and license text. Translate colors, radii, focal points, and asset slots into allowlisted `theme` fields.

Set rights conservatively:

- use `redistributionAllowed: true` only with recorded permission for every included asset;
- otherwise use `false`;
- do not upload private screenshots or packages to public GitHub.

### 6. Package and validate

Run:

```bash
python3 "<CodexSkinManager>/scripts/build_codexskin.py" \
  --source "/absolute/path/to/skins/<skin-id>" \
  --output "/absolute/path/to/<skin-id>-<version>.codexskin"
```

Then:

1. run the authoring packager tests;
2. import through Codex Skin Manager;
3. apply and restore the skin;
4. capture wide and narrow screenshots;
5. verify core Codex interactions remain usable;
6. measure the sidebar theme identity and account-control rectangles and require `0px` overlap;
7. record output SHA-256 and rights state.

If conversion fails, fix the declarative source or manager template. Do not weaken importer checks or add legacy executable content to the package.

### 7. Submit only when requested

When the user asks to commit, push, create a PR, or publish:

- commit the converted `skin.json`, approved assets, `LICENSES`, brief, and screenshots;
- include the `.codexskin` and checksum in GitHub Release when redistribution is allowed;
- exclude private or unclear-rights assets from public Git and list every exclusion;
- stage only files belonging to the conversion;
- update `.ai-context/当前进度.md`;
- report branch, commit, PR/Release links, upload list, and excluded files.

## Completion response

Return:

```text
Detected input:
Conversion route:
Reused files:
Converted files:
Excluded active content:
Template:
Rights:
Source directory:
Output package:
SHA-256:
Import/apply/restore:
Screenshots:
Tests:
Git/Release:
Remaining limitations:
```
