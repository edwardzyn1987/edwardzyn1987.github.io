# 「昨日今朝」栏目设计

**日期**: 2026-10-01
**项目**: 隐恕诗笺 (poetry-website, Astro 5 + GitHub Pages)
**作者**: Edward Zhang / Claude

---

## 1. 目标与意图

为诗歌网站新增一个「昨日今朝」栏目：按**访客打开页面的实时日期**，从全部诗作中筛出"历年同月同日"的诗，呈现一个跨年份的"同一天回望"。

- **意图**: 让读者在任意一天打开网站，都能看到往年这一天（或最接近这一天）写下的诗，形成"今日与往年今日对话"的时光回廊。
- **受众**: 网站访客（公开读者）。
- **成功标准**:
  1. 访客任意一天打开，栏目自动展示当天对应的历年诗作，无需作者每日重新部署。
  2. 每个有诗的年份都有一瞥代表（当天有则取当天，无则取该年最近）。
  3. 视觉与现有诗歌卡片完全一致，无风格偏差。

---

## 2. 约束与前提

| 约束 | 说明 |
|---|---|
| 静态站 | Astro 5 content collection + GitHub Pages。页面在 build 时生成；"实时日期"必须靠**客户端 JS**实现（build 时的日期不是访客的今天）。 |
| 零部署维护 | 栏目内容不能依赖每日重新构建——必须客户端按 `new Date()` 动态计算。 |
| 不改数据 | 不新增/修改诗歌 `.md`、不改 `src/content.config.ts` schema、不碰视频 CDN。 |
| 复用现有视觉 | 卡片 DOM 复用 `poems.astro` 的 `buildCard` 结构，`.section`/`.poem-list` 复用首页样式。 |
| 数据规模 | 当前 319 首，跨 2018–2026 九个年份。 |

---

## 3. 匹配算法 (A1 — 逐年一瞥)

设访客当天为 `MM-DD`（取自客户端 `new Date()`，用访客本地时区取 `getMonth()+1`/`getDate()`）。

**日期基准统一 (消除 off-by-one)**: 诗的 date 由 `z.coerce.date()` 按 **UTC 午夜**解析（`2018-04-05` → `2018-04-05T00:00:00Z`）。若 client 用本地时区 `new Date(iso).getMonth()` 重新解析，UTC-N 时区会把 04-05 读成 04-04。因此**诗的 `month`/`day` 一律在 build 时用 `getUTCMonth()+1`/`getUTCDate()` 拆成整数注入**（见 §5.1），client 端**不再 `new Date(dateISO)` 重新解析**，只做整数比对。访客"今天"的 MM-DD 用本地时区——这是唯一保留的本地时区依赖（符合"访客的今天"语义），同一访客不同时区看到不同结果是预期行为。

```
对每个有诗的年份 Y (2018..2026)，降序 (新→旧):
    当年该 MM-DD 当天的诗 S_exact = 该年 (month,day) == (MM,DD) 的全部诗
    若 S_exact 非空:
        输出 S_exact 全部 (B: 多首全列)，标记 kind = "当日"
    否则:
        在该年所有诗中，取与 MM-DD "日历距离"最小的一首 (tie-break 见下)
        输出该首，标记 kind = "近似"，附实际日期
    若该年无任何诗 → 跳过该年
```

**日历距离定义 (闰年无污染)**: 把每首诗的 `(month,day)` 和 target 的 `(MM,DD)` 都投影到**同一个固定基准年**（如非闰年 2001）再算序数差 `|ordinal(month,day) − ordinal(MM,DD)|`——不使用各自真实年份的 dayOfYear（否则闰年 target 与平年诗相减会在 3 月后 ±1 污染）。**不做跨年回绕**（12-31 与 01-01 视为相隔约 364 天，符合"该年里离这一天最近"的直觉）。若 target 恰为 2-29（访客当天）而基准年无 2-29，按 2-28 投影。

**tie-break**: 同年内两首与 target 距离相等时，取 `dateISO` 更晚者（更新）；仍并列取标题字典序。

**排序**: 结果按年份降序（新→旧），与"最新发布"方向一致。

**标注**: 见 §5.1 的卡片标注策略（与"视觉零偏差"的协调见 M4 修订）。

---

## 4. 落点

### 4.1 首页 (`src/pages/index.astro`)

当前首页实际渲染顺序（`featured` 为空，精选板块不显示）:

```
hero → 最新发布 → CTA
```

新增后:

```
hero
→ 昨 日 今 朝        ← 新增 (紧邻"最新发布"上方)
→ 最 新 发 布
→ 浏览全部诗词 CTA
```

- 若将来有诗设 `featured: true`，精选板块会出现在"昨日今朝"之上（代码位置更靠前），符合"昨日今朝在最新发布之前"的要求，不冲突。
- 首页模式 `mode="home"`：展示**前 3 年**一瞥（与 featured `.slice(0,3)` 对齐），板块标题右侧带"查看全部 →"链到独立页。
- **顺带修复既有 bug (已授权)**: `index.astro:61` 现为 `hasAudio={!!poem.data.audio}`，但 schema 无 `audio` 字段、PoemCard 无 `hasAudio` prop → 首页"最新发布"的 🎬 视频标记**从不显示**。改为 `hasVideo={!!poem.data.video}`，使其与昨日今朝板块的 🎬 一致（否则同一首有视频的诗在两板块 badge 不一致，违反"视觉零偏差"）。

### 4.2 独立页 (`src/pages/anthology-today.astro`，路由 `/anthology-today`)

- `BaseLayout` 包壳，页面标题"昨日今朝"。
- `mode="full"`：列出每年一瞥的完整卡片，不限年份数。

### 4.3 导航 (`src/components/Header.astro`)

`navItems` 由
```
首页 / 诗词 / 关于
```
改为
```
首页 / 昨日今朝 / 诗词 / 关于
```
新增项 `{ label: '昨日今朝', href: '/anthology-today' }`。

---

## 5. 组件设计

### 5.1 `src/components/AnthologyToday.astro` (新建)

**职责**: 单一入口，封装"序列化诗数据 + 客户端 A1 渲染"，首页与独立页复用。

**接口**:
```
Props: { mode: 'home' | 'full' }
```

**frontmatter (build 时)**:
- `getCollection('poems')` 拿全部诗。
- 序列化为 `{ id, title, category, tags, month, day, dateISO, hasVideo, excerpt }`：
  - **`id` = `poem.id`**，其值**含年份子目录前缀**，形如 `2024/七律-中秋片影`（collection 无 `slug` 字段；现有卡片全部用 `poem.id`，见 `poems.astro:22,149`、`index.astro:38→PoemCard.astro:21`）。client JS 拼 ``/poems/${id}`` 直接命中现有 rest-param 路由 `[...slug].astro`（`params:{slug:poem.id}` 吃下带斜杠的 id）。**绝不可把 id 当裸标题**，否则 URL 漏掉 `年份/` → 全站卡片点击 404。
  - **`month` / `day`**: build 时直接拆成整数 `poem.data.date.getUTCMonth()+1` / `poem.data.date.getUTCDate()`（见 §3 时区说明，解决 off-by-one）。
  - **`dateISO`**: `poem.data.date.toISOString()`，仅用于近似项显示年份，不参与月日比对。
  - `hasVideo` = `!!poem.data.video`（schema 唯一的媒体字段，见 content.config.ts；无 `audio` 字段）。
  - `excerpt`: 在本组件内**重新声明** `getExcerpt`（现有两处 `getExcerpt` 均为各文件内局部函数，无法 import）。
- 注入页面：`<template id="anthology-data" set:text={JSON.stringify(...)}>`（与 `poems.astro` 同款模式）。

**模板 (SSR fallback)**:
- 容器 `#anthology-list`（空），加一行占位文案 `正在为您寻回往年今日…`（JS 禁用时降级）。
- 板块外壳复用 `.section` / `.section-title` / `.poem-list`。
- `mode="home"` 时标题右侧渲染"查看全部 →"链接到 `/anthology-today`。

**客户端 `<script>`**:
1. 读 `new Date()` → 得访客当天 `MM-DD`（本地时区）。
2. 解析注入的诗数据（直接用 `month`/`day` 整数，不重新 `new Date()`）。
3. 跑 §3 A1 算法 → 得按年降序的一瞥列表（`mode="home"` 截取**前 3 年**，与 featured `.slice(0,3)` 对齐；`mode="full"` 不限）。
4. 用与 `poems.astro` `buildCard` **相同的 DOM 结构**生成卡片，追加到 `#anthology-list`，移除占位。
5. **当日/近似标注 (与"视觉零偏差"协调)**: 不新增破坏结构的节点。卡片日期位统一用现有长格式 `toLocaleDateString('zh-CN',{year,month,day})`（与 PoemCard/buildCard 一致）。"近似"项仅在日期位**前缀**一个轻量文案 `約` 或 `近`（用现有 `.tag` 样式的小 span），"当日"项前缀 `今日往年` 或不加——文案在实现时定稿、不改 DOM 骨架，故不破坏零偏差。
6. 全空兜底：显示"今日暂无往年诗作"。

### 5.2 复用点
- `getExcerpt`: 与 `index.astro` / `poems.astro` 相同实现（取前两行）。
- `buildCard` DOM: 照搬 `poems.astro` 结构，确保视觉零偏差。
- 卡片点击 → `/poems/<slug>`（现有详情路由）。

---

## 6. 数据流

```
build 时:
  AnthologyToday.astro frontmatter
    → getCollection('poems') → 序列化 → 注入 <template>

运行时 (访客浏览器):
  <script> 读 new Date() + <template> 数据
    → A1 算法 → 生成卡片 DOM → 填入 #anthology-list
```

首页其他板块（最新发布/精选）仍为 build 时静态渲染，互不影响。

---

## 7. 边界处理

| 情况 | 处理 |
|---|---|
| 某年当天有多首 | 全列，不去重 (B 决定) |
| 某年当天无诗 | 取该年最近一首，标"近似"+实际日期 |
| 某年无任何诗 | 跳过该年 |
| 所有年份都算不出 | 显示"今日暂无往年诗作" |
| 闰年 2-29 当天 | 目标日按最近有效日处理 |
| JS 禁用 | 显示占位文案（优雅降级，不报错） |
| FOUC (加载闪烁) | 该板块靠 client JS 填充，访客打开首页会先见空容器。**处理**: 容器初始 CSS `min-height` 占位 + 占位文案低调（`color:muted`），JS 就绪后替换；避免布局跳动。接受首屏到 JS 执行间的短暂占位（非 bug，是静态站 CSR 的固有行为）。 |
| SEO | 该板块内容不在静态 HTML 中，搜索引擎不索引"往年今日"卡片。**已知取舍**，可接受——诗作本身仍通过 `/poems` 和详情页被索引，昨日今朝只是入口聚合。 |

---

## 8. 测试与验证

1. **构建**: `npm run build` 过 schema + 构建成功；`npm run build 2>&1 | grep -iE "error|warn|fail"` 为空。
2. **逻辑验证 (Playwright + 假日期)**: `npm run dev` 本地起站，用 Playwright `addInitScript` 覆写 `Date` **构造器 + `Date.now`**（client 统一只用 `new Date()`，但覆写需连 `Date.now` 一起，否则真实时间泄漏），并用 `context` 的 `timezoneId` 固定时区（配合 M1，验证时区无 off-by-one），验证两种场景：
   - **当天有诗** (如 10-01): 确认列出的是各年 10-01 当天诗。
   - **当天无诗需取最近** (挑一个无诗的日期): 确认各年回退到最近一首且标"近似"。
3. **视觉**: 首页"昨日今朝"板块卡片与"最新发布"卡片样式一致；导航出现"昨日今朝"项且 active 态正确。
4. **不回归**: 现有首页/诗词/详情页不受影响。

---

## 9. 范围红线

**新增**: `src/components/AnthologyToday.astro`、`src/pages/anthology-today.astro`。
**修改**: `src/components/Header.astro`（navItems 加 1 项）、`src/pages/index.astro`（加 1 import + 1 段 section + 修复 line 61 `hasAudio`→`hasVideo` 既有 bug）。
**不碰**: 诗歌 `.md`、`content.config.ts` schema、视频/CDN、其他页面逻辑、`Sidebar.astro`、`PoemCard.astro`、`[...slug].astro` 路由、`Header.astro` 的 mobile 汉堡 script（新增项自动被 toggle 纳入，无需改）。

部署沿用现有 `poetry_website_upload` skill 的 build→commit→push→Playwright 验证流程。
