# Codex macOS 皮肤制作与管理器导入指南

本文是制作 Codex 桌面皮肤的统一入口。新的默认交付物是可由 **Codex 皮肤管理器**直接导入的 `.codexskin`，不再为每套皮肤新建 `.command`、CDP 端口和注入运行时。

- 管理器项目：`/Users/admin/Documents/ai_project/CodexSkinManager`
- 本机应用：`/Users/admin/Applications/Codex 皮肤管理器.app`
- 公共仓库：[LouisDM/CodexSkinManager](https://github.com/LouisDM/CodexSkinManager)
- 下载页面：[CodexSkinManager Releases](https://github.com/LouisDM/CodexSkinManager/releases)

旧 `.command` 方案仍记录在本文末尾，只用于迁移已经存在的皮肤。制作新皮肤时直接生成 `.codexskin`，不要先制作 `.command` 再转换。

## 0. 先选择正确路线

| 场景 | 推荐路线 |
| --- | --- |
| 使用现有布局制作新配色、人物和背景 | 选择现有模板，准备 `skin.json + assets + LICENSES`，直接打包 `.codexskin` |
| 需要一种现有模板无法表达的新布局 | 先在管理器项目增加一个受信任模板，再制作数据包 |
| 已有 `.command` 皮肤 | 提取图片和权利信息，映射到现有或新增模板，再打包 `.codexskin` |
| 只想安装别人制作的皮肤 | 下载 `.codexskin`，双击或在管理器中按 `⌘O` |

### 第一次使用：只需要一句话

在 Codex 中打开本仓库，然后直接发送：

```text
查看 codex-cdp-skin-launcher.md，制作《沧元图》柳七月的 Codex 皮肤，先给我 3 个风格差异明显的方案选择。
```

不需要先提供模板名、端口或 JSON。Codex 应先定位并完整阅读本文，再返回 3 个可比较方案；每个方案至少说明名称、色彩、构图、人物焦点、适合复用的模板和素材权利风险。用户确认前不生成整套最终素材。

选中方案后只需继续回复：

```text
我选 A。参考官方造型特征，生成无水印原创同人素材，直接制作成可导入 Codex 皮肤管理器的 .codexskin，并完成宽窄屏和自动化测试。
```

需要同步到 GitHub 时再回复：

```text
确认提交。把对应皮肤的源文件、LICENSES、宽窄屏截图和获准分发的 .codexskin 一起上传；更新项目上下文，并给我 commit、PR 和 Release 链接。
```

如果素材只允许本机使用，Codex 应继续完成本地皮肤，但不能把受限图片、截图或成品上传到公开 GitHub；最终交付必须列出这些排除项。

想一次说完也可以：

```text
查看 docs/codex-cdp-skin-launcher.md，为《沧元图》柳七月制作一套 Codex 皮肤。先给我 3 个方案并推荐 1 个；等我确认后再生成无水印原创同人素材，复用或新增安全模板，直接输出 .codexskin，通过管理器导入，完成宽窄屏与自动化测试。若我要求提交，连同源文件、许可、截图和可公开分发的成品一起上传 GitHub。
```

### 为什么这样更顺

皮肤被拆成两层：

1. **管理器拥有的执行层**：CDP 启动、页面注入、恢复逻辑和 CSS 模板随管理器应用发布并接受测试。
2. **皮肤拥有的数据层**：`.codexskin` 只包含 JSON、PNG/JPEG、许可文本和权利声明。

因此每套新皮肤不再需要自己维护端口、Node 脚本、守护进程或启动器。皮肤包不能携带 `.command`、JavaScript、CSS、远程 URL 或可执行文件；管理器会检查路径、文件类型、哈希、图片和模板允许列表。

## 1. 开始前需要的信息

| 项目 | 示例 | 是否必需 |
| --- | --- | --- |
| 显示名称 | 柳七月 · 不死凰焰 | 必需 |
| 皮肤 ID | `liu-qiyue-undying-phoenix` | 必需 |
| 版本 | `1.0.0` | 必需 |
| 人物或主题 | 柳七月、《沧元图》 | 必需 |
| 视觉方向 | 不死凤凰、赤金、战斗感 | 必需 |
| 模板 | `undying-phoenix-v1` | 必需 |
| 人物立绘 | PNG/JPEG | 推荐 |
| Hero 背景 | 横向 PNG/JPEG | 推荐 |
| 素材许可说明 | `LICENSES/assets.txt` | 必需 |
| 重新分发边界 | 私用 / 可公开非商用 / 可商用 | 必需 |

如果用户只有人物名称，没有明确视觉方向，先搜索或分析公开视觉特征，给出 3 个差异明确的方案。方案确定后只制作被选中的方案。

第三方人物、Logo、照片和影视素材不等于自动获得公开分发授权。不能确认授权时：

- 优先使用用户提供或生成的无水印原创同人素材；
- 把 `redistributionAllowed` 和 `commercialUse` 设为 `false`；
- 在 `rights.notice` 和许可文本中明确“仅本地预览、非官方、不得分发”。

## 2. 当前可用模板

| template | 适合方向 |
| --- | --- |
| `nightblade-v1` | 冷蓝、夜行、刀锋、克制 |
| `red-lotus-v1` | 暗红、鎏金、红莲、厚重 |
| `undying-phoenix-v1` | 赤金、凤凰、火焰、强烈人物 Hero |

模板决定布局、选择器、装饰层和响应式行为；`skin.json` 中的令牌和图片只提供安全数据。

如果新皮肤只是换人物、背景、配色和圆角，复用现有模板。如果必须改变 DOM 布局或增加新的视觉结构，按第 8 节新增模板，不要把 CSS 塞入 `.codexskin`。

## 3. 标准皮肤源目录

建议在项目中为每套皮肤建立唯一源目录：

```text
skins/<skin-id>/
├── skin.json
├── assets/
│   ├── background.png
│   ├── hero.png
│   └── avatar.png          # 可选
└── LICENSES/
    └── assets.txt
```

`skin.json` 是唯一需要手写的包配置。`manifest.json`、文件大小和 SHA-256 哈希由打包器生成，不应手工维护。

打包器只收集：

- `skin.json` 引用的 PNG/JPEG；
- `LICENSES/` 下的 UTF-8 `.txt`；
- 自动生成的 `theme.json`、`rights.json` 和 `manifest.json`。

源目录中即使暂时保留旧 `.command`、CSS 或 JS，也不会进入输出包。为了便于维护，设计参考图、截图和旧运行时仍建议放在源目录之外。

### 3.1 完整 `skin.json` 示例

```json
{
  "schemaVersion": 1,
  "id": "liu-qiyue-undying-phoenix",
  "name": "柳七月 · 不死凰焰",
  "version": "1.0.0",
  "template": "undying-phoenix-v1",
  "minManagerVersion": "1.1.0",
  "preview": "assets/background.png",
  "author": {
    "name": "OPCspace",
    "website": null
  },
  "theme": {
    "tokens": {
      "accent": "#F26B2F",
      "accentStrong": "#FFD47A",
      "canvas": "#090404",
      "controlRadius": "12",
      "focus": "#FFD47A",
      "ink": "#FFF4DF",
      "line": "#5B251B",
      "motionDuration": "180",
      "mutedInk": "#9AAABC",
      "panelRadius": "7",
      "surface": "#140707",
      "surfaceRaised": "#23100D"
    },
    "assets": {
      "background": "assets/background.png",
      "hero": "assets/hero.png"
    },
    "focalPoints": {
      "background": {
        "x": 0.68,
        "y": 0.45
      },
      "hero": {
        "x": 0.5,
        "y": 0.2
      }
    }
  },
  "rights": {
    "redistributionAllowed": false,
    "commercialUse": false,
    "fanMade": true,
    "unofficial": true,
    "noEndorsement": true,
    "notice": "Private local preview only. Redistribution and commercial use are not permitted."
  }
}
```

### 3.2 字段约束

- `id`：3–64 字节，小写字母、数字、连字符和分段点号。
- `version`、`minManagerVersion`：严格使用 `x.y.z`。
- `preview`：必须指向包内 PNG/JPEG。
- 图片：单张不超过 32 MB；PNG 必须是真 PNG，JPEG 必须是真 JPEG。
- 许可：至少有一个 `LICENSES/**/*.txt`，必须是非空 UTF-8 文本。
- 焦点：`x` 和 `y` 均为 `0–1`，表示图片裁切时的视觉中心。
- 色彩令牌：`#RRGGBB` 或 `#RRGGBBAA`。
- 数值令牌：字符串形式的 `0–1000`。

允许的图片槽：

```text
avatar
background
hero
```

允许的颜色令牌：

```text
accent
accentStrong
canvas
focus
ink
line
mutedInk
surface
surfaceRaised
```

允许的数值令牌：

```text
controlRadius
motionDuration
panelRadius
```

## 4. 一条主流程：制作、打包、导入

### 4.1 制作视觉资源

推荐规格：

| 资源 | 推荐规格 | 要求 |
| --- | --- | --- |
| `hero.png` | 高度 1600–2400 px | 真透明背景、边缘干净、无水印 |
| `background.png` | 2400×1600 px 或更大 | 横向构图，文字区不要过于复杂 |
| `avatar.png` | 512×512 px 或更大 | 可选，主体居中 |

检查：

- 立绘没有白底伪透明、棋盘格、角标或意外文字；
- 脸部、武器等视觉重点能通过 `focalPoints` 保留；
- 宽屏、普通窗口和窄屏都不遮挡 Composer、任务列表和审批操作；
- 素材来源与使用边界已写入 `LICENSES/assets.txt`。

### 4.2 打包

直接调用管理器项目中的通用打包器：

```bash
MANAGER_REPO="/Users/admin/Documents/ai_project/CodexSkinManager"
SOURCE="/绝对路径/skins/liu-qiyue-undying-phoenix"
OUTPUT="/Users/admin/Applications/Liu-Qiyue-Undying-Phoenix-1.0.0.codexskin"

cd "$MANAGER_REPO"
npm run build:skin -- \
  --source "$SOURCE" \
  --output "$OUTPUT"
```

也可以直接运行：

```bash
python3 "/Users/admin/Documents/ai_project/CodexSkinManager/scripts/build_codexskin.py" \
  --source "/绝对路径/skins/<skin-id>" \
  --output "/绝对路径/<skin-id>-1.0.0.codexskin"
```

同一份源目录会生成字节完全一致的 store-only ZIP。未知字段、不安全路径、未知令牌、缺少许可、图片扩展名/文件头不符和不受支持模板会在打包阶段直接报错；管理器导入时还会再次完整解码图片。

### 4.3 导入和应用

生成后可直接打开：

```bash
/usr/bin/open -a "/Users/admin/Applications/Codex 皮肤管理器.app" "$OUTPUT"
```

也可以：

1. 打开“Codex 皮肤管理器”；
2. 按 `⌘O` 选择 `.codexskin`；
3. 检查名称、模板、作者和权利提示；
4. 点击“应用皮肤”；
5. 需要停用时点击“恢复默认”。

管理器负责选择自己的本机端口并启动官方 Codex。不要为皮肤填写或固定 `9340` 等端口；端口不属于皮肤包，也不是官方 Codex 的固定接口。

## 5. 在新 Codex 任务中使用的提示词

复制下面内容并替换方括号：

```text
请先完整阅读：
/Users/admin/.codex/worktrees/3ae1/CodexUI/docs/codex-cdp-skin-launcher.md

同时检查皮肤管理器项目：
/Users/admin/Documents/ai_project/CodexSkinManager

请制作一套可由 Codex 皮肤管理器直接导入的 data-only .codexskin。

皮肤信息：
- 显示名称：[皮肤显示名称]
- id：[小写英文/拼音标识]
- 人物/IP：[人物或主题]
- 视觉方向：[风格、气质、关键词]
- 期望模板：[nightblade-v1 / red-lotus-v1 / undying-phoenix-v1 / 需要新模板]
- 主色：[颜色]
- 强调色：[颜色]
- 素材路径或参考链接：[立绘、背景、参考图]
- 使用范围：[仅本地 / 公开非商用 / 已取得商业授权]

要求：
1. 先检查两个仓库状态和项目 AI 上下文，不覆盖已有皮肤或用户改动。
2. 视觉方向不明确时，先给我 3 个方案选择。
3. 新皮肤直接创建 skin.json、assets 和 LICENSES，不先创建 .command。
4. 优先复用管理器已有模板；只有现有模板无法表达布局时才新增管理器模板。
5. .codexskin 不得携带 CSS、JS、Shell、远程资源或可执行文件。
6. 使用 scripts/build_codexskin.py 打包，并通过管理器导入和应用。
7. 先写失败测试，再实现新模板或打包能力。
8. 检查宽屏和窄屏，不能遮挡任务、Composer、代码、Diff、终端和审批。
9. 完成自动化测试、真实 Codex 应用/恢复验证和官方签名检查。
10. 更新项目上下文，记录素材权利、模板、输出包、测试和下一步。
11. 如果我要求提交、推送、创建 PR 或发布，在权利允许的前提下，把对应皮肤的宽窄屏截图、声明式源文件、许可说明和可分发 `.codexskin` 一并上传到 GitHub；不得只提交代码或指南。受限素材必须改用明确授权的私有仓库/私有渠道，或在交付中说明未上传原因。

完成后告诉我：源目录、输出 .codexskin、使用的模板、如何导入/应用、测试结果、权利边界，以及提交分支、commit、PR/Release 链接和实际上传文件。
```

如果工作区路径变化，先定位本文和 `CodexSkinManager/scripts/build_codexskin.py` 的新绝对路径再执行。

## 6. 皮肤任务档案

建议建立：

```text
docs/skins/<skin-id>/skin-brief.md
```

模板：

```markdown
# <显示名称> Skin Brief

## 基本信息

- id：
- version：
- 人物/IP：
- 作者：
- 使用范围：
- 素材来源：
- 目标管理器版本：

## 视觉方向

- 关键词：
- 主色：
- 强调色：
- 字体方向：
- 人物与背景焦点：
- 必须保留的原生功能：

## 模板决策

- template：
- 复用现有模板的理由：
- 如果新增模板，涉及的管理器文件：

## 资源

- preview：
- hero：
- background：
- avatar：
- LICENSES：
- wide-screenshot：
- narrow-screenshot：

## 当前进度

- [ ] 方案确认
- [ ] 素材完成
- [ ] 宽窄屏预览
- [ ] skin.json
- [ ] 权利声明
- [ ] 打包测试
- [ ] 管理器导入
- [ ] 应用与恢复验证
- [ ] Git 提交/发布素材范围核对
- [ ] 项目上下文更新

## 输出

- source：
- package：
- sha256：
- git branch / commit：
- PR / Release：

## 已知问题与下一步

- 无
```

每次任务结束前更新档案和项目的 `.ai-context/当前进度.md`。不要把尚未确认的素材授权写成已获得。

## 7. 验证和交付标准

### 7.1 自动化验证

在管理器项目中运行：

```bash
cd "/Users/admin/Documents/ai_project/CodexSkinManager"
python3 tests/test_skin_authoring_packager.py
npm test
```

如果新增或修改模板，还需要：

```bash
npm run test:engine
npm run test:resources
npm run build:install
npm run test:bundle
npm run test:e2e
```

### 7.2 人工验证

1. 导入生成的 `.codexskin`；
2. 确认预览图、名称、作者、模板和权利状态正确；
3. 应用皮肤并检查首页、侧栏、Composer、任务页、代码、Diff、终端和审批；
4. 切换宽屏和窄屏；
5. 退出后重新应用，检查持久化；
6. 点击“恢复默认”，确认页面状态被清理；
7. 验证官方应用没有被修改或重签名。

官方完整性检查：

```bash
codesign --verify --deep --strict --verbose=2 \
  /Applications/ChatGPT.app
```

### 7.3 完成交付清单

- [ ] 视觉方向经过用户确认。
- [ ] 源目录只把安全声明式数据作为包输入。
- [ ] 素材来源和使用范围已写入 `LICENSES` 与 `rights`。
- [ ] `skin.json` 使用受支持模板和令牌。
- [ ] `.codexskin` 由通用打包器生成，未手改 manifest。
- [ ] 包内没有 `.command`、CSS、JS、二进制或远程资源。
- [ ] 管理器能成功导入、应用和恢复。
- [ ] 宽窄屏与核心工作流可用。
- [ ] 自动化测试通过。
- [ ] 官方 Codex 签名有效。
- [ ] 如果用户要求提交或发布，对应皮肤截图、源文件和获准分发的成品已经上传，而不是只保留在本机。
- [ ] 任务档案和项目上下文已更新。

### 7.4 Git 提交与上传规则

当用户明确说“提交”“commit”“push”“上传 Git”“创建 PR”或“发布 Release”时，除非用户明确缩小范围，否则默认提交范围必须包含该皮肤的完整可交接材料，不能只提交制作指南、模板代码或打包脚本：

1. `skins/<skin-id>/skin.json`、被引用的 `assets/`、`LICENSES/` 和 `skin-brief.md`；
2. 对应皮肤的宽屏、窄屏截图，建议命名为 `docs/screenshots/<skin-id>.png` 与 `docs/screenshots/<skin-id>-narrow.png`；
3. 新增或修改的管理器模板、测试、作者文档和项目上下文；
4. 权利允许公开分发的 `.codexskin` 与 SHA-256；仓库不跟踪发行二进制时，上传到对应 GitHub Release，并在 PR 中链接；
5. 能让另一台设备上的 AI 重新打包、验证和发布所需的非敏感文件。

提交前必须先核对 `rights.json`/`skin.json` 与 `LICENSES`：

- `redistributionAllowed: true`：可以把对应源素材、截图和成品上传到公开 Git/Release，但仍要遵守 `commercialUse` 和署名要求；
- `redistributionAllowed: false`：不得上传到公开仓库或公开 Release。只有用户明确授权并确认目标为私有仓库/私有渠道时才能上传；否则只提交安全的代码、模板、测试和文档，并清楚列出未上传的素材、截图或成品；
- 权利不明：按不可公开处理，不得因为收到“提交”指令就推定已获授权。

发布前执行并检查：

```bash
git status --short
git diff --cached --name-status
```

只精确暂存本次皮肤文件，避免带入其他工作区改动。完成后必须报告分支、commit、PR/Release 链接、实际上传清单，以及因权利或仓库策略未上传的文件。

## 8. 什么时候需要新增管理器模板

只有下面情况才新增模板：

- 需要新的页面结构或装饰语法；
- 现有模板的响应式行为不适用；
- 仅靠允许的颜色、圆角、动效时长和图片槽无法实现设计。

新增模板至少同步修改：

```text
CodexSkinManager/
├── skin-manager/Sources/SkinCore/SkinPackageModels.swift
├── skin-manager/Sources/CodexSkinManager/Resources/Engine/injector.mjs
├── skin-manager/Sources/CodexSkinManager/Resources/Templates/<template>.css
├── scripts/build_codexskin.py
├── tests/test_skin_manager_cdp_engine.mjs
├── tests/test_builtin_skin_packages.py
└── tests/test_codex_skin_manager_bundle.py
```

规则：

- 模板 CSS 属于管理器，不属于皮肤包；
- Swift 合约、Node `TEMPLATE_CATALOG` 和打包器允许列表必须一致；
- CSS 不得使用 `@import`、远程 URL 或工作区绝对路径；
- 装饰层必须 `pointer-events: none`；
- 提供窄屏和 `prefers-reduced-motion` 降级；
- 先添加失败测试，再实现模板并重建管理器。

## 9. 已有 `.command` 皮肤的迁移

旧启动器不能直接作为 `.codexskin` 导入，因为它包含可执行脚本和自带 CSS。正确迁移方式：

1. 定位旧运行时中的人物图、背景图和素材说明；
2. 判断旧 CSS 能否映射到现有模板；
3. 如果不能，先按第 8 节把 CSS 审核并迁移为管理器模板；
4. 新建标准源目录和 `skin.json`；
5. 用通用打包器生成 `.codexskin`；
6. 通过管理器导入、应用和恢复；
7. 验证成功后再决定是否保留旧 `.command`，不要自动删除用户文件。

迁移时不会把旧文件中的以下内容打入包：

```text
*.command
*.sh
*.js
*.mjs
*.css
injector.*
renderer-inject.*
```

旧运行时里的 CSS 只能作为开发参考，不能作为包内容。旧端口、PID、日志目录、状态键和守护进程配置全部废弃，由管理器统一负责。

## 10. 旧 `.command` / CDP 架构说明（仅供排错）

旧流程是：

```text
双击 .command
        ↓
用某个 127.0.0.1 CDP 端口启动官方 Codex
        ↓
自带 injector.mjs 发现 app:// 页面
        ↓
Runtime.evaluate 注入自带 CSS 和图片
        ↓
守护进程处理刷新和路由变化
```

它的主要维护成本是每套皮肤都复制启动器、端口、注入脚本、CSS、PID 和日志逻辑，且容易因端口冲突或目标页面竞态失败。这正是新流程不再把 `.command` 作为交付格式的原因。

如果仍需排查旧启动器：

- CDP 只能监听 `127.0.0.1`，不能监听 `0.0.0.0`；
- 不应修改、解包或重签名 `/Applications/ChatGPT.app`；
- Codex 已普通启动时应先由用户按 `⌘Q` 正常退出；
- 装饰层必须 `pointer-events: none`；
- 应有幂等安装、`cleanup()`、等待 `app://` 目标和恢复逻辑；
- 旧端口只是该启动器的本机配置，不是官方 Codex 的固定端口。

除非是在迁移或修复已有旧皮肤，不要再为新皮肤复制这套架构。
