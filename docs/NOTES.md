# 实现笔记 · Implementation Notes

给 DSH 客户端写"换肤"插件时踩过的坑与结论。每条都附**现象 → 根因 → 做法**，方便后来者少走弯路。

---

## 1. 插件的生命周期：`apply()` 早于 React 挂载

- **现象**：插件里 `document.querySelectorAll('.sidebarCol')` 返回 0 个；壁纸层已插入但界面纹丝不动。
- **根因**：客户端先 `await JS({...})` 加载所有插件（`apply()` 在此执行），**之后**才 `mount()` 挂载 React 树。首次 `apply()` 时 DOM 里只有启动引导层。
- **做法**：不要依赖 `ctx.effect`（插件卸载时会清理定时器），改用 `window.setInterval(fn, 800)` 做**自愈式补齐**；每次 tick 里用 idempotent 的方式重申样式（有则更新、无则创建）。

## 2. 设计 token 的层级：写 `body`，不要写 `html`

- **现象**：在内联 `html` 上写了 `--dsw-alias-bg-base`，但面板依旧不透明。
- **根因**：主题把整套 CSS 变量声明在 `body{...}` 与 `body[data-ds-dark-theme]{...}` 上，而**元素自身的声明优先于继承**。写在 `html` 上会被 `body` 的同名声明压掉。
- **做法**：把 token 覆盖写到 `document.body`（`!important`），或写到目标子树的根元素上以限定作用域。

## 3. `backdrop-filter` 的作用域：只给外壳

- **现象**：给"所有大面积面板"加毛玻璃后，**聊天内容整片发虚**。
- **根因**：`backdrop-filter` 模糊的是**元素背后的内容**。外壳（背后是壁纸）→ 壁纸柔化、文字正常；内层面板（背后是聊天内容）→ 把内容一起糊掉。
- **做法**：只在 `_frame` / `_sidebarCol` / `_rightbarCol` 等**外壳容器**上施加；内层只改半透明底色。

## 4. 明暗两套 token 必须成对推导

- **现象**：深色主题下，`HARNESS` 徽章里的文字消失（浅底白字）。
- **根因**：`--dsw-alias-label-primary-inverted`（"浅色底上的文字色"）在**深色主题**应当为**深色**（官方值 `neutral-bluish-800`），我两个主题都写了 `#FFFFFF` → 浅底 + 白字 = 隐形。
- **做法**：覆盖 token 时按"语义"推导明暗，例如
  - `label-primary`：浅色主题深色 / 深色主题浅色
  - `label-primary-foreground`、`label-primary-inverted`：与之**相反**
  - 想彻底还原某一区域，可**全量套用官方 token 值**（从应用打包 CSS 里解析 `--dsw-static-*` 再解引用 `var()`）。

## 5. 品牌区是 SVG，且"底"和"字"在同一张图里

- **现象**：想给左上角 `deepseek` 字标换主题色，结果旁边的 `HARNESS` 徽章变成一个**空胶囊**（底色和字形同色 → 隐形）。
- **根因**：
  - 品牌区**没有文本节点**（诊断输出 `document.querySelectorAll('*')` 里找不到含 "deepseek" 的元素，文字是 SVG 路径）；
  - `deepseek` 字标、胶囊底色（一个 `<rect>`）、`HARNESS` 字形**同属一个 `<svg>`**；
  - "把所有形状 `fill` 改成主题色" 会**抹平底与字的对比**。
- **做法**：**按形状身份分别上色**，用 `getBBox()`（SVG 用户坐标，内部一致）：
  1. 面积最大的形状 = **胶囊底** → 目标底色；
  2. 完全位于胶囊**左侧**的形状 = **字标** → 主题色；
  3. 位于胶囊**内部/右侧**的形状 = **徽章字形** → 文字色。
  判断不出来时**什么都不染**（保持原生 → 至少可见），避免"越改越坏"。

## 6. 弹窗可能是 portal

- **现象**：设置面板透明度极高、文字看不清。
- **根因**：弹窗渲染在 `document.body` 下（portal），不在 `#root` 内；只扫 `#root *` 的规则永远命中不到。
- **做法**：识别弹窗时扫描**全文档**（`[role="dialog"]`、`[aria-modal="true"]`、类名含 `dialog/modal/drawer/sheet`），命中后套用高不透明表面。

## 7. 自愈逻辑要防"自己把自己干掉"

- **现象**：注入的徽章文字出现一瞬后消失。
- **根因**：装饰逻辑下一帧执行时，"隐藏原徽章的子元素"把**自己注入的标签**也一起隐藏了。
- **做法**：注入的元素打标记（`data-dsh-*`），后续所有"隐藏/覆盖"操作显式跳过带标记的元素，并在每帧重申其可见性。

## 8. 大图内嵌：控制体积

- 壁纸以 data URI 内嵌进 `client.js`，避免额外网络请求与路径问题。
- 4K 源图（~11 MB PNG）先缩到 **2560×1440 JPEG q88**（~700 KB）→ base64 后约 950 KB；两张壁纸的 bundle 约 1.6 MB 可接受。
- 若源图本身分辨率不高（例如 1672×941），**不要放大**，按原始尺寸编码更真实也更小。

---

## 调试建议

```js
// 1) 插件是否激活、当前皮肤
localStorage.getItem('dsh-anime-skin')

// 2) 大面积不透明元素还有哪些（应为空数组）
JSON.stringify([...document.querySelectorAll('#root *,#root')].filter(e=>{
  const r=e.getBoundingClientRect(), c=getComputedStyle(e);
  const a=(c.backgroundColor.match(/[\d.]+\)$/)||['1)'])[0];
  return r.width*r.height>300000 && parseFloat(a)>=0.9;
}).slice(0,6).map(e=>({cls:String(e.className).slice(0,44),bg:getComputedStyle(e).backgroundColor})))

// 3) 品牌区 SVG 内每个形状的位置与颜色（排查"底字同色"）
[...document.querySelectorAll('svg')].filter(s=>s.getBoundingClientRect().top<150)
  .map(s=>[...s.querySelectorAll('path,rect')].map(e=>{const b=e.getBBox();
    return {tag:e.tagName,x:Math.round(b.x),w:Math.round(b.width),h:Math.round(b.height),fill:getComputedStyle(e).fill}}))
```
