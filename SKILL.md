---
name: dP狸封面
description: >-
  dP狸小红书 3:4 图文封面。三版定稿：黑底绿字花纹（dark）、绿底图下文红重点（light）、绿底图上文红重点（flip）。用于「做封面」「小红书封面」「dP狸封面」、改标题/主图/版式，以及按这套模板出图。
---
# dP狸封面（小红书 3:4）

品牌：dP狸。画幅固定 **1242×1656**。下文路径相对本技能目录。渲染入口：`scripts/build.py`。

## 硬约束

- **版本必须由用户选**：新制作先问「这次用哪版？① 黑底（dark）② 绿底图下文（light）③ 绿底图上文（flip）。」未选不得默认；本次已指定或在改同一张时沿用；明确要多版就都做。
- **品牌色不可改**：薄荷绿 `#73fcd6`、黑 `#111111`、重点红 `#D93A2B`。黑底重点行用薄荷绿，绿底两版重点行用红。
- **字体固定**：标题用卓特悦动黑 `assets/fonts/YueDongHei.ttf`。中英文之间不加空格（写「AI正在」，不写「AI 正在」）。默认 `letter_spacing: 0`。
- **句号与 logo**：标题末用实心黑圆点盖住字体「。」，再把 r4_4 monogram（`assets/logo/r4_4_pupils_black.svg`）叠在圆点内；logo 笔画用薄荷绿、鼻尖红点保留；logo 不得超出黑点（`LOGO_EM=0.185`，`FILL_EM=0.24`）。
- **行距**：dark 用 `line2_drop: 35`（墨迹间距约 50px）。light / flip 两行相对间距与定稿一致，改布局时两行必须同幅平移，禁止单独拧行距。
- **只改配置再渲染**：常规制作只写 `config.json`，用本技能 `scripts/build.py` 出图；不要另起临时脚本绕过。
- **主图来源**：可用用户提供、作品集路径、联网检索或 AI 生成；生成/检索前在对话里确认方向，落盘后再写入 `image`。

## 三版定稿

| 版本 | build 变体 | 背景 | 主图 | 第一行 | 重点行 | 其它 |
|---|---|---|---|---|---|---|
| dark | `bleed` + `red_mode: C_green` | `#111111` | 底部满宽方形 | 白 | 薄荷绿 + 黑柔光 | 顶部 logo 暗纹，`pattern_opacity: 0.14` |
| light | `frame` | `#73fcd6` | 下方红框方形，顶缘薄荷渐变 | 黑 | 红 + 白柔光 | 图框 `border: 4px #D93A2B` |
| flip | `flip` | `#73fcd6` | 上方红框方形，底缘薄荷渐变 | 黑 | 红 + 白柔光 | 两行整体上移压图约 100px；行距与 light 一致 |

示例配置：`examples/config_dark.json`、`examples/config_light.json`、`examples/config_flip.json`。示例成图：`examples/xhs_dark.png`、`examples/xhs_light.png`、`examples/xhs_light_flip.png`。

## 配置字段

```json
{
  "lines": ["第一行", "第二行"],
  "highlight": [1],
  "image": "绝对或相对路径",
  "image_position": "center",
  "font": "assets/fonts/YueDongHei.ttf",
  "period_mode": "dot",
  "letter_spacing": 0,
  "line2_drop": 35,
  "pattern_opacity": 0.14,
  "red_mode": "C_green"
}
```

- `lines`：通常两行；最后一行是重点行（与 `highlight` 对应）。
- `red_mode`：仅 dark 需要，定稿为 `C_green`。
- `line2_drop` / `pattern_*`：主要服务 dark；light/flip 勿随意改相对间距。
- 示例 config 里 `font` 若写相对路径，相对**配置文件所在目录**解析；推荐在任务 config 里写技能内字体的绝对路径，或把字体拷到任务旁再引用。

## 制作流程

1. **选版本**：按硬约束问用户。
2. **收标题与主图**：拿到 `lines`、重点行、主图路径或生成/检索任务。
3. **写配置**：在任务目录写 `config.json`（可从 `examples/` 复制对应版）。dark 记得 `red_mode` 与 `line2_drop`。
4. **渲染**：
   - dark：`python3 <技能目录>/scripts/build.py config.json <输出目录> bleed`
   - light：`python3 <技能目录>/scripts/build.py config.json <输出目录> frame`
   - flip：`python3 <技能目录>/scripts/build.py config.json <输出目录> flip`
   输出 `xhs_<variant>.png` 与同名 HTML。依赖本机 `google-chrome` headless。脚本默认从本技能 `assets/logo` 读 monogram；字体路径来自 config。
5. **目视验收**：字号撑满左右边距、句号黑点内 logo 不溢出、行距未跑偏、红框/渐变/花纹符合该版定稿；通过后再交付 PNG。
6. **交付**：先发 PNG；需要时再附 HTML 与 config。

## 改版边界

- 只改文案/主图：改 config 重渲即可。
- 用户要微调位置：同幅平移两行或微调 `line2_drop`（仅 dark），改完说明像素变化。
- 用户要新版式：另开变体，不得静默改写三版定稿参数；定稿变更需用户明确确认后再改 skill 与 `examples/`。

## 素材

| 路径 | 用途 |
|---|---|
| `assets/fonts/YueDongHei.ttf` | 标题字体 |
| `assets/logo/r4_4_pupils_black.svg` | 句号内 monogram 与 dark 花纹源 |
| `scripts/build.py` | HTML + Chrome 截图渲染 |
