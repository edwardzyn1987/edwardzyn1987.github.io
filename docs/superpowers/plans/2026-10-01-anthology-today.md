# 「昨日今朝」栏目 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 给诗歌网站新增「昨日今朝」栏目——按访客实时日期，从全部诗作中筛出"历年同月同日（或最近）"的诗，呈现跨年份的"同一天回望"。

**Architecture:** Astro 5 静态站。build 时 `getCollection('poems')` 把全部诗序列化（含 build 端拆出的 UTC `month`/`day` 整数）注入页面；客户端 JS 读访客当天日期跑"逐年一瞥"算法、用与现有卡片一致的 DOM 注入渲染。新组件 `AnthologyToday.astro` 封装逻辑，首页与独立页复用。先把 `.poem-card*` 样式从 PoemCard scoped 提到 global.css 全局化（治本：JS 注入卡片才有样式，并修复 poems 页筛选塌样式的既有 bug）。

**Tech Stack:** Astro 5, TypeScript, Astro content collections, 原生 DOM API（无额外依赖）, GitHub Pages 静态部署。

**Spec:** `docs/superpowers/specs/2026-10-01-anthology-today-design.md`

## Global Constraints

- 静态站 + GitHub Pages：`output: 'static'`，无 `base`/`trailingSlash` 配置；"实时日期"必须靠客户端 JS，不能依赖 build 时日期。
- 诗歌卡片链接：`/poems/${id}`，其中 **`id` = `poem.id` 含年份子目录前缀**（形如 `2024/七律-中秋片影`）。collection **无 `slug` 字段**。绝不可把 id 当裸标题，否则漏年份 → 404。
- 日期基准：诗的 `month`/`day` 一律 build 时用 `getUTCMonth()+1` / `getUTCDate()` 拆成整数注入；client 不再 `new Date(iso)` 重解析。访客"今天"用本地时区 `getMonth()+1`/`getDate()`。
- schema 媒体字段只有 `video`（无 `audio`）；卡片媒体标记用 `hasVideo = !!poem.data.video`。
- 文件名/视觉：复用现有 `.poem-card*` DOM 结构与 class，视觉零偏差。
- 不碰：诗歌 `.md`、`content.config.ts` schema、视频/CDN、`Sidebar.astro`、`[...slug].astro`、`poems.astro`（样式全局化后自动修复）。
- 不新增依赖、不改 `package.json`。
- 不 `git push`（仅本地 commit；部署由 Edward 决定时机）。

## Review Focus

- **访客时区 off-by-one**：诗 date 按 UTC 午夜解析，client 若用本地时区读月日，UTC-N 时区会把 04-05 读成 04-04。→ Task 2 用 build 端 UTC 拆分的 `month`/`day`，client 不重解析；Task 6 Playwright 用 `timezoneId` 固定时区验证。
- **闰年 dayOfYear 污染**：target 按访客当前年（可能闰年）、诗按诗所在年算 dayOfYear，3 月后距离 ±1 污染。→ Task 2 距离计算把两边都投影到固定基准年（2001）算序数差。
- **卡片链接漏年份 → 404**：若把 `id` 当裸标题拼 URL。→ Task 2 直接用 `poem.id`（含年份），Task 6 验证点击跳转 200。
- **JS 注入卡片无样式**：Astro scoped CSS 用 cid 属性限定，JS 新建节点匹配不上。→ Task 1 把 `.poem-card*` 提到 global.css 全局化；Task 6 验证筛选/注入后卡片有 border-left。
- **某年无任何诗 / 全空兜底**：某年空则跳过；全部算不出则显示"今日暂无往年诗作"。→ Task 2 算法含跳过逻辑，Task 3 含空态文案。

---

## File Structure

| 文件 | 动作 | 职责 |
|---|---|---|
| `src/styles/global.css` | 修改 | 新增 `.poem-card*` 全局样式块（从 PoemCard 移来） |
| `src/components/PoemCard.astro` | 修改 | 从 scoped `<style>` 删除 `.poem-card*` 规则 |
| `src/components/AnthologyToday.astro` | 新建 | 封装：序列化诗数据 + 客户端 A1 算法 + 卡片注入；props `mode` |
| `src/pages/anthology-today.astro` | 新建 | 独立页 `/anthology-today`，`mode="full"` |
| `src/pages/index.astro` | 修改 | 插入 `<AnthologyToday mode="home" />` + 修 `hasAudio`→`hasVideo` bug |
| `src/components/Header.astro` | 修改 | navItems 加「昨日今朝」项 |

---

## Task 1: 卡片样式全局化（治本，修既有 bug）

把 `.poem-card*` 从 PoemCard scoped `<style>` 移到 global.css，使 JS 注入的卡片节点能命中样式。独立可验证：改完后 PoemCard 组件渲染不变、poems 页筛选后卡片不再塌。

**Files:**
- Modify: `src/styles/global.css`（在 `.tag:hover` 规则后追加 `.poem-card*` 块）
- Modify: `src/components/PoemCard.astro:36-93`（删除 scoped style 里的 `.poem-card*` 规则，保留 `<style>` 外壳为空或删空块）

**Interfaces:**
- Consumes: `global.css :root` 的 `--color-card-bg / --color-primary / --color-text-title / --color-text-secondary / --color-text-muted`（已存在）。
- Produces: 全局裸选择器 `.poem-card / .poem-card-header / .poem-card-title / .poem-card-excerpt / .poem-card-footer / .poem-card-tags / .poem-card-date / .video-badge` —— Task 2/3 的 JS 注入卡片依赖这些全局样式。

- [ ] **Step 1: 在 global.css 追加 `.poem-card*` 全局样式块**

在 `src/styles/global.css` 末尾（`.tag:hover {...}` 之后）追加（规则逐字来自 PoemCard.astro:37-92）：

```css
.poem-card {
  display: block;
  background: var(--color-card-bg);
  border-left: 3px solid var(--color-primary);
  padding: 18px 22px;
  border-radius: 0 8px 8px 0;
  text-decoration: none;
  transition: all 0.2s;
}

.poem-card:hover {
  background: rgba(255, 255, 255, 0.7);
  transform: translateX(4px);
}

.poem-card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.poem-card-title {
  font-size: 17px;
  color: var(--color-text-title);
  font-weight: 600;
}

.video-badge {
  font-size: 14px;
  opacity: 0.6;
}

.poem-card-excerpt {
  font-size: 14px;
  color: var(--color-text-secondary);
  line-height: 1.9;
  margin-bottom: 10px;
}

.poem-card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.poem-card-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.poem-card-date {
  font-size: 12px;
  color: var(--color-text-muted);
}
```

- [ ] **Step 2: 从 PoemCard.astro 删除这组 scoped 规则**

删除 `src/components/PoemCard.astro` 的 `<style>` 块内 `.poem-card` 到 `.poem-card-date` 的全部规则（即原 line 37-92 的内容）。`<style>` 块删空后一并删掉空的 `<style></style>`（PoemCard 不再有组件级样式）。保留 frontmatter 与模板不动。

- [ ] **Step 3: 构建验证样式已全局化、JS 卡片可命中**

Run:
```bash
cd "C:/Users/I350333/AI Workspace/poetry-website" && rm -rf dist .astro && npm run build 2>&1 | tail -5
grep -rn "\.poem-card\b" dist/poems/index.html | grep -v "data-astro-cid" | head -3
```
Expected: build `Complete!`；grep 能找到**裸** `.poem-card`（无 `[data-astro-cid` 限定）的 CSS 规则，证明已全局化。

- [ ] **Step 4: 验证无回归 + 既有卡片仍带 border-left**

Run:
```bash
cd "C:/Users/I350333/AI Workspace/poetry-website" && npm run build 2>&1 | grep -iE "error|warn|fail" || echo "CLEAN"
grep -c "border-left:3px solid var(--color-primary)" dist/poems/index.html
```
Expected: `CLEAN`；border-left 规则存在（count ≥ 1）。

- [ ] **Step 5: Commit**

```bash
cd "C:/Users/I350333/AI Workspace/poetry-website"
git add src/styles/global.css src/components/PoemCard.astro
git commit -m "fix: globalize .poem-card styles so JS-injected cards render (fixes poems filter restyle bug)"
```

---

## Task 2: AnthologyToday 组件 — 数据序列化 + A1 算法 + 卡片注入

新建核心组件。build 端序列化全部诗（含 UTC 拆分的 month/day），客户端跑逐年一瞥算法并注入卡片。先只做 `mode="full"` 全量（Task 4 的独立页直接用），`mode="home"` 的截断在 Step 内一并实现。

**Files:**
- Create: `src/components/AnthologyToday.astro`

**Interfaces:**
- Consumes: Task 1 的全局 `.poem-card*` 样式；`getCollection('poems')`；`poem.id`（含年份）、`poem.data.{title,category,tags,date,video}`、`poem.body`。
- Produces: Astro 组件 `<AnthologyToday mode="home" | "full" />`。内部客户端全局无导出；页面只需 import 并以 props 使用。注入目标容器 id = `anthology-list`，数据 template id = `anthology-data`。

- [ ] **Step 1: 写组件 frontmatter（build 端序列化）**

创建 `src/components/AnthologyToday.astro`，frontmatter：

```astro
---
import { getCollection } from 'astro:content';

interface Props {
  mode: 'home' | 'full';
}
const { mode } = Astro.props;

const poems = await getCollection('poems');

function getExcerpt(body: string): string {
  const lines = body.trim().split('\n').filter(l => l.trim());
  return lines.slice(0, 2).join('');
}

// 序列化：month/day 用 UTC 拆成整数（消除本地时区 off-by-one）；id 含年份前缀
const anthologyData = poems.map(poem => ({
  id: poem.id,                                   // 含年份，如 "2024/七律-中秋片影"
  title: poem.data.title,
  category: poem.data.category,
  tags: poem.data.tags,
  year: poem.data.date.getUTCFullYear(),
  month: poem.data.date.getUTCMonth() + 1,
  day: poem.data.date.getUTCDate(),
  dateISO: poem.data.date.toISOString(),
  hasVideo: !!poem.data.video,
  excerpt: getExcerpt(poem.body ?? ''),
}));

const HOME_YEAR_LIMIT = 3;  // mode="home" 展示前 N 年一瞥
---
```

- [ ] **Step 2: 写组件模板（外壳 + 占位 + 数据注入）**

frontmatter 后接模板。`mode="home"` 标题右侧带"查看全部 →"；容器 `#anthology-list` 初始放占位，JS 替换：

```astro
<section class="section anthology">
  <div class="anthology-head">
    <h2 class="section-title">昨 日 今 朝</h2>
    {mode === 'home' && <a class="anthology-more" href="/anthology-today">查看全部 →</a>}
  </div>
  <div class="poem-list" id="anthology-list">
    <p class="anthology-placeholder" id="anthology-placeholder">正在为您寻回往年今日…</p>
  </div>
</section>

<template id="anthology-data" set:text={JSON.stringify(anthologyData)}></template>
<script define:vars={{ mode, homeLimit: HOME_YEAR_LIMIT }}>
  window.__ANTHOLOGY_MODE__ = mode;
  window.__ANTHOLOGY_HOME_LIMIT__ = homeLimit;
</script>
```

- [ ] **Step 3: 写客户端算法 + 注入脚本**

接着写 `<script>`（TypeScript，Astro 会编译）。实现 §3 的 A1 算法——投影到固定基准年算距离（消除闰年污染）、逐年一瞥、当日全列、近似取最近、空年跳过、全空兜底、标注前缀：

```astro
<script>
  interface Entry {
    id: string; title: string; category: string; tags: string[];
    year: number; month: number; day: number; dateISO: string;
    hasVideo: boolean; excerpt: string;
  }

  // 把 (month,day) 投影到固定基准年 2001（平年）算"离年初第几天"，消除闰年污染。
  // 2001 无 2-29，故 2 月的 day 先 clamp 到 28，避免 Date 溢出到 3 月反而污染距离。
  function ordinal(month: number, day: number): number {
    const safeDay = (month === 2 && day > 28) ? 28 : day;
    const ms = Date.UTC(2001, month - 1, safeDay) - Date.UTC(2001, 0, 1);
    return Math.round(ms / 86400000);
  }

  function pickPerYear(all: Entry[], tMonth: number, tDay: number) {
    const byYear = new Map<number, Entry[]>();
    for (const e of all) {
      if (!byYear.has(e.year)) byYear.set(e.year, []);
      byYear.get(e.year)!.push(e);
    }
    const years = [...byYear.keys()].sort((a, b) => b - a); // 新→旧
    const tOrd = ordinal(tMonth, tDay);
    const result: Array<{ entry: Entry; kind: 'exact' | 'near' }> = [];
    for (const y of years) {
      const list = byYear.get(y)!;
      const exact = list.filter(e => e.month === tMonth && e.day === tDay);
      if (exact.length > 0) {
        for (const e of exact) result.push({ entry: e, kind: 'exact' });
      } else {
        let best: Entry | null = null, bestDist = Infinity;
        for (const e of list) {
          const d = Math.abs(ordinal(e.month, e.day) - tOrd);
          // tie-break: 距离相等取 dateISO 更晚；再相等取 title 字典序
          if (d < bestDist ||
              (d === bestDist && best && (e.dateISO > best.dateISO ||
               (e.dateISO === best.dateISO && e.title < best.title)))) {
            best = e; bestDist = d;
          }
        }
        if (best) result.push({ entry: best, kind: 'near' });
      }
    }
    return result;
  }

  function fmtDate(iso: string): string {
    return new Date(iso).toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' });
  }

  function buildCard(e: Entry, kind: 'exact' | 'near'): HTMLAnchorElement {
    const a = document.createElement('a');
    a.href = `/poems/${e.id}`;              // id 含年份，命中 /poems/<year>/<title>
    a.className = 'poem-card';
    const badge = e.hasVideo ? '<span class="video-badge" title="有朗诵视频">🎬</span>' : '';
    const mark = kind === 'exact'
      ? '<span class="tag anthology-mark">往年今日</span>'
      : `<span class="tag anthology-mark">近 · ${fmtDate(e.dateISO)}</span>`;
    a.innerHTML = `
      <div class="poem-card-header">
        <h3 class="poem-card-title">${e.title}</h3>
        ${badge}
      </div>
      <p class="poem-card-excerpt">${e.excerpt}</p>
      <div class="poem-card-footer">
        <div class="poem-card-tags">
          ${mark}
          <span class="tag">${e.category}</span>
          ${e.tags.map(t => `<span class="tag">${t}</span>`).join('')}
        </div>
        <span class="poem-card-date">${fmtDate(e.dateISO)}</span>
      </div>`;
    return a;
  }

  document.addEventListener('DOMContentLoaded', () => {
    const raw = document.getElementById('anthology-data')?.innerHTML ?? '[]';
    const data: Entry[] = JSON.parse(raw);
    const list = document.getElementById('anthology-list');
    const placeholder = document.getElementById('anthology-placeholder');
    if (!list) return;

    const now = new Date();
    const tMonth = now.getMonth() + 1;   // 访客本地时区"今天"
    const tDay = now.getDate();

    let picks = pickPerYear(data, tMonth, tDay);
    const mode = (window as any).__ANTHOLOGY_MODE__ ?? 'full';
    const homeLimit = (window as any).__ANTHOLOGY_HOME_LIMIT__ ?? 3;
    if (mode === 'home') picks = picks.slice(0, homeLimit);

    placeholder?.remove();
    if (picks.length === 0) {
      const p = document.createElement('p');
      p.className = 'anthology-placeholder';
      p.textContent = '今日暂无往年诗作';
      list.appendChild(p);
      return;
    }
    for (const { entry, kind } of picks) list.appendChild(buildCard(entry, kind));
  });
</script>
```

- [ ] **Step 4: 写组件样式（仅板块级，卡片样式已全局）**

```astro
<style>
  .anthology-head {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
  }
  .anthology-more {
    font-size: 13px;
    color: var(--color-primary);
    letter-spacing: 1px;
    text-decoration: none;
    white-space: nowrap;
  }
  .anthology-more:hover { text-decoration: underline; }
  .anthology-placeholder {
    color: var(--color-text-muted);
    font-size: 14px;
    padding: 20px 0;
    min-height: 60px;   /* 占位撑高，减少 JS 填充后的布局跳动 (FOUC) */
  }
  .anthology-mark {
    cursor: default;
    border-color: var(--color-primary);
    color: var(--color-primary);
  }
</style>
```

注意：组件没有 `.section`/`.section-title`/`.poem-list` 的定义——这些在首页/独立页上下文里已有（index.astro 的 scoped style 和全局），独立页需自带（见 Task 4）。

- [ ] **Step 5: 构建验证组件无语法错误**

Run:
```bash
cd "C:/Users/I350333/AI Workspace/poetry-website" && npm run build 2>&1 | tail -5
```
Expected: build `Complete!`，无 TS/Astro 报错。（此时组件尚未被任何页面引用，仅验证可编译——Astro 不会 tree-shake 掉 import，但未 import 的组件也不参与 build；若 build 不涉及它则此步仅确保文件语法合法。实际 import 验证在 Task 3/4。）

- [ ] **Step 6: Commit**

```bash
cd "C:/Users/I350333/AI Workspace/poetry-website"
git add src/components/AnthologyToday.astro
git commit -m "feat: add AnthologyToday component (anniversary poems by visitor date)"
```

---

## Task 3: 首页集成 + 修 hasAudio bug

把组件插入首页"最新发布"上方，并修复 `index.astro:61` 的 `hasAudio`→`hasVideo` 既有 bug。

**Files:**
- Modify: `src/pages/index.astro`

**Interfaces:**
- Consumes: Task 2 的 `<AnthologyToday mode="home" />`。

- [ ] **Step 1: import 组件**

在 `src/pages/index.astro` frontmatter 顶部 import 区加：

```astro
import AnthologyToday from '../components/AnthologyToday.astro';
```

- [ ] **Step 2: 在"最新发布" section 之前插入组件**

在 `<section class="section">`（含 `最 新 发 布` 的那段，约 line 50）**之前**插入：

```astro
    <AnthologyToday mode="home" />

```

即顺序变为：hero → `{featured && 精选}` → **AnthologyToday** → 最新发布 → CTA。

- [ ] **Step 3: 修复 hasAudio bug**

把 `src/pages/index.astro` 里"最新发布"PoemCard 的（约 line 61）：

```astro
hasAudio={!!poem.data.audio}
```

改为：

```astro
hasVideo={!!poem.data.video}
```

- [ ] **Step 4: 构建验证**

Run:
```bash
cd "C:/Users/I350333/AI Workspace/poetry-website" && rm -rf dist .astro && npm run build 2>&1 | tail -5
grep -c "anthology-list" dist/index.html
grep -c "anthology-data" dist/index.html
```
Expected: build `Complete!`；首页 HTML 含 `anthology-list` 容器和 `anthology-data` 数据模板（count ≥ 1）。

- [ ] **Step 5: 验证 hasVideo 修复生效（首页有视频的诗出 🎬）**

Run:
```bash
cd "C:/Users/I350333/AI Workspace/poetry-website"
# 首页"最新发布"是静态渲染的 PoemCard，若最新 5 首里有带 video 的，应出现 video-badge
grep -c "video-badge" dist/index.html || echo "0 (最新5首可能都无视频，需人工确认)"
```
Expected: 若最新 5 首中有 `video:` 字段的诗，`video-badge` count ≥ 1；若恰好都无视频则为 0（Task 6 的 Playwright 会跨板块核对一致性）。

- [ ] **Step 6: Commit**

```bash
cd "C:/Users/I350333/AI Workspace/poetry-website"
git add src/pages/index.astro
git commit -m "feat: add 昨日今朝 section to home; fix hasAudio→hasVideo badge bug"
```

---

## Task 4: 独立页 /anthology-today

**Files:**
- Create: `src/pages/anthology-today.astro`

**Interfaces:**
- Consumes: `BaseLayout`、Task 2 的 `<AnthologyToday mode="full" />`。

- [ ] **Step 1: 写独立页**

创建 `src/pages/anthology-today.astro`。独立页需自带 `.section`/`.section-title`/`.poem-list` 样式（首页靠自己的 scoped style 提供，独立页没有）——复用 index.astro 的同名规则值：

```astro
---
import BaseLayout from '../layouts/BaseLayout.astro';
import AnthologyToday from '../components/AnthologyToday.astro';
---

<BaseLayout title="昨日今朝">
  <main class="anthology-page">
    <AnthologyToday mode="full" />
    <div class="home-cta">
      <a href="/poems" class="cta-link">浏览全部诗词 →</a>
    </div>
  </main>
</BaseLayout>

<style>
  .anthology-page {
    max-width: 700px;
    margin: 0 auto;
    padding: 40px 40px 60px;
  }
  .section-title {
    font-size: 16px;
    color: var(--color-primary);
    letter-spacing: 6px;
    font-weight: 600;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid var(--color-border);
  }
  .poem-list {
    display: flex;
    flex-direction: column;
    gap: 14px;
  }
  .home-cta { text-align: center; margin-top: 50px; }
  .cta-link {
    display: inline-block;
    font-size: 14px;
    color: var(--color-primary);
    letter-spacing: 2px;
    padding: 10px 30px;
    border: 1px solid var(--color-primary-light);
    border-radius: 24px;
    text-decoration: none;
    transition: all 0.2s;
  }
  .cta-link:hover { background: rgba(139, 115, 85, 0.08); text-decoration: none; }
  @media (max-width: 768px) {
    .anthology-page { padding: 24px 20px 40px; }
  }
</style>
```

注意 `.section-title` 等需为**全局或本页 scoped**。因 AnthologyToday 组件内部的 `.section-title` 用的是 class（无样式），而本页 scoped style 的 `.section-title` 会因 Astro scoped 机制只命中本页 DOM——但 AnthologyToday 渲染的 `.section-title` 节点属于子组件，带的是子组件 cid 而非本页 cid，**本页 scoped `.section-title` 匹配不上**。因此本页这些样式需用 `<style is:global>`，或在 AnthologyToday 组件内自带 `.section-title`。**决策：把 `.section-title` 的声明放进本页的 `<style is:global>`**（范围限这几条，不污染过多）。将 `<style>` 改为 `<style is:global>`。

- [ ] **Step 2: 改用 is:global 确保子组件节点命中**

把 Step 1 的 `<style>` 改为 `<style is:global>`（因 `.section-title`/`.poem-list` 要作用于 AnthologyToday 子组件渲染的节点）。`.anthology-page`/`.home-cta`/`.cta-link` 也随之全局——与首页同名规则值一致，无冲突风险（值相同）。

- [ ] **Step 3: 构建验证路由生成**

Run:
```bash
cd "C:/Users/I350333/AI Workspace/poetry-website" && rm -rf dist .astro && npm run build 2>&1 | tail -8
ls dist/anthology-today/index.html && echo "ROUTE_OK"
grep -c "anthology-list" dist/anthology-today/index.html
```
Expected: build `Complete!`；`dist/anthology-today/index.html` 存在（`ROUTE_OK`）；含 `anthology-list`。

- [ ] **Step 4: Commit**

```bash
cd "C:/Users/I350333/AI Workspace/poetry-website"
git add src/pages/anthology-today.astro
git commit -m "feat: add /anthology-today standalone page"
```

---

## Task 5: 导航加「昨日今朝」

**Files:**
- Modify: `src/components/Header.astro:4-8`

**Interfaces:**
- Consumes: Task 4 的 `/anthology-today` 路由。

- [ ] **Step 1: navItems 加项**

把 `src/components/Header.astro` 的 `navItems` 由：

```astro
const navItems = [
  { label: '首页', href: '/' },
  { label: '诗词', href: '/poems' },
  { label: '关于', href: '/about' },
];
```

改为：

```astro
const navItems = [
  { label: '首页', href: '/' },
  { label: '昨日今朝', href: '/anthology-today' },
  { label: '诗词', href: '/poems' },
  { label: '关于', href: '/about' },
];
```

- [ ] **Step 2: 构建验证导航出现**

Run:
```bash
cd "C:/Users/I350333/AI Workspace/poetry-website" && npm run build 2>&1 | tail -3
grep -o "昨日今朝" dist/index.html | head -1
grep -c 'href="/anthology-today"' dist/index.html
```
Expected: build 成功；首页 HTML 含「昨日今朝」文本和 `href="/anthology-today"`（导航链接，count ≥ 1）。

- [ ] **Step 3: Commit**

```bash
cd "C:/Users/I350333/AI Workspace/poetry-website"
git add src/components/Header.astro
git commit -m "feat: add 昨日今朝 to site navigation"
```

---

## Task 6: 端到端功能验证（Playwright，假日期 + 固定时区）

无 unit test 框架；用 Playwright 对 dev server 做行为验证。覆盖 Review Focus 的所有点。

**Files:**
- 无源码改动（验证任务）；临时脚本/截图存 `temp/` 前缀。

**Interfaces:**
- Consumes: Task 1-5 的全部产物。

- [ ] **Step 1: 确认 Playwright 可用，否则降级为 build 产物断言**

Run:
```bash
cd "C:/Users/I350333/AI Workspace/poetry-website" && npx playwright --version 2>&1 || echo "NO_PLAYWRIGHT"
```
若 `NO_PLAYWRIGHT`：跳过 Playwright 步骤，改用"构建产物 + 逻辑手算"验证（见 Step 5 fallback），并在报告里明确标注"无法做浏览器实时验证，需 Edward 本地确认 UI"。不擅自 `npm install playwright`（违反 global constraint 不新增依赖）。

- [ ] **Step 2: 起 dev server**

Run（后台）:
```bash
cd "C:/Users/I350333/AI Workspace/poetry-website" && npm run dev
```
记下本地 URL（通常 `http://localhost:4321`）。验证完务必关掉该后台进程。

- [ ] **Step 3: 假日期=10-01 + 固定时区，验证"当日"匹配**

用 Playwright `context` 设 `timezoneId: 'Asia/Shanghai'`，`addInitScript` 覆写 `Date` 构造器**和** `Date.now`，固定为 `2026-10-01T08:00:00+08:00`。打开首页，`evaluate` 检查：
- `#anthology-list` 内 `.poem-card` 数量 > 0
- 存在带「往年今日」标注的卡片（historic 10-01 的诗，如数据中 2026 有 `七律·中秋片影` 不在 10-01 则看其他年份）
- 每张卡片 `getComputedStyle(card).borderLeftWidth` === `'3px'`（证明 Task 1 全局样式生效）
- 每张卡片 `href` 以 `/poems/` 开头且 decode 后含中文（含年份段）

截图存 `temp/anthology-1001.png`。

- [ ] **Step 4: 假日期=无诗日，验证"近似"回退**

同法把日期固定到一个大概率无诗的日子（如 `2026-02-15` 若该日各年无诗）。`evaluate` 检查：
- 卡片存在且带「近 · YYYY年M月D日」标注（证明回退到最近一首）
- 不同年份的近似诗其实际日期 ≠ 02-15

截图存 `temp/anthology-near.png`。

- [ ] **Step 5: 点击卡片验证路由 200（不 404）**

Playwright 点击首页「昨日今朝」第一张卡片，等待导航，断言：
- URL 形如 `/poems/<year>/<title>`（含年份段）
- 页面标题/正文正常渲染（非 404）

**Fallback（无 Playwright 时）**：
```bash
# 验证卡片 href 构造正确（id 含年份）——检查数据注入里 id 格式
cd "C:/Users/I350333/AI Workspace/poetry-website"
grep -o '"id":"[0-9]\{4\}/[^"]*"' dist/index.html | head -3   # 应形如 "id":"2024/七律-xxx"
# 验证全局卡片样式存在
grep -c "border-left:3px solid var(--color-primary)" dist/index.html
```
Expected: id 带 4 位年份前缀；border-left 规则存在。

- [ ] **Step 6: 跨板块 badge 一致性（hasVideo 修复验证）**

Playwright 在首页找一首同时出现在"最新发布"和"昨日今朝"的有视频诗（若存在），断言两处都显示 🎬。若无交集诗，手工确认"最新发布"里带 `video` 的诗现在有 🎬（Task 3 修复生效）。记录结论。

- [ ] **Step 7: 关闭 dev server，汇总验证报告**

关掉后台 `npm run dev`。在 session 里逐条列出 Step 3-6 的实际结果（通过/失败/无法验证+原因），不笼统说"验证通过"。

- [ ] **Step 8: Commit（若验证中发现并修了小问题）**

仅当验证暴露 bug 并修复时才 commit；纯验证无改动则跳过。

---

## 部署（Edward 确认后单独执行，不在本计划自动做）

本计划只到本地 commit。部署沿用 `poetry_website_upload` skill 流程：`git push origin main` → GitHub Actions 自动 build+发布（~60-90s）→ Playwright 验证线上 https://edwardzyn1987.github.io/ 的首页「昨日今朝」板块与 `/anthology-today` 页。**push 需 Edward 明确指令**（见 global constraint）。
