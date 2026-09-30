# DSH Anime Skins · 二次元皮肤

为 **DeepSeek Harness（DSH）桌面 / Web 客户端**做的皮肤系统插件：壁纸 + 配色 + 字体 + 毛玻璃侧栏，并在「设置」里提供一个 **皮肤设置** 菜单，可随时切换、随时还原。

![樱花黄昏](assets/preview-sakura.jpg)

![天空之岛](assets/preview-zelda.jpg)

---

## ✨ 特性

| 能力 | 说明 |
|---|---|
| 🎨 **多套皮肤** | 内置「二次元 · 樱花黄昏」「天空之岛 · 塞尔达风」，外加「原始皮肤」一键还原 |
| ⚙️ **设置内切换** | 注册 `settings.section` 分区「皮肤设置」，点选即切换（自动刷新），选择持久化到 `localStorage` |
| 🖼️ **壁纸透出** | 壁纸作为独立图层铺底，面板半透明；**对话区不加模糊**（壁纸保持清晰） |
| 🧊 **磨砂玻璃侧栏** | 只对**外壳容器**施加 `backdrop-filter`，文字清晰、壁纸柔化 |
| 🌗 **明暗双主题** | 每套皮肤各有一套浅色 / 深色 token，跟随客户端外观自动切换 |
| 🪟 **弹窗保持可读** | 弹窗（含 portal 到 `body` 的）自动套用高不透明表面，不被主题透明化 |
| 🔤 **字体与品牌色** | 可配置字体栈；品牌字标（deepseek）与徽章按 SVG 形状分别上色 |
| 🧩 **零依赖** | 纯浏览器端插件，不需要宿主侧逻辑（`lib/index.js` 为空实现） |

---

## 🚀 安装

> 前提：DSH 桌面客户端（或 Web 端）已能正常启动，profile 目录形如 `~/.dsh/profiles/desktop`。

**1. 把本仓库放进 profile 的 `node_modules`**

```bash
git clone https://github.com/cloud0-long/dsh-anime-skins.git
cp -R dsh-anime-skins ~/.dsh/profiles/desktop/node_modules/dsh-anime-background
```

**2. 在 profile 的 `package.json` 里声明依赖**

```json
{
  "dependencies": {
    "dsh-anime-background": "0.5.0"
  }
}
```

**3. 在 profile 的 `cordis.patch.yml` 末尾插入插件**

```yaml
- insert:
    - id: anime-background
      name: dsh-anime-background
```

**4. 重启客户端**（或在窗口内按 <kbd>⌘R</kbd> / <kbd>Ctrl</kbd>+<kbd>R</kbd> 刷新）

**5. 打开「设置 → 皮肤设置」选择皮肤**

---

## 🎛️ 内置皮肤

| 皮肤 | 风格 | 主色 | 字体 |
|---|---|---|---|
| **原始皮肤** | DSH 默认外观 | — | 系统默认 |
| **二次元 · 樱花黄昏** | 黄昏云海壁纸 · 樱花粉 + 天青 | `#FF6FA5` / `#FF8CC8` | 圆体（圆体-简 → Hiragino Maru Gothic） |
| **天空之岛 · 塞尔达风** | 浮空岛壁纸 · 希卡青 + 古金 | `#0FA8B8` / `#35D0DF` | 苹方 PingFang SC |

---

## 🧑‍🎨 自己加一套皮肤

皮肤就是**一份数据**，编辑 `build.py` 里的 `SKINS` 数组即可：

```python
{
    "id": "my-skin",
    "name": "我的皮肤",
    "desc": "一句话描述",
    "kind": "theme",
    "wallpaper": WALLPAPER_MINE,          # base64 data URI（由构建脚本生成）
    "font": FONT_MINE,                    # 字体栈
    "palette": PALETTE_MINE,              # {"light": {...}, "dark": {...}} 设计 token
    "dialog": DIALOG_MINE,                # 弹窗用高不透明表面
    "blur": "none",                       # 外壳是否毛玻璃
    "sidebar": {"light": "...", "dark": "..."},   # 侧栏底色
    "sidebarBlur": "blur(24px) saturate(1.35)",
    "accentGradient": {"light": "...", "dark": "..."},   # 选中会话/字标渐变
    "accentColor": {"light": "...", "dark": "..."},
    "badgeSolid": {"light": "...", "dark": "..."},
    "badgePillBg": {"light": "...", "dark": "..."},
    "badgeText": "#FFFFFF",
    "wallpaperFilter": {"light": "none", "dark": "none"}
}
```

然后重新构建：

```bash
python3 -m pip install pillow      # 仅需 Pillow
python3 build.py                   # 生成 lib/client.js（含内嵌壁纸）
```

壁纸源文件放在仓库根目录，命名 `anime_bg_4k.png`（樱花）/ `zelda_bg_source.png`（天空之岛），
或直接使用 `assets/` 里已有的 JPEG —— 脚本会自动回退。

---

## 🧠 实现要点（踩过的坑）

都记在 [`docs/NOTES.md`](docs/NOTES.md)，几个关键结论：

1. **`apply()` 早于 React 挂载** —— 首次执行时 DOM 里只有引导层；必须用 `window.setInterval` 自愈式补齐。
2. **token 要写在正确的层级** —— 主题把变量声明在 `body` 上，写 `html` 上会被 `body` 覆盖。
3. **`backdrop-filter` 只给外壳** —— 给内层面板加会把**背后内容**一起糊掉（文字发虚）。
4. **深色主题下"浅底文字色"必须是深色** —— `label-primary-inverted` / `label-primary-foreground` 设错会让一批浅底元素文字隐形。
5. **品牌区是 SVG，不是文字** —— `deepseek` 与 `HARNESS` 徽章在**同一个 SVG** 内；一刀切改 `fill` 会把"底"和"字"染成同色 → 隐形。正确做法是**按形状**区分：面积最大者=胶囊底，位于其左侧者=字标，位于其内/右侧者=徽章字形。
6. **弹窗可能 portal 到 `body`** —— 识别弹窗时不能只扫 `#root`。

---

## 📄 License

[MIT](LICENSE)
