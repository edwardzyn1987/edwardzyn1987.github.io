# 设计文档：关于页隐藏全站访问量统计

- **日期**：2026-07-20
- **状态**：待 Edward 确认
- **网站**：https://edwardzyn1987.github.io/ （Astro 5 静态站，GitHub Pages 部署，无后端）

## 1. 目标

在「关于」页面底部加一个不起眼的按钮，点击弹出密码 modal，输入正确密码后显示**全站总访问量**。访问量数字平时不出现在任何页面上，只在密码正确后才显示。

## 2. 需求（已与 Edward 确认）

| 项 | 决定 |
|---|---|
| 统计口径 | 全站总访问量（新建站点级计数器） |
| 数据源 | 复用现有 CounterAPI v1（`api.counterapi.dev`，免费、无 token） |
| 计数语义 | UV 近似——`sessionStorage` 去重，同一标签页会话只 +1 |
| 密码 | `12345678`，客户端轻量遮蔽（Edward 已接受静态站无法真正隐藏密码） |
| 交互 | 弹窗 modal（复用现有视频播放器 modal 风格） |
| 按钮位置 | 「关于」页最底部，低调样式 |
| 平时是否显示数字 | 否，只在密码正确后在 modal 内显示 |

## 3. 现状（代码证据）

- 全部 4 个页面（`about.astro` / `index.astro` / `poems/[...slug].astro` / `poems.astro`）都用 `BaseLayout` 包裹 → 放在 BaseLayout 的脚本对全站生效。（grep 已确认）
- `BaseLayout.astro` 29 行：`<head>` + `<body>`（`<Header/>` + `<slot/>`）+ 全局样式。
- 现有 per-poem 计数器（`[...slug].astro`）：`fetch('.../v1/edward-poetry/<counterKey>/up')` → 响应 JSON 有数字字段 `.count`；namespace = `edward-poetry`，per-poem key = `p-<sha1前16位>`。
- **无** Astro `ClientRouter`/`ViewTransitions`/`astro:page-load`（grep 已确认，只有 CSS `transition:` 属性）→ 传统整页加载，BaseLayout 的普通 `<script>` 每次导航都执行。
- 现有视频 modal 行为（`[...slug].astro`）：`.video-modal` + `.open` class 切换；`backdrop` 点击关闭、`close` 按钮、`Escape` keydown 关闭；打开时把 modal `appendChild` 到 `document.body` 以脱离父级 stacking context。

## 4. CounterAPI v1 真实行为（审阅 agent 实测验证）

- `GET .../v1/edward-poetry/<key>/up` → 读 **并 +1**，返回 `{"count":N,...}`。
- `GET .../v1/edward-poetry/<key>`（裸 URL，不带 `/up`）→ **只读不加**，返回 `{"count":N,...}`。连续裸读数字不变。
- `/up` 对不存在的 key 会**自动创建**（首次返回 `count:1`）。
- 裸读一个从未 `/up` 过的 key 可能 404 → 读取端必须优雅处理（显示 0/—）。
- 裸读偶有短暂 read-replica 延迟（写后立即读可能读到旧值，秒级自愈）——对访问量这种数字无影响，但不要建立"写后立即读一致"的逻辑。
- **不迁移 v2**：v2 需要 Authorization token（`401 private workspaces`）；v1 无 token 可用，且现有代码已依赖 v1。

## 5. 架构

改 2 个文件，无新增后端、无新增第三方服务：

| 文件 | 改动 |
|---|---|
| `src/layouts/BaseLayout.astro` | 加全站计数脚本：每会话首次访问任意页面 → 对站点 key `site-uv` 发一次 `/up`（+1），成功后置 sessionStorage 标记。不读、不显示返回值。 |
| `src/pages/about.astro` | 底部加低调按钮 + 密码 modal（JS/CSS 内联）。密码正确 → **裸 URL 读** `site-uv`（不 +1）→ modal 内显示 `count.toLocaleString()`。 |

### 5.1 组件 A — 全站 UV 计数（BaseLayout）

- 站点 key：`site-uv`（与 per-poem 的 `p-` 前缀隔离），namespace 仍是 `edward-poetry`。
- 逻辑：
  ```js
  if (!sessionStorage.getItem('uv-counted')) {
    fetch('https://api.counterapi.dev/v1/edward-poetry/site-uv/up')
      .then(r => { if (r.ok) sessionStorage.setItem('uv-counted', '1'); })
      .catch(() => {});   // 失败静默，不设标记 → 下次导航重试
  }
  ```
- **关键修正**：标记只在 `r.ok` 成功时设（失败不设，避免误标"已计数"导致少计）。
- 不在 BaseLayout 读/显示返回值（避免 view-source 泄漏读取入口；且平时不显示是核心需求）。
- 整页加载模型下，此脚本每次导航都执行，靠 sessionStorage 保证一会话只 +1。

### 5.2 组件 B — 关于页隐藏入口

- 按钮：`about.astro` 最底部，低调样式（小字、淡色、类似页脚），文案如「· 站点信息 ·」或一个不显眼的小图标，不吸引普通访客。
- Modal：复用视频 modal 的结构与行为——`.open` class 切换、点背景关闭、✕ 关闭、`Escape` 关闭、打开时 `appendChild` 到 body、打开时聚焦密码输入框、关闭时清空密码框。
- 两态：
  - 输入态：密码 input + 确定按钮（回车 = 确定）。
  - 结果态（密码正确后）：显示「全站访问量 **1,234** 次」。
- 密码校验：`const PW = '12345678'; if (input.value === PW) { ...读取并显示... } else { 显示"密码错误"，不关闭，可重试 }`。
- 读取：`GET .../v1/edward-poetry/site-uv`（**裸 URL，不 +1**），`.then(r => r.ok ? r.json() : null)`，取 `.count`，`toLocaleString()` 格式化；非 ok / 无 count → 显示 `0` 或 `—`。

### 5.3 数据流

```
访客打开任意页面 → BaseLayout 脚本 → (本会话首次?) → site-uv /up → +1（静默，不显示）
Edward 打开关于页 → 拉到底 → 点隐藏按钮 → modal → 输 12345678 → 校验通过
                → 裸读 site-uv（不+1）→ 显示 count.toLocaleString()
```

## 6. 错误处理

- CounterAPI 计数不可达：静默失败，不影响页面渲染；sessionStorage 标记不设，下次重试。
- 密码错误：modal 内提示「密码错误」，不关闭，可重试。
- 读取失败 / key 尚未创建（404）：显示 `0` 或 `—`，不破坏 modal。
- 回车键 = 点确定。

## 7. 安全性（明确的限制）

- 密码 `12345678` 明文写在客户端 JS 里，view-source 可见 → 只挡随手点的普通访客，挡不住懂技术的人。Edward 已接受此级别。
- 访问量数字**不在**静态构建产物 / view-source / 初始 DOM 中——只在密码正确分支运行时 fetch 后注入 DOM。source 里只有按钮、modal 骨架、明文密码。✓ 符合"平时不显示"需求。

## 8. 验证方案

- `npm run build` 干净通过，`about` 页正常构建。
- 本地 `npm run dev`：
  - 打开任意页 → DevTools Network 看到 `site-uv/up` 发出一次；刷新/翻页不再发（sessionStorage 生效）。
  - 关于页底部按钮存在且低调；点击弹出 modal；错密码提示错误；对密码 `12345678` 显示数字。
  - Escape / 点背景 / ✕ 均可关闭；关闭后重开密码框为空。
- 部署后线上 Playwright 复验：按钮存在、modal 可开、密码流程正常、数字能显示；确认现有视频 modal 与 per-poem 计数器未被破坏。

## 9. 不做的事（YAGNI）

- 不做真正的服务端密码校验（需后端，静态站做不到）。
- 不迁 CounterAPI v2、不引入 goatcounter/umami 等第二个统计服务（对个人诗歌网站属过度工程）。
- 不做趋势图/按日曲线（CounterAPI 免费版只存累计值）。
- 不做 localStorage 每日去重（Edward 选了每会话计一次）。
