#!/usr/bin/env python3
"""构建 DSH 客户端插件：二次元主题（壁纸 + 全套配色/字体/玻璃拟态）。

设计要点：
  * 调色板：樱花粉 + 天空蓝 + 薰衣草紫；深色主题为深夜紫 + 霓虹粉/青。
  * 全部通过 **内联 !important** 写 token，不依赖样式表优先级。
  * 外壳容器/大面板 → 半透明 + 毛玻璃(backdrop-filter)，让壁纸透出。
  * 弹窗/浮层 → 主题化的**高不透明度**表面（0.94~0.95），保证可读，不做成透明。
  * 字体：圆体（圆体-简 / Hiragino Maru Gothic ProN / PingFang SC 兜底）。
  * 自愈：window 绑定的定时器，React 挂载后补齐；弹窗出现时也会被主题化。
"""
import base64, io, json, os
from PIL import Image

PLUGIN = "."
W, H, Q = 2560, 1440, 88
import os as _os
def pick(*cands):
    for c in cands:
        if _os.path.exists(c):
            return c
    raise SystemExit("缺少壁纸源文件：" + " / ".join(cands))
SRC = pick("anime_bg_4k.png", "assets/wallpaper-sakura.jpg")

os.makedirs(f"{PLUGIN}/lib", exist_ok=True)
os.makedirs(f"{PLUGIN}/assets", exist_ok=True)

# ---- 1. 壁纸 ----
im = Image.open(SRC).convert("RGB").resize((W, H), Image.LANCZOS)
buf = io.BytesIO()
im.save(buf, "JPEG", quality=Q, optimize=True, progressive=True)
jpg = buf.getvalue()
b64 = base64.b64encode(jpg).decode()
open(f"{PLUGIN}/wallpaper.jpg", "wb").write(jpg)
print(f"壁纸: {W}x{H} JPEG q{Q} -> {len(jpg)/1024:.0f} KB")
# 皮肤 2 的壁纸（用户提供的图，保持原始尺寸不放大）
SRC2 = pick("zelda_bg_source.png", "assets/wallpaper-zelda.jpg")
im2 = Image.open(SRC2).convert("RGB")
buf2 = io.BytesIO()
im2.save(buf2, "JPEG", quality=90, optimize=True, progressive=True)
jpg2 = buf2.getvalue()
b64z = base64.b64encode(jpg2).decode()
open(f"{PLUGIN}/wallpaper-zelda.jpg", "wb").write(jpg2)
print(f"壁纸2(塞尔达): {im2.size[0]}x{im2.size[1]} JPEG q90 -> {len(jpg2)/1024:.0f} KB")

# ---- 2. 宿主侧 ----
open(f"{PLUGIN}/lib/index.js", "w").write(
    "/** 二次元主题插件（宿主侧）。只贡献浏览器呈现。 */\n"
    "export function apply() {}\n"
)

# ---- 3. package.json ----
json.dump({
    "name": PLUGIN,
    "version": "0.5.0",
    "private": True,
    "type": "module",
    "description": "Skins for the DeepSeek Harness (DSH) desktop/web GUI: Sakura Dusk & Sky Island",
    "main": "lib/index.js",
    "exports": {
        ".": {"default": "./lib/index.js"},
        "./client": {"default": "./lib/client.js"},
        "./package.json": "./package.json",
    },
    "dsh": {"client": {"inject": [], "platform": "web", "immediately": True}},
}, open(f"{PLUGIN}/package.json", "w"), ensure_ascii=False, indent=2)

# ---- 4. 调色板 ----
PALETTE = {
    "light": {
        # 表面（半透明，透出壁纸）
        "--dsw-alias-bg-base": "rgba(255, 250, 252, 0.16)",
        "--dsw-alias-bg-layer-1": "rgba(255, 251, 253, 0.18)",
        "--dsw-alias-bg-layer-2": "rgba(255, 247, 251, 0.26)",
        "--dsw-alias-bg-layer-3": "rgba(255, 255, 255, 0.42)",
        "--dsw-alias-bg-module-platform": "rgba(243, 240, 255, 0.24)",
        "--dsw-alias-bg-overlay": "rgba(255, 240, 248, 0.52)",
        "--dsw-alias-bg-mask-1": "rgba(0, 0, 0, 0.14)",
        "--dsw-alias-bg-mask-2": "rgba(0, 0, 0, 0.07)",
        "--dsw-alias-bg-mask-3": "rgba(0, 0, 0, 0.30)",
        "--dsw-alias-bg-multi-select": "rgba(255, 240, 246, 0.40)",
        "--dsw-alias-bg-skeleton": "rgba(255, 150, 195, 0.12)",
        "--dsw-specific-input-major": "rgba(255, 255, 255, 0.46)",
        "--dsw-specific-sidebar-fill": "rgba(255, 238, 246, 0.26)",
        # 交互态（粉色）
        "--dsw-alias-interactive-bg-hover": "rgba(255, 150, 190, 0.16)",
        "--dsw-alias-interactive-bg-active": "rgba(255, 150, 190, 0.26)",
        "--dsw-alias-interactive-bg-hover-accent": "rgba(255, 130, 180, 0.30)",
        "--dsw-alias-interactive-bg-hover-solid": "rgba(255, 216, 232, 0.75)",
        # 文字（深梅紫，暖调）
        "--dsw-alias-label-primary": "#3A2A46",
        "--dsw-alias-label-primary-dimmed": "#4A3856",
        "--dsw-alias-label-primary-bluish": "#4A3A6A",
        "--dsw-alias-label-primary-foreground": "#FFFFFF",
        "--dsw-alias-label-primary-inverted": "#FFFFFF",
        "--dsw-alias-label-secondary": "#6E5A7E",
        "--dsw-alias-label-tertiary": "#9482A6",
        "--dsw-alias-label-caption": "#A894BA",
        "--dsw-alias-label-dimmed": "#C6B6D4",
        # 描边（粉紫）
        "--dsw-alias-border-l1": "rgba(255, 165, 205, 0.22)",
        "--dsw-alias-border-l2": "rgba(255, 150, 195, 0.30)",
        "--dsw-alias-border-l3": "rgba(226, 150, 200, 0.38)",
        "--dsw-alias-border-l4": "rgba(205, 140, 190, 0.48)",
        "--dsw-elevation-stroke-color": "rgba(255, 165, 205, 0.40)",
        # 主色（樱花粉）+ 辅色（天空青）
        "--dsw-alias-brand-primary": "#FF6FA5",
        "--dsw-alias-brand-primary-invert": "#FF6FA5",
        "--dsw-alias-brand-text": "#C2306A",
        "--dsw-alias-button-primary-fill": "#FF6FA5",
        "--dsw-alias-button-primary-hover": "#FF4E90",
        "--dsw-alias-button-primary-dimmed": "rgba(255, 111, 165, 0.35)",
        "--dsw-alias-state-business-primary": "#4CC3E8",
        "--dsw-alias-state-business-tertiary": "rgba(76, 195, 232, 0.22)",
        "--dsw-alias-label-deep-diving": "#7A4BA8",
        # 滚动条
        "--dsw-alias-scrollbar-bg-l1": "rgba(255, 150, 195, 0.30)",
        "--dsw-alias-scrollbar-bg-l2": "rgba(255, 150, 195, 0.30)",
        "--dsw-alias-scrollbar-hover-l1": "rgba(255, 111, 165, 0.55)",
        "--dsw-alias-scrollbar-hover-l2": "rgba(255, 111, 165, 0.55)",
        # 柔光阴影
        "--dsw-shadow-lv1": "0 2px 8px rgba(255, 120, 175, 0.14)",
        "--dsw-shadow-lv1-blur": "0 4px 14px rgba(180, 120, 220, 0.10)",
        "--dsw-shadow-lv2": "0 6px 18px rgba(255, 120, 175, 0.16), 0 2px 8px rgba(180, 120, 220, 0.10)",
        "--dsw-shadow-lv3": "0 0 1px rgba(230, 150, 200, 0.30), 0 12px 36px rgba(160, 110, 220, 0.20)",
    },
    "dark": {
        "--dsw-alias-bg-base": "rgba(24, 20, 44, 0.12)",
        "--dsw-alias-bg-layer-1": "rgba(30, 25, 54, 0.14)",
        "--dsw-alias-bg-layer-2": "rgba(38, 31, 66, 0.22)",
        "--dsw-alias-bg-layer-3": "rgba(46, 38, 78, 0.40)",
        "--dsw-alias-bg-module-platform": "rgba(40, 33, 70, 0.20)",
        "--dsw-alias-bg-overlay": "rgba(42, 34, 76, 0.50)",
        "--dsw-alias-bg-mask-1": "rgba(0, 0, 0, 0.24)",
        "--dsw-alias-bg-mask-2": "rgba(0, 0, 0, 0.12)",
        "--dsw-alias-bg-mask-3": "rgba(0, 0, 0, 0.34)",
        "--dsw-alias-bg-multi-select": "rgba(46, 38, 78, 0.40)",
        "--dsw-alias-bg-skeleton": "rgba(255, 150, 210, 0.10)",
        "--dsw-specific-input-major": "rgba(38, 31, 66, 0.42)",
        "--dsw-specific-sidebar-fill": "rgba(26, 21, 48, 0.24)",
        "--dsw-alias-interactive-bg-hover": "rgba(255, 140, 190, 0.18)",
        "--dsw-alias-interactive-bg-active": "rgba(255, 140, 190, 0.28)",
        "--dsw-alias-interactive-bg-hover-accent": "rgba(255, 140, 190, 0.34)",
        "--dsw-alias-interactive-bg-hover-solid": "rgba(72, 56, 108, 0.75)",
        "--dsw-alias-label-primary": "#F3EBFF",
        "--dsw-alias-label-primary-dimmed": "#E4D8FA",
        "--dsw-alias-label-primary-bluish": "#DCE8FF",
        "--dsw-alias-label-primary-foreground": "#171320",
        "--dsw-alias-label-primary-inverted": "#2E2740",
        "--dsw-alias-label-secondary": "#C9B8E6",
        "--dsw-alias-label-tertiary": "#A692C9",
        "--dsw-alias-label-caption": "#8C79AE",
        "--dsw-alias-label-dimmed": "#6E5C8C",
        "--dsw-alias-border-l1": "rgba(190, 160, 255, 0.18)",
        "--dsw-alias-border-l2": "rgba(190, 160, 255, 0.26)",
        "--dsw-alias-border-l3": "rgba(200, 170, 255, 0.34)",
        "--dsw-alias-border-l4": "rgba(210, 180, 255, 0.44)",
        "--dsw-elevation-stroke-color": "rgba(190, 160, 255, 0.40)",
        "--dsw-alias-brand-primary": "#FF8CC8",
        "--dsw-alias-brand-primary-invert": "#FF8CC8",
        "--dsw-alias-brand-text": "#FFB3D9",
        "--dsw-alias-button-primary-fill": "#FF6FB5",
        "--dsw-alias-button-primary-hover": "#FF8CC8",
        "--dsw-alias-button-primary-dimmed": "rgba(255, 111, 181, 0.38)",
        "--dsw-alias-state-business-primary": "#6FE3FF",
        "--dsw-alias-state-business-tertiary": "rgba(111, 227, 255, 0.22)",
        "--dsw-alias-label-deep-diving": "#C9A8FF",
        "--dsw-alias-scrollbar-bg-l1": "rgba(190, 160, 255, 0.28)",
        "--dsw-alias-scrollbar-bg-l2": "rgba(190, 160, 255, 0.28)",
        "--dsw-alias-scrollbar-hover-l1": "rgba(255, 140, 200, 0.55)",
        "--dsw-alias-scrollbar-hover-l2": "rgba(255, 140, 200, 0.55)",
        "--dsw-shadow-lv1": "0 2px 10px rgba(0, 0, 0, 0.35)",
        "--dsw-shadow-lv1-blur": "0 4px 16px rgba(120, 80, 200, 0.18)",
        "--dsw-shadow-lv2": "0 6px 20px rgba(0, 0, 0, 0.40), 0 0 12px rgba(255, 140, 200, 0.12)",
        "--dsw-shadow-lv3": "0 0 1px rgba(200, 170, 255, 0.35), 0 14px 40px rgba(90, 60, 160, 0.35)",
    },
}

# 弹窗专用：主题化但高不透明度（保证可读，不做透明）
DIALOG = {
    "light": {
        "--dsw-alias-bg-base": "rgba(255, 253, 255, 0.98)",
        "--dsw-alias-bg-layer-1": "rgba(255, 253, 255, 0.98)",
        "--dsw-alias-bg-layer-2": "rgba(255, 250, 253, 0.98)",
        "--dsw-alias-bg-layer-3": "rgba(255, 255, 255, 0.98)",
        "--dsw-alias-bg-module-platform": "rgba(250, 247, 255, 0.97)",
        "--dsw-specific-input-major": "rgba(255, 253, 255, 0.98)",
    },
    "dark": {
        "--dsw-alias-bg-base": "rgba(28, 23, 50, 0.95)",
        "--dsw-alias-bg-layer-1": "rgba(30, 25, 52, 0.97)",
        "--dsw-alias-bg-layer-2": "rgba(36, 30, 62, 0.98)",
        "--dsw-alias-bg-layer-3": "rgba(44, 36, 74, 0.98)",
        "--dsw-alias-bg-module-platform": "rgba(38, 31, 66, 0.98)",
        "--dsw-specific-input-major": "rgba(38, 31, 66, 0.98)",
    },
}

# 皮肤 2：天空之岛 · 塞尔达风（浅色优先：希卡青 + 古金 + 象牙白面板）
PALETTE_ZELDA = {
    "light": {
        "--dsw-alias-bg-base": "rgba(236, 246, 249, 0.30)",
        "--dsw-alias-bg-layer-1": "rgba(240, 249, 251, 0.34)",
        "--dsw-alias-bg-layer-2": "rgba(246, 252, 253, 0.44)",
        "--dsw-alias-bg-layer-3": "rgba(252, 255, 255, 0.60)",
        "--dsw-alias-bg-module-platform": "rgba(222, 240, 244, 0.40)",
        "--dsw-alias-bg-overlay": "rgba(238, 248, 250, 0.66)",
        "--dsw-alias-bg-multi-select": "rgba(220, 240, 244, 0.38)",
        "--dsw-alias-bg-skeleton": "rgba(15, 168, 184, 0.12)",
        "--dsw-alias-bg-mask-1": "rgba(0, 0, 0, 0.16)",
        "--dsw-alias-bg-mask-2": "rgba(0, 0, 0, 0.06)",
        "--dsw-alias-bg-mask-3": "rgba(0, 0, 0, 0.26)",
        "--dsw-specific-input-major": "rgba(250, 254, 255, 0.64)",
        "--dsw-specific-sidebar-fill": "rgba(236, 246, 249, 0.30)",
        "--dsw-alias-interactive-bg-hover": "rgba(15, 168, 184, 0.14)",
        "--dsw-alias-interactive-bg-active": "rgba(15, 168, 184, 0.24)",
        "--dsw-alias-interactive-bg-hover-accent": "rgba(15, 168, 184, 0.28)",
        "--dsw-alias-interactive-bg-hover-solid": "rgba(198, 234, 240, 0.90)",
        "--dsw-alias-label-primary": "#16323C",
        "--dsw-alias-label-primary-dimmed": "#1E414C",
        "--dsw-alias-label-primary-bluish": "#123A52",
        "--dsw-alias-label-primary-foreground": "#FFFFFF",
        "--dsw-alias-label-primary-inverted": "#FFFFFF",
        "--dsw-alias-label-secondary": "#3E6470",
        "--dsw-alias-label-tertiary": "#628692",
        "--dsw-alias-label-caption": "#86A5AE",
        "--dsw-alias-label-dimmed": "#AEC6CC",
        "--dsw-alias-border-l1": "rgba(0, 170, 190, 0.16)",
        "--dsw-alias-border-l2": "rgba(0, 160, 185, 0.24)",
        "--dsw-alias-border-l3": "rgba(0, 150, 180, 0.32)",
        "--dsw-alias-border-l4": "rgba(0, 130, 165, 0.42)",
        "--dsw-elevation-stroke-color": "rgba(0, 160, 185, 0.35)",
        "--dsw-alias-brand-primary": "#0FA8B8",
        "--dsw-alias-brand-primary-invert": "#0FA8B8",
        "--dsw-alias-brand-text": "#0A7684",
        "--dsw-alias-button-primary-fill": "#0FA8B8",
        "--dsw-alias-button-primary-hover": "#0B8E9C",
        "--dsw-alias-button-primary-dimmed": "rgba(15, 168, 184, 0.35)",
        "--dsw-alias-state-business-primary": "#D9A02B",
        "--dsw-alias-state-business-tertiary": "rgba(217, 160, 43, 0.22)",
        "--dsw-alias-label-deep-diving": "#1B7F8C",
        "--dsw-alias-scrollbar-bg-l1": "rgba(15, 168, 184, 0.28)",
        "--dsw-alias-scrollbar-bg-l2": "rgba(15, 168, 184, 0.28)",
        "--dsw-alias-scrollbar-hover-l1": "rgba(15, 168, 184, 0.55)",
        "--dsw-alias-scrollbar-hover-l2": "rgba(15, 168, 184, 0.55)",
        "--dsw-shadow-lv1": "0 2px 8px rgba(10, 90, 110, 0.14)",
        "--dsw-shadow-lv1-blur": "0 4px 14px rgba(10, 90, 110, 0.10)",
        "--dsw-shadow-lv2": "0 6px 18px rgba(10, 90, 110, 0.16), 0 2px 8px rgba(15, 168, 184, 0.10)",
        "--dsw-shadow-lv3": "0 0 1px rgba(0, 150, 175, 0.30), 0 12px 36px rgba(10, 80, 100, 0.20)",
    },
    "dark": {
        "--dsw-alias-bg-base": "rgba(8, 28, 38, 0.30)",
        "--dsw-alias-bg-layer-1": "rgba(11, 34, 45, 0.34)",
        "--dsw-alias-bg-layer-2": "rgba(15, 42, 55, 0.44)",
        "--dsw-alias-bg-layer-3": "rgba(21, 54, 69, 0.58)",
        "--dsw-alias-bg-module-platform": "rgba(15, 44, 57, 0.42)",
        "--dsw-alias-bg-overlay": "rgba(13, 38, 50, 0.72)",
        "--dsw-alias-bg-multi-select": "rgba(21, 54, 69, 0.48)",
        "--dsw-alias-bg-skeleton": "rgba(53, 208, 223, 0.10)",
        "--dsw-alias-bg-mask-1": "rgba(0, 0, 0, 0.24)",
        "--dsw-alias-bg-mask-2": "rgba(0, 0, 0, 0.12)",
        "--dsw-alias-bg-mask-3": "rgba(0, 0, 0, 0.34)",
        "--dsw-specific-input-major": "rgba(15, 42, 55, 0.60)",
        "--dsw-specific-sidebar-fill": "rgba(8, 28, 38, 0.32)",
        "--dsw-alias-interactive-bg-hover": "rgba(53, 208, 223, 0.16)",
        "--dsw-alias-interactive-bg-active": "rgba(53, 208, 223, 0.26)",
        "--dsw-alias-interactive-bg-hover-accent": "rgba(53, 208, 223, 0.32)",
        "--dsw-alias-interactive-bg-hover-solid": "rgba(24, 70, 86, 0.88)",
        "--dsw-alias-label-primary": "#EAFBFF",
        "--dsw-alias-label-primary-dimmed": "#D6F0F6",
        "--dsw-alias-label-primary-bluish": "#CFE9FF",
        "--dsw-alias-label-primary-foreground": "#0A2430",
        "--dsw-alias-label-primary-inverted": "#0A2430",
        "--dsw-alias-label-secondary": "#A9D3DC",
        "--dsw-alias-label-tertiary": "#7FB0BC",
        "--dsw-alias-label-caption": "#5F8F9C",
        "--dsw-alias-label-dimmed": "#4A7480",
        "--dsw-alias-border-l1": "rgba(120, 220, 235, 0.18)",
        "--dsw-alias-border-l2": "rgba(120, 220, 235, 0.26)",
        "--dsw-alias-border-l3": "rgba(130, 225, 240, 0.34)",
        "--dsw-elevation-stroke-color": "rgba(120, 220, 235, 0.40)",
        "--dsw-alias-border-l4": "rgba(140, 230, 245, 0.44)",
        "--dsw-alias-brand-primary": "#35D0DF",
        "--dsw-alias-brand-primary-invert": "#35D0DF",
        "--dsw-alias-brand-text": "#7FE6F0",
        "--dsw-alias-button-primary-fill": "#1FB6C6",
        "--dsw-alias-button-primary-hover": "#35D0DF",
        "--dsw-alias-button-primary-dimmed": "rgba(31, 182, 198, 0.38)",
        "--dsw-alias-state-business-primary": "#E8B44A",
        "--dsw-alias-state-business-tertiary": "rgba(232, 180, 74, 0.22)",
        "--dsw-alias-label-deep-diving": "#8FE3EE",
        "--dsw-alias-scrollbar-bg-l1": "rgba(120, 220, 235, 0.28)",
        "--dsw-alias-scrollbar-bg-l2": "rgba(120, 220, 235, 0.28)",
        "--dsw-alias-scrollbar-hover-l1": "rgba(53, 208, 223, 0.55)",
        "--dsw-alias-scrollbar-hover-l2": "rgba(53, 208, 223, 0.55)",
        "--dsw-shadow-lv1": "0 2px 10px rgba(0, 0, 0, 0.35)",
        "--dsw-shadow-lv1-blur": "0 4px 16px rgba(10, 80, 95, 0.20)",
        "--dsw-shadow-lv2": "0 6px 20px rgba(0, 0, 0, 0.40), 0 0 12px rgba(53, 208, 223, 0.12)",
        "--dsw-shadow-lv3": "0 0 1px rgba(130, 225, 240, 0.35), 0 14px 40px rgba(4, 45, 58, 0.40)",
    },
}

DIALOG_ZELDA = {
    "light": {
        "--dsw-alias-bg-base": "rgba(252, 255, 255, 0.97)",
        "--dsw-alias-bg-layer-1": "rgba(252, 255, 255, 0.98)",
        "--dsw-alias-bg-layer-2": "rgba(255, 254, 248, 0.98)",
        "--dsw-alias-bg-layer-3": "rgba(255, 255, 255, 0.99)",
        "--dsw-alias-bg-module-platform": "rgba(240, 250, 252, 0.97)",
        "--dsw-specific-input-major": "rgba(255, 255, 255, 0.98)",
    },
    "dark": {
        "--dsw-alias-bg-base": "rgba(11, 34, 45, 0.97)",
        "--dsw-alias-bg-layer-1": "rgba(13, 38, 50, 0.98)",
        "--dsw-alias-bg-layer-2": "rgba(16, 44, 58, 0.98)",
        "--dsw-alias-bg-layer-3": "rgba(21, 54, 69, 0.99)",
        "--dsw-alias-bg-module-platform": "rgba(15, 44, 57, 0.97)",
        "--dsw-specific-input-major": "rgba(15, 42, 55, 0.98)",
    },
}

FONT_ZELDA = ('"PingFang SC","Hiragino Sans GB","Hiragino Maru Gothic ProN",'
              '"Microsoft YaHei",system-ui,sans-serif')

FONT = ('"圆体-简","Yuanti SC","Hiragino Maru Gothic ProN","PingFang SC",'
        '"Hiragino Sans GB","Microsoft YaHei",system-ui,sans-serif')

# ---- 5. 浏览器侧 bundle ----
client_js = f"""window.__ModuleLoader__.load({{
\tid: "{PLUGIN}",
\tfactory: (require) => {{
\t\tvar module = {{ exports: {{}} }};
\t\tvar exports = module.exports;
\t\tObject.defineProperty(exports, Symbol.toStringTag, {{ value: "Module" }});

\t\tconst WALLPAPER = "data:image/jpeg;base64,{b64}";
\t\tconst PALETTE = {json.dumps(PALETTE, ensure_ascii=False)};
\t\tconst DIALOG = {json.dumps(DIALOG, ensure_ascii=False)};
\t\tconst FONT = {json.dumps(FONT, ensure_ascii=False)};
\t\tconst WALLPAPER_ZELDA = "data:image/jpeg;base64,{b64z}";
\t\tconst PALETTE_ZELDA = {json.dumps(PALETTE_ZELDA, ensure_ascii=False)};
\t\tconst DIALOG_ZELDA = {json.dumps(DIALOG_ZELDA, ensure_ascii=False)};
\t\tconst FONT_ZELDA = {json.dumps(FONT_ZELDA, ensure_ascii=False)};
\t\tconst LAYER_ID = "dsh-anime-wallpaper-layer";
\t\tconst SHELL_SELECTOR = '[class*="_frame"],[class*="_centerCol"],[class*="_sidebarCol"],[class*="_rightbarCol"]';
\t\t/* 严格：只有这些才算真正的弹窗（会被主题化成高不透明表面） */
\t\tconst DIALOG_HINT = /(dialog|modal|popup|popover|drawer|sheet)/i;
\t\t/* 宽松：可能是浮层，仅用于"跳过扫描、保持原样"，绝不改成不透明 */
\t\tconst OVERLAY_HINT = /(dropdown|menu|tooltip|toast|overlay|portal|scrim|mask|float|command)/i;
\t\tconst BLUR = "none";

\t\tconst React = require("react");
\t\tconst STORAGE_KEY = "dsh-anime-skin";
\t\tconst DEFAULT_SKIN = "sakura-dusk";
\t\t/* 皮肤注册表：以后加新皮肤，往这个数组里加一项即可 */
\t\tconst SKINS = [
\t\t\t{{
\t\t\t\tid: "original",
\t\t\t\tname: "原始皮肤",
\t\t\t\tdesc: "DeepSeek Harness 默认外观（不施加任何自定义）",
\t\t\t\tkind: "original"
\t\t\t}},
\t\t\t{{
\t\t\t\tid: "sakura-dusk",
\t\t\t\tname: "二次元 · 樱花黄昏",
\t\t\t\tdesc: "樱花粉 + 天空蓝 · 圆体字 · 黄昏云海壁纸 · 半透明面板",
\t\t\t\tkind: "theme",
\t\t\t\twallpaper: WALLPAPER,
\t\t\t\tfont: FONT,
\t\t\t\tpalette: PALETTE,
\t\t\t\tdialog: DIALOG,
\t\t\t\twallpaperFilter: {{ light: "none", dark: "none" }},
\t\t\t\t/* 与「深度求索中」同一色系（实测像素 #B2A5DD ≈ label-deep-diving #C9A8FF）*/
\t\t\t\taccentGradient: {{ light: "linear-gradient(92deg, #7A4BA8 0%, #A98CFF 55%, #C9A8FF 100%)", dark: "linear-gradient(92deg, #A98CFF 0%, #C9A8FF 55%, #E4D8FF 100%)" }},
\t\t\t\taccentColor: {{ light: "#7A4BA8", dark: "#C9A8FF" }},
\t\t\t\tbadgeGradient: {{ light: "linear-gradient(92deg, #9B7BE0 0%, #C9A8FF 100%)", dark: "linear-gradient(92deg, #8A63C8 0%, #C9A8FF 100%)" }},
\t\t\t\tbadgeSolid: {{ light: "#B9A0F0", dark: "#A98CFF" }},
\t\t\t\tbadgePillBg: {{ light: "#6A3F98", dark: "#5E3CA8" }},
\t\t\t\tbadgeText: "#FFFFFF",
\t\t\t\tbadgeDecor: false,
\t\t\t\tblur: BLUR,
\t\t\t\t/* 侧边栏/右栏：毛玻璃 + 更厚底色，保证文字清晰 */
\t\t\t\tsidebar: {{ light: "rgba(255, 246, 250, 0.40)", dark: "rgba(22, 18, 40, 0.36)" }},
\t\t\t\tsidebarBlur: "blur(24px) saturate(1.35)"
\t\t\t}},
\t\t\t{{
\t\t\t\tid: "zelda-sky",
\t\t\t\tname: "天空之岛 · 塞尔达风",
\t\t\t\tdesc: "希卡青 + 古金 · 明亮浅色 · 浮空岛壁纸 · 磨砂玻璃侧栏",
\t\t\t\tkind: "theme",
\t\t\t\twallpaper: WALLPAPER_ZELDA,
\t\t\t\tfont: FONT_ZELDA,
\t\t\t\tpalette: PALETTE_ZELDA,
\t\t\t\tdialog: DIALOG_ZELDA,
\t\t\t\t/* 浅色下压暗壁纸 12% 并略提饱和 → 不再"发白刺眼" */
\t\t\t\twallpaperFilter: {{ light: "brightness(0.88) saturate(1.08) contrast(1.03)", dark: "none" }},
\t\t\t\taccentGradient: {{ light: "linear-gradient(92deg, #0FA8B8 0%, #4FC7D6 45%, #D9A02B 100%)", dark: "linear-gradient(92deg, #35D0DF 0%, #7FE6F0 45%, #E8B44A 100%)" }},
\t\t\t\taccentColor: {{ light: "#0FA8B8", dark: "#35D0DF" }},
\t\t\t\tbadgeGradient: {{ light: "linear-gradient(92deg, #14A3B4 0%, #4FD0DE 100%)", dark: "linear-gradient(92deg, #0E8A99 0%, #35D0DF 100%)" }},
\t\t\t\tbadgeSolid: {{ light: "#3CC3D2", dark: "#1FB6C6" }},
\t\t\t\tbadgePillBg: {{ light: "#0A6C79", dark: "#0B6E7C" }},
\t\t\t\tbadgeText: "#FFFFFF",
\t\t\t\tbadgeDecor: false,
\t\t\t\tblur: BLUR,
\t\t\t\tsidebar: {{ light: "rgba(234, 246, 249, 0.32)", dark: "rgba(8, 28, 38, 0.36)" }},
\t\t\t\tsidebarBlur: "blur(24px) saturate(1.35)"
\t\t\t}}
\t\t];
\t\tlet ACTIVE = null;
\t\tlet decoTick = 0;
\t\tfunction readSkinId() {{
\t\t\ttry {{ return localStorage.getItem(STORAGE_KEY) || DEFAULT_SKIN; }} catch (error) {{ return DEFAULT_SKIN; }}
\t\t}}
\t\tfunction writeSkinId(id) {{
\t\t\ttry {{ localStorage.setItem(STORAGE_KEY, id); }} catch (error) {{ /* 忽略 */ }}
\t\t}}
\t\tfunction currentSkin() {{
\t\t\tconst id = readSkinId();
\t\t\tfor (let i = 0; i < SKINS.length; i += 1) if (SKINS[i].id === id) return SKINS[i];
\t\t\treturn SKINS[0];
\t\t}}

\t\tconst inject = ["slots"];

\t\tfunction isDark(doc) {{
\t\t\treturn doc.body.hasAttribute("data-ds-dark-theme")
\t\t\t\t|| doc.documentElement.hasAttribute("data-ds-dark-theme");
\t\t}}

\t\tfunction setTokens(el, map) {{
\t\t\tfor (const key in map) el.style.setProperty(key, map[key], "important");
\t\t}}

\t\t/** 真正的弹窗：role/aria-modal 或严格关键词。 */
\t\tfunction isDialog(el) {{
\t\t\tlet node = el;
\t\t\tfor (let d = 0; node && d < 4; d += 1, node = node.parentElement) {{
\t\t\t\ttry {{
\t\t\t\t\tconst role = node.getAttribute && node.getAttribute("role");
\t\t\t\t\tif (role === "dialog" || role === "alertdialog") return true;
\t\t\t\t\tif (node.getAttribute && node.getAttribute("aria-modal") === "true") return true;
\t\t\t\t\tif (DIALOG_HINT.test(String(node.className || ""))) return true;
\t\t\t\t}} catch (error) {{ /* 忽略 */ }}
\t\t\t}}
\t\t\treturn false;
\t\t}}

\t\tfunction isOverlay(el) {{
\t\t\tlet node = el;
\t\t\tfor (let d = 0; node && d < 6; d += 1, node = node.parentElement) {{
\t\t\t\ttry {{
\t\t\t\t\tif (OVERLAY_HINT.test(String(node.className || ""))) return true;
\t\t\t\t\tconst role = node.getAttribute && node.getAttribute("role");
\t\t\t\t\tif (role === "dialog" || role === "alertdialog" || role === "menu"
\t\t\t\t\t\t|| role === "listbox" || role === "tooltip") return true;
\t\t\t\t\tif (node.getAttribute && node.getAttribute("aria-modal") === "true") return true;
\t\t\t\t}} catch (error) {{ /* 忽略 */ }}
\t\t\t}}
\t\t\treturn false;
\t\t}}

\t\tfunction glazed(el) {{
\t\t\ttry {{
\t\t\t\tel.style.setProperty("backdrop-filter", (ACTIVE || currentSkin()).blur || "none", "important");
\t\t\t\tel.style.setProperty("-webkit-backdrop-filter", (ACTIVE || currentSkin()).blur || "none", "important");
\t\t\t}} catch (error) {{ /* 忽略 */ }}
\t\t}}

\t\tfunction ensureLayer(doc) {{
\t\t\tconst skin1 = ACTIVE || currentSkin();
\t\t\tif (!skin1.wallpaper) return false;
\t\t\tconst existing = doc.getElementById(LAYER_ID);
\t\t\tif (existing) {{
\t\t\t\tif (doc.body.firstElementChild !== existing) doc.body.prepend(existing);
\t\t\t\treturn false;
\t\t\t}}
\t\t\tconst layer = doc.createElement("div");
\t\t\tlayer.id = LAYER_ID;
\t\t\tlayer.setAttribute("aria-hidden", "true");
\t\t\tlayer.style.cssText = "position:fixed;top:0;left:0;right:0;bottom:0;z-index:0;pointer-events:none;overflow:hidden";
\t\t\tconst img = doc.createElement("img");
\t\t\timg.alt = "";
\t\t\timg.src = skin1.wallpaper;
\t\t\timg.style.cssText = "width:100%;height:100%;object-fit:cover;display:block";
\t\t\tlayer.appendChild(img);
\t\t\tdoc.body.prepend(layer);
\t\t\treturn true;
\t\t}}

\t\t/* ===== 皮肤装饰：品牌区 & 选中会话（渐变色）===== */
\t\tfunction paintGradient(el, grad) {{
\t\t\ttry {{
\t\t\t\tel.style.setProperty("background-image", grad, "important");
\t\t\t\tel.style.setProperty("background-clip", "text", "important");
\t\t\t\tel.style.setProperty("-webkit-background-clip", "text", "important");
\t\t\t\tel.style.setProperty("color", "transparent", "important");
\t\t\t\tel.style.setProperty("-webkit-text-fill-color", "transparent", "important");
\t\t\t\tel.style.setProperty("text-shadow", "none", "important");
\t\t\t}} catch (error) {{ /* 忽略 */ }}
\t\t}}

\t\t/** 左上角品牌：字标渐变、HARNESS 徽章、SVG 图标换成主题色。 */
\t\t/* 品牌区原生配色（取自应用原始主题 token，用于"恢复原生徽章"） */
\t\tconst NATIVE_LIGHT = {{
\t\t\t"--dsw-alias-bg-base": "rgb(255, 255, 255)",
\t\t\t"--dsw-alias-bg-layer-1": "rgb(255, 255, 255)",
\t\t\t"--dsw-alias-bg-layer-2": "rgb(255, 255, 255)",
\t\t\t"--dsw-alias-bg-layer-3": "rgb(255, 255, 255)",
\t\t\t"--dsw-alias-bg-mask-1": "rgba(0, 0, 0, .24)",
\t\t\t"--dsw-alias-bg-mask-2": "rgba(0, 0, 0, .12)",
\t\t\t"--dsw-alias-bg-mask-3": "rgba(0, 0, 0, .48)",
\t\t\t"--dsw-alias-bg-module-platform": "rgb(245, 246, 247)",
\t\t\t"--dsw-alias-bg-multi-select": "rgb(245, 246, 247)",
\t\t\t"--dsw-alias-bg-overlay": "rgb(233, 236, 242)",
\t\t\t"--dsw-alias-bg-skeleton": "rgba(0, 0, 0, .04)",
\t\t\t"--dsw-alias-border-l1": "rgba(0, 0, 0, .04)",
\t\t\t"--dsw-alias-border-l2": "rgba(0, 0, 0, .1)",
\t\t\t"--dsw-alias-border-l3": "rgba(0, 0, 0, .12)",
\t\t\t"--dsw-alias-border-l4": "rgba(0, 0, 0, .16)",
\t\t\t"--dsw-alias-brand-primary": "rgb(15, 17, 21)",
\t\t\t"--dsw-alias-brand-primary-invert": "rgb(15, 17, 21)",
\t\t\t"--dsw-alias-brand-text": "rgb(15, 17, 21)",
\t\t\t"--dsw-alias-button-primary-dimmed": "rgb(235, 238, 242)",
\t\t\t"--dsw-alias-button-primary-fill": "var(--dsw-alias-brand-primary)",
\t\t\t"--dsw-alias-button-primary-hover": "rgb(67, 69, 74)",
\t\t\t"--dsw-alias-interactive-bg-active": "rgba(38, 49, 72, .1)",
\t\t\t"--dsw-alias-interactive-bg-hover": "rgba(38, 49, 72, .06)",
\t\t\t"--dsw-alias-interactive-bg-hover-accent": "rgba(38, 49, 72, .14)",
\t\t\t"--dsw-alias-interactive-bg-hover-solid": "rgb(241, 243, 245)",
\t\t\t"--dsw-alias-label-caption": "rgb(173, 178, 184)",
\t\t\t"--dsw-alias-label-deep-diving": "color-mix(in srgb, var(--dsw-static-deepseek-500) 70%, var(--dsw-static-blue-950))",
\t\t\t"--dsw-alias-label-dimmed": "rgb(225, 229, 238)",
\t\t\t"--dsw-alias-label-primary": "rgb(15, 17, 21)",
\t\t\t"--dsw-alias-label-primary-bluish": "rgb(14, 48, 116)",
\t\t\t"--dsw-alias-label-primary-dimmed": "rgb(21, 21, 23)",
\t\t\t"--dsw-alias-label-primary-foreground": "rgb(255, 255, 255)",
\t\t\t"--dsw-alias-label-primary-inverted": "rgb(255, 255, 255)",
\t\t\t"--dsw-alias-label-secondary": "rgb(97, 102, 107)",
\t\t\t"--dsw-alias-label-tertiary": "rgb(129, 133, 140)",
\t\t\t"--dsw-alias-scrollbar-bg-l1": "rgb(229, 229, 229)",
\t\t\t"--dsw-alias-scrollbar-bg-l2": "rgb(229, 229, 229)",
\t\t\t"--dsw-alias-scrollbar-hover-l1": "rgb(212, 212, 212)",
\t\t\t"--dsw-alias-scrollbar-hover-l2": "rgb(212, 212, 212)",
\t\t\t"--dsw-alias-state-business-primary": "rgb(65, 118, 230)",
\t\t\t"--dsw-alias-state-business-tertiary": "rgb(228, 237, 253)",
\t\t\t"--dsw-elevation-stroke-color": "var(--dsw-alias-border-l4)",
\t\t\t"--dsw-shadow-lv1": "0 2px 4px 0 rgba(0, 0, 0, .05)",
\t\t\t"--dsw-shadow-lv1-blur": "0 4px 12px 0 rgba(0, 0, 0, .02)",
\t\t\t"--dsw-shadow-lv2": "0 4px 12px 0 rgba(0, 0, 0, .02), 0 2px 8px 0 rgba(0, 0, 0, .04)",
\t\t\t"--dsw-shadow-lv3": "0 0 1px 0 rgba(0, 0, 0, .2), 0 0 4px 0 rgba(0, 0, 0, .02), 0 12px 32px 0 rgba(0, 0, 0, .08)",
\t\t\t"--dsw-specific-input-major": "rgb(255, 255, 255)",
\t\t\t"--dsw-specific-sidebar-fill": "rgb(249, 250, 251)",
\t\t}};
\t\tconst NATIVE_DARK = {{
\t\t\t"--dsw-alias-bg-base": "rgb(21, 21, 23)",
\t\t\t"--dsw-alias-bg-layer-1": "rgb(35, 35, 36)",
\t\t\t"--dsw-alias-bg-layer-2": "rgb(44, 44, 46)",
\t\t\t"--dsw-alias-bg-layer-3": "rgb(53, 54, 56)",
\t\t\t"--dsw-alias-bg-mask-1": "rgba(0, 0, 0, .5)",
\t\t\t"--dsw-alias-bg-mask-2": "rgba(0, 0, 0, .2)",
\t\t\t"--dsw-alias-bg-mask-3": "rgba(0, 0, 0, .48)",
\t\t\t"--dsw-alias-bg-module-platform": "rgb(53, 54, 56)",
\t\t\t"--dsw-alias-bg-multi-select": "rgb(33, 33, 35)",
\t\t\t"--dsw-alias-bg-overlay": "rgb(97, 102, 107)",
\t\t\t"--dsw-alias-bg-skeleton": "rgba(255, 255, 255, .08)",
\t\t\t"--dsw-alias-border-l1": "rgba(255, 255, 255, .06)",
\t\t\t"--dsw-alias-border-l2": "rgba(255, 255, 255, .12)",
\t\t\t"--dsw-alias-border-l3": "rgba(255, 255, 255, .16)",
\t\t\t"--dsw-alias-border-l4": "rgba(255, 255, 255, .2)",
\t\t\t"--dsw-alias-brand-primary": "rgb(249, 250, 251)",
\t\t\t"--dsw-alias-brand-primary-invert": "rgb(249, 250, 251)",
\t\t\t"--dsw-alias-brand-text": "rgb(249, 250, 251)",
\t\t\t"--dsw-alias-button-primary-dimmed": "rgb(67, 69, 74)",
\t\t\t"--dsw-alias-button-primary-fill": "var(--dsw-alias-brand-primary)",
\t\t\t"--dsw-alias-button-primary-hover": "rgb(235, 238, 242)",
\t\t\t"--dsw-alias-interactive-bg-active": "rgba(255, 255, 255, .14)",
\t\t\t"--dsw-alias-interactive-bg-hover": "rgba(255, 255, 255, .08)",
\t\t\t"--dsw-alias-interactive-bg-hover-accent": "rgba(255, 255, 255, .24)",
\t\t\t"--dsw-alias-interactive-bg-hover-solid": "rgb(53, 54, 56)",
\t\t\t"--dsw-alias-label-caption": "rgb(129, 133, 140)",
\t\t\t"--dsw-alias-label-deep-diving": "color-mix(in srgb, var(--dsw-static-deepseek-450) 55%, var(--dsw-static-neutral-bluish-400))",
\t\t\t"--dsw-alias-label-dimmed": "rgb(67, 69, 74)",
\t\t\t"--dsw-alias-label-primary": "rgb(249, 250, 251)",
\t\t\t"--dsw-alias-label-primary-bluish": "rgb(249, 250, 251)",
\t\t\t"--dsw-alias-label-primary-dimmed": "rgb(235, 238, 242)",
\t\t\t"--dsw-alias-label-primary-foreground": "rgb(15, 17, 21)",
\t\t\t"--dsw-alias-label-primary-inverted": "rgb(53, 54, 56)",
\t\t\t"--dsw-alias-label-secondary": "rgb(207, 211, 214)",
\t\t\t"--dsw-alias-label-tertiary": "rgb(173, 178, 184)",
\t\t\t"--dsw-alias-scrollbar-bg-l1": "rgb(60, 60, 61)",
\t\t\t"--dsw-alias-scrollbar-bg-l2": "rgb(84, 85, 87)",
\t\t\t"--dsw-alias-scrollbar-hover-l1": "rgb(84, 85, 87)",
\t\t\t"--dsw-alias-scrollbar-hover-l2": "rgb(101, 103, 107)",
\t\t\t"--dsw-alias-state-business-primary": "rgb(122, 170, 255)",
\t\t\t"--dsw-alias-state-business-tertiary": "rgb(52, 65, 91)",
\t\t\t"--dsw-specific-input-major": "rgb(44, 44, 46)",
\t\t\t"--dsw-specific-sidebar-fill": "rgb(27, 27, 28)",
\t\t}};

\t\t/** 品牌区：完全恢复原生（不改结构、不染色、不注入），只把该区域的 token 还原为应用原始值。 */
\t\tfunction decorateBrand(doc, skin, dark) {{
\t\t\tconst scope = doc.querySelector('[class*="_sidebarCol"],[class*="sidebar"],[class*="Sidebar"]') || doc.body;
\t\t\tconst native = dark ? NATIVE_DARK : NATIVE_LIGHT;
\t\t\tlet hits = 0;
\t\t\t/* 按形状染色：同一 SVG 内"最大形状=胶囊底"，只染它左侧的形状（= deepseek 字形），
\t\t\t   胶囊及其内部（HARNESS 字形）保持原生 → 不会再出现"同色隐形"。 */
\t\t\tconst accentC = dark ? skin.accentColor.dark : skin.accentColor.light;
\t\t\tconst brandSvgs = scope.querySelectorAll("svg");
\t\t\tfor (let v = 0; v < brandSvgs.length; v += 1) {{
\t\t\t\tconst svg = brandSvgs[v];
\t\t\t\tlet host = svg.parentElement, kind = "";
\t\t\t\tfor (let d = 0; host && d < 5; d += 1, host = host.parentElement) {{
\t\t\t\t\tconst cls = String(host.className || "");
\t\t\t\t\tif (/brandName|wordmark/i.test(cls)) {{ kind = "name"; break; }}
\t\t\t\t\tif (/brandMark|brandLogo/i.test(cls)) {{ kind = "mark"; break; }}
\t\t\t\t}}
\t\t\t\tif (kind === "mark") {{
\t\t\t\t\t/* 鲸鱼图标是独立 SVG：整体染主题色 */
\t\t\t\t\tsvg.style.setProperty("color", accentC, "important");
\t\t\t\t\tconst mk = svg.querySelectorAll("path,circle,rect,polygon,ellipse,use");
\t\t\t\t\tfor (let p = 0; p < mk.length; p += 1) {{
\t\t\t\t\t\ttry {{
\t\t\t\t\t\t\tconst cs = doc.defaultView.getComputedStyle(mk[p]);
\t\t\t\t\t\t\tif (cs && cs.fill && cs.fill !== "none") mk[p].style.setProperty("fill", "currentColor", "important");
\t\t\t\t\t\t}} catch (error) {{ /* 忽略 */ }}
\t\t\t\t\t}}
\t\t\t\t\thits += 1;
\t\t\t\t\tcontinue;
\t\t\t\t}}
\t\t\t\tif (kind !== "name") continue;
\t\t\t\t/* 字标 SVG（可能同时含徽章）：先量所有形状 */
\t\t\t\tconst shp = svg.querySelectorAll("path,rect,circle,ellipse,polygon");
\t\t\t\tlet pill = null, pillArea = -1;
\t\t\t\tconst boxes = [];
\t\t\t\tfor (let k = 0; k < shp.length; k += 1) {{
\t\t\t\t\tlet bb = null;
\t\t\t\t\ttry {{ bb = shp[k].getBBox ? shp[k].getBBox() : null; }} catch (error) {{ bb = null; }}
\t\t\t\t\tboxes.push(bb);
\t\t\t\t\tif (bb && bb.width && bb.height) {{
\t\t\t\t\t\tconst a = bb.width * bb.height;
\t\t\t\t\t\tif (a > pillArea) {{ pillArea = a; pill = bb; }}
\t\t\t\t\t}}
\t\t\t\t}}
\t\t\t\t/* 记录"最大形状"的下标（= 胶囊底） */
\t\t\t\tlet pillIdx = -1, bestA = -1;
\t\t\t\tfor (let k = 0; k < boxes.length; k += 1) {{
\t\t\t\t\tconst bb = boxes[k];
\t\t\t\t\tif (!bb || !bb.width || !bb.height) continue;
\t\t\t\t\tconst a = bb.width * bb.height;
\t\t\t\t\tif (a > bestA) {{ bestA = a; pillIdx = k; }}
\t\t\t\t}}
\t\t\t\tconst pillBg = skin.badgePillBg ? (dark ? skin.badgePillBg.dark : skin.badgePillBg.light) : "#5E3CA8";
\t\t\t\tconst pillText = skin.badgeText || "#FFFFFF";
\t\t\t\tlet tinted = 0;
\t\t\t\tfor (let k = 0; k < shp.length; k += 1) {{
\t\t\t\t\tconst bb = boxes[k];
\t\t\t\t\tif (!bb || !bb.width || !bb.height) continue;
\t\t\t\t\ttry {{
\t\t\t\t\t\tif (k === pillIdx) {{
\t\t\t\t\t\t\t/* 胶囊底 → 深紫 */
\t\t\t\t\t\t\tshp[k].style.setProperty("fill", pillBg, "important");
\t\t\t\t\t\t\ttinted += 1;
\t\t\t\t\t\t}} else if (pill && bb.x >= (pill.x - 0.5)) {{
\t\t\t\t\t\t\t/* 胶囊内部/右侧的小形状 → HARNESS 字形 → 白 */
\t\t\t\t\t\t\tshp[k].style.setProperty("fill", pillText, "important");
\t\t\t\t\t\t\ttinted += 1;
\t\t\t\t\t\t}} else if (!pill || (bb.x + bb.width) <= (pill.x - 0.5)) {{
\t\t\t\t\t\t\t/* 完全位于胶囊左侧 → deepseek 字形 → 主题色 */
\t\t\t\t\t\t\tshp[k].style.setProperty("fill", accentC, "important");
\t\t\t\t\t\t\ttinted += 1;
\t\t\t\t\t\t}}
\t\t\t\t\t}} catch (error) {{ /* 忽略 */ }}
\t\t\t\t}}
\t\t\t\tif (decoTick <= 3) console.log("[dsh-skin] 字标形状染色 | 形状 =", shp.length, "| 已染 =", tinted, "| 胶囊底面积 =", Math.round(pillArea));
\t\t\t\thits += tinted;
\t\t\t}}
\t\t\tconst rows = scope.querySelectorAll('[class*="brand_"],[class*="brandBadge"],[class*="brandTag"],[class*="Badge"]');
\t\t\tfor (let i = 0; i < rows.length; i += 1) {{
\t\t\t\tconst row = rows[i];
\t\t\t\tlet r; try {{ r = row.getBoundingClientRect(); }} catch (error) {{ continue; }}
\t\t\t\tif (!r.width || !r.height || r.height > 60) continue;
\t\t\t\t/* ① 整行先套原生 token → 徽章保持原生外观 */
\t\t\t\tsetTokens(row, native);
\t\t\t\tif (decoTick <= 3) console.log("[dsh-skin] 品牌行：徽章=原生，鲸鱼/字标=主题色 | w =", Math.round(r.width), "h =", Math.round(r.height));
\t\t\t\thits += 1;
\t\t\t}}
\t\t\treturn hits;
\t\t}}

\t\t/** 侧栏"选中/当前"会话：文字上渐变色（只涂文字叶子，避免吃掉胶囊底色）。 */
\t\tfunction decorateSelected(doc, skin, dark) {{
\t\t\tconst grad = dark ? skin.accentGradient.dark : skin.accentGradient.light;
\t\t\tconst scopes = doc.querySelectorAll('[class*="_sidebarCol"],[class*="sidebar"]');
\t\t\tconst roots = scopes.length ? scopes : [doc.body];
\t\t\tlet hits = 0;
\t\t\tfor (let i = 0; i < roots.length; i += 1) {{
\t\t\t\tconst items = roots[i].querySelectorAll('[class*="_selected"],[class*="_active"],[class*="Active"],[aria-current="true"],[aria-selected="true"]');
\t\t\t\tfor (let j = 0; j < items.length; j += 1) {{
\t\t\t\t\tconst it = items[j];
\t\t\t\t\tif (!String(it.textContent || "").trim()) continue;
\t\t\t\t\tconst leaves = it.querySelectorAll("span,p,a,button,div,strong,em");
\t\t\t\t\tlet painted = 0;
\t\t\t\t\tfor (let k = 0; k < leaves.length; k += 1) {{
\t\t\t\t\t\tconst lf = leaves[k];
\t\t\t\t\t\tif (lf.children.length || !String(lf.textContent || "").trim()) continue;
\t\t\t\t\t\ttry {{
\t\t\t\t\t\t\tconst cs = doc.defaultView.getComputedStyle(lf);
\t\t\t\t\t\t\tif (cs && cs.backgroundColor && cs.backgroundColor !== "rgba(0, 0, 0, 0)" && cs.backgroundColor !== "transparent") continue;
\t\t\t\t\t\t}} catch (error) {{ /* 忽略 */ }}
\t\t\t\t\t\tpaintGradient(lf, grad);
\t\t\t\t\t\tpainted += 1;
\t\t\t\t\t}}
\t\t\t\t\tif (!painted && it.children.length === 0) {{ paintGradient(it, grad); painted = 1; }}
\t\t\t\t\thits += painted;
\t\t\t\t}}
\t\t\t}}
\t\t\treturn hits;
\t\t}}

\t\tfunction forceDoc(doc) {{
\t\t\tif (!doc || !doc.body) return 0;
\t\t\tconst dark = isDark(doc);
\t\t\tconst skin0 = ACTIVE || currentSkin();
\t\t\tif (skin0.kind !== "theme") return 0;
\t\t\tconst pal = dark ? skin0.palette.dark : skin0.palette.light;
\t\t\tconst dia = dark ? skin0.dialog.dark : skin0.dialog.light;

\t\t\t/* 1) 全站调色板（主题化一切，含弹窗） */
\t\t\tsetTokens(doc.body, pal);
\t\t\t/* 侧边栏文字加轻微投影（壁纸再亮也不糊字） */
\t\t\tdoc.body.style.setProperty("text-shadow", dark ? "0 1px 2px rgba(0, 0, 0, 0.45)" : "0 1px 1px rgba(255, 255, 255, 0.55)", "important");
\t\t\tdoc.body.style.setProperty("font-family", skin0.font, "important");
\t\t\tdoc.documentElement.style.setProperty("background-color", "transparent", "important");
\t\t\tdoc.body.style.setProperty("background-color", "transparent", "important");
\t\t\t/* 关键：清掉应用自带的渐变背景，否则它会像蒙版一样盖在壁纸上 */
\t\t\tdoc.documentElement.style.setProperty("background-image", "none", "important");
\t\t\tdoc.body.style.setProperty("background-image", "none", "important");
\t\t\tconst appRoot = doc.getElementById("root");
\t\t\tif (appRoot) appRoot.style.setProperty("background-color", "transparent", "important");

\t\t\t/* 1.5) 品牌区 & 选中会话：渐变色（节流执行，避免每次全量遍历）*/
\t\t\tdecoTick += 1;
\t\t\tif (decoTick % 3 === 1) {{
\t\t\t\ttry {{
\t\t\t\t\tconst bh = decorateBrand(doc, skin0, dark);
\t\t\t\t\tconst sh = decorateSelected(doc, skin0, dark);
\t\t\t\t\tif (decoTick <= 4) console.log("[dsh-skin] 装饰 | 品牌元素 =", bh, "| 选中会话 =", sh);
\t\t\t\t}} catch (error) {{ console.error("[dsh-skin] 装饰失败:", error); }}
\t\t\t}}

\t\t\t/* 2) 壁纸层（浅色下压暗+提色，避免高调壁纸把界面冲白）*/
\t\t\tensureLayer(doc);
\t\t\ttry {{
\t\t\t\tconst lay = doc.getElementById(LAYER_ID);
\t\t\t\tlet fimg = null;
\t\t\t\tif (lay && lay.children) {{
\t\t\t\t\tfor (let ci = 0; ci < lay.children.length; ci += 1) {{
\t\t\t\t\t\tif (String(lay.children[ci].tagName).toUpperCase() === "IMG") {{ fimg = lay.children[ci]; break; }}
\t\t\t\t\t}}
\t\t\t\t}}
\t\t\t\tif (fimg && skin0.wallpaperFilter) {{
\t\t\t\t\tfimg.style.filter = dark ? skin0.wallpaperFilter.dark : skin0.wallpaperFilter.light;
\t\t\t\t}}
\t\t\t}} catch (error) {{ /* 忽略 */ }}

\t\t\t/* 3) 外壳：玻璃拟态 */
\t\t\tlet n = 0;
\t\t\tlet dialogs = 0;
\t\t\tlet skipped = 0;
\t\t\tdoc.querySelectorAll(SHELL_SELECTOR).forEach((el) => {{
\t\t\t\tconst cls = String(el.className || "");
\t\t\t\tif (/_sidebarCol|_rightbarCol/.test(cls)) {{
\t\t\t\t\t/* 侧边栏 / 右栏：毛玻璃（模糊背后壁纸）+ 加厚底色 → 文字清晰 */
\t\t\t\t\tel.style.setProperty("background-color", dark ? skin0.sidebar.dark : skin0.sidebar.light, "important");
\t\t\t\t\tif (skin0.sidebarBlur) {{
\t\t\t\t\t\tel.style.setProperty("backdrop-filter", skin0.sidebarBlur, "important");
\t\t\t\t\t\tel.style.setProperty("-webkit-backdrop-filter", skin0.sidebarBlur, "important");
\t\t\t\t\t}}
\t\t\t\t}} else {{
\t\t\t\t\t/* 中间区/框架：保持通透，让壁纸清楚可见 */
\t\t\t\t\tel.style.setProperty("background-color", dark ? skin0.palette.dark["--dsw-alias-bg-base"] : skin0.palette.light["--dsw-alias-bg-base"], "important");
\t\t\t\t\tif (skin0.blur && skin0.blur !== "none") {{
\t\t\t\t\t\tel.style.setProperty("backdrop-filter", skin0.blur, "important");
\t\t\t\t\t\tel.style.setProperty("-webkit-backdrop-filter", skin0.blur, "important");
\t\t\t\t\t}}
\t\t\t\t}}
\t\t\t\tn += 1;
\t\t\t}});

\t\t\t/* 3.5) 弹窗（含 portal 到 body 的设置面板）：给高不透明表面，保证内容可读 */
\t\t\ttry {{
\t\t\t\tconst dlgNodes = doc.querySelectorAll('[role="dialog"],[aria-modal="true"],[class*="dialog"],[class*="Dialog"],[class*="modal"],[class*="Modal"],[class*="drawer"],[class*="Drawer"],[class*="sheet"],[class*="Sheet"],[class*="popover"]');
\t\t\t\tfor (let di = 0; di < dlgNodes.length; di += 1) {{
\t\t\t\t\tconst dn = dlgNodes[di];
\t\t\t\t\tif (dn === doc.body || dn === doc.documentElement) continue;
\t\t\t\t\tsetTokens(dn, dia);
\t\t\t\t\tdialogs += 1;
\t\t\t\t}}
\t\t\t}} catch (error) {{ /* 忽略 */ }}

\t\t\t/* 4) 大块不透明面板：透明化 + 玻璃；弹窗则主题化但不透明 */
\t\t\ttry {{
\t\t\t\tconst view = doc.defaultView;
\t\t\t\tconst vw = doc.documentElement.clientWidth || 1280;
\t\t\t\tconst vh = doc.documentElement.clientHeight || 800;
\t\t\t\tconst nodes = doc.querySelectorAll("#root *");
\t\t\t\tfor (let i = 0; i < nodes.length; i += 1) {{
\t\t\t\t\tconst el = nodes[i];
\t\t\t\t\tconst rect = el.getBoundingClientRect();
\t\t\t\t\tif (rect.width * rect.height < vw * vh * 0.16) continue;
\t\t\t\t\tif (isDialog(el)) {{
\t\t\t\t\t\tsetTokens(el, dia);
\t\t\t\t\t\tdialogs += 1;
\t\t\t\t\t\tcontinue;
\t\t\t\t\t}}
\t\t\t\t\t/* 宽松命中不再跳过：继续按"大块不透明→半透明"处理，保证壁纸能透出来 */
\t\t\t\t\tconst cs = view.getComputedStyle(el);
\t\t\t\t\tconst mm = (cs.backgroundColor || "").match(/rgba?\\(([^)]+)\\)/);
\t\t\t\t\tif (!mm) continue;
\t\t\t\t\tconst parts = mm[1].split(",");
\t\t\t\t\tconst alpha = parts.length < 4 ? 1 : parseFloat(parts[3]);
\t\t\t\t\tif (alpha < 0.99) continue;
\t\t\t\t\tel.style.setProperty("background-color", pal["--dsw-alias-bg-layer-1"], "important");
\t\t\t\t\tn += 1;
\t\t\t\t}}
\t\t\t}} catch (error) {{ /* 忽略 */ }}

\t\t\treturn n;
\t\t}}

\t\tfunction allDocs(win, acc, depth) {{
\t\t\twin = win || window; acc = acc || []; depth = depth || 0;
\t\t\ttry {{
\t\t\t\tif (acc.indexOf(win.document) === -1) acc.push(win.document);
\t\t\t\tif (depth >= 3) return acc;
\t\t\t\tconst frames = win.frames || [];
\t\t\t\tfor (let i = 0; i < frames.length; i += 1) {{
\t\t\t\t\ttry {{ allDocs(frames[i], acc, depth + 1); }} catch (e) {{ /* 跨域 */ }}
\t\t\t\t}}
\t\t\t}} catch (e) {{ /* 忽略 */ }}
\t\t\treturn acc;
\t\t}}

\t\tfunction forceAll(verbose) {{
\t\t\tlet total = 0;
\t\t\tconst docs = allDocs();
\t\t\tfor (let i = 0; i < docs.length; i += 1) {{
\t\t\t\ttry {{ total += forceDoc(docs[i]); }} catch (error) {{ console.error("[dsh-skin] forceDoc failed:", error); }}
\t\t\t}}
\t\t\tif (verbose) console.log("[dsh-anime-theme] forceAll | docs =", docs.length,
\t\t\t\t"| 玻璃化元素 =", total, "| 弹窗 =", (typeof dialogsLast !== "undefined" ? dialogsLast : ""), "| 主题 =", isDark(document) ? "dark" : "light",
\t\t\t\t"| 字体 =", getComputedStyle(document.body).fontFamily.slice(0, 24));
\t\t\treturn total;
\t\t}}

\t\t/** 设置 →「皮肤设置」分区的界面。 */
\t\tfunction SkinSection() {{
\t\t\tconst state = React.useState(readSkinId());
\t\t\tconst active = state[0];
\t\t\tconst setActive = state[1];
\t\t\tfunction pick(id) {{
\t\t\t\tif (id === active) return;
\t\t\t\twriteSkinId(id);
\t\t\t\tsetActive(id);
\t\t\t\twindow.setTimeout(function () {{ try {{ location.reload(); }} catch (error) {{ /* 忽略 */ }} }}, 220);
\t\t\t}}
\t\t\treturn React.createElement("div", {{ style: {{ maxWidth: "720px", padding: "4px 0" }} }},
\t\t\t\tReact.createElement("h2", {{ style: {{ margin: "0 0 6px", fontSize: "18px", fontWeight: 600, color: "var(--dsw-alias-label-primary)" }} }}, "皮肤设置"),
\t\t\t\tReact.createElement("p", {{ style: {{ margin: "0 0 16px", fontSize: "13px", lineHeight: 1.6, color: "var(--dsw-alias-label-tertiary)" }} }}, "选择一套界面皮肤，切换后页面会自动刷新。"),
\t\t\t\tReact.createElement("ul", {{ style: {{ listStyle: "none", margin: 0, padding: 0, display: "grid", gap: "10px" }} }},
\t\t\t\t\tSKINS.map(function (skin) {{
\t\t\t\t\t\tconst on = skin.id === active;
\t\t\t\t\t\treturn React.createElement("li", {{ key: skin.id }},
\t\t\t\t\t\t\tReact.createElement("button", {{
\t\t\t\t\t\t\t\ttype: "button",
\t\t\t\t\t\t\t\tonClick: function () {{ pick(skin.id); }},
\t\t\t\t\t\t\t\tstyle: {{
\t\t\t\t\t\t\t\t\twidth: "100%", textAlign: "left", cursor: "pointer", font: "inherit",
\t\t\t\t\t\t\t\t\tdisplay: "flex", alignItems: "center", gap: "12px",
\t\t\t\t\t\t\t\t\tpadding: "14px 16px", borderRadius: "16px",
\t\t\t\t\t\t\t\t\tborder: on ? "1.5px solid var(--dsw-alias-brand-primary)" : "1px solid var(--dsw-alias-border-l3)",
\t\t\t\t\t\t\t\t\tbackground: on ? "var(--dsw-alias-bg-layer-2)" : "var(--dsw-alias-bg-layer-1)",
\t\t\t\t\t\t\t\t\tcolor: "var(--dsw-alias-label-primary)"
\t\t\t\t\t\t\t\t}}
\t\t\t\t\t\t\t}},
\t\t\t\t\t\t\tReact.createElement("span", {{ style: {{ flex: "1 1 auto", minWidth: 0, display: "flex", flexDirection: "column", gap: "4px" }} }},
\t\t\t\t\t\t\t\tReact.createElement("span", {{ style: {{ fontSize: "15px", fontWeight: 600 }} }}, skin.name),
\t\t\t\t\t\t\t\tReact.createElement("span", {{ style: {{ fontSize: "12.5px", color: "var(--dsw-alias-label-tertiary)" }} }}, skin.desc)
\t\t\t\t\t\t\t),
\t\t\t\t\t\t\ton ? React.createElement("span", {{ style: {{ flex: "none", fontSize: "12px", padding: "2px 10px", borderRadius: "999px", background: "var(--dsw-alias-brand-primary)", color: "#ffffff" }} }}, "使用中") : null
\t\t\t\t\t\t)
\t\t\t\t\t);
\t\t\t\t}})
\t\t\t));
\t\t}}

\t\tfunction apply(ctx) {{
\t\t\tACTIVE = currentSkin();
\t\t\tconsole.log("[dsh-skin] active skin =", ACTIVE.id, "|", ACTIVE.name);
\t\t\tif (ACTIVE.kind === "theme") {{
\t\t\t\tforceAll(true);
\t\t\t\twindow.setInterval(function () {{ forceAll(false); }}, 800);
\t\t\t\twindow.setTimeout(function () {{ forceAll(true); }}, 2500);
\t\t\t\tconsole.log("[dsh-skin] 皮肤已挂载:", ACTIVE.name);
\t\t\t}} else {{
\t\t\t\tconsole.log("[dsh-skin] 原始皮肤：不施加任何自定义");
\t\t\t}}
\t\t\ttry {{
\t\t\t\tctx.slots.inject("settings.section", function () {{
\t\t\t\t\treturn ctx.slots.register({{ name: "settings.section", id: "skins", order: 40, label: function () {{ return "皮肤设置"; }} }}, SkinSection);
\t\t\t\t}});
\t\t\t\tconsole.log("[dsh-skin] 已注册「皮肤设置」分区");
\t\t\t}} catch (error) {{
\t\t\t\tconsole.error("[dsh-skin] 注册设置分区失败", error);
\t\t\t}}
\t\t}}

\t\texports.apply = apply;
\t\texports.inject = inject;
\t\treturn module.exports;
\t}}
}});
"""
open(f"{PLUGIN}/lib/client.js", "w").write(client_js)
print(f"插件已构建: {PLUGIN}/  (client.js {len(client_js)/1024:.0f} KB)")
print(f"  浅色 token: {len(PALETTE['light'])} 个 | 深色 token: {len(PALETTE['dark'])} 个 | 弹窗 token: {len(DIALOG['light'])} 个")
