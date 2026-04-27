# Poetry Website Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a static Astro poetry website with ink-wash classical Chinese styling, sidebar navigation, audio recitation playback, search, and Giscus comments.

**Architecture:** Astro with Content Collections for poem Markdown files. Pure CSS styling (no framework). Client-side search via Fuse.js. Audio via HTML5 Audio API with floating play button. Giscus for comments.

**Tech Stack:** Astro 5.x, Fuse.js, Giscus, HTML5 Audio API, Google Fonts (Ma Shan Zheng, Noto Serif SC, ZCOOL XiaoWei)

---

## File Structure

```
poetry-website/
├── astro.config.mjs              # Astro configuration
├── package.json                   # Dependencies
├── tsconfig.json                  # TypeScript config
├── public/
│   ├── audio/                     # MP3 recitation files
│   └── favicon.svg                # Site favicon
├── src/
│   ├── content.config.ts          # Content collection schema
│   ├── content/
│   │   └── poems/                 # Poem Markdown files
│   │       ├── qiu-ye-huai-yuan.md
│   │       ├── chun-ri-ou-cheng.md
│   │       ├── deng-gao-wang-yuan.md
│   │       ├── ye-yu-ji-bei.md
│   │       └── jiang-pan-du-bu.md
│   ├── styles/
│   │   └── global.css             # Global styles (colors, fonts, base)
│   ├── layouts/
│   │   └── BaseLayout.astro       # HTML shell, fonts, global CSS
│   ├── components/
│   │   ├── Header.astro           # Top navigation bar
│   │   ├── Sidebar.astro          # Left sidebar (search, categories, tags)
│   │   ├── PoemCard.astro         # Poem list item card
│   │   ├── AudioPlayer.astro      # Floating audio play button
│   │   └── PoemNav.astro          # Previous/next poem navigation
│   └── pages/
│       ├── index.astro            # Home page
│       ├── poems.astro            # Poem list page with sidebar
│       ├── poems/
│       │   └── [...slug].astro    # Poem detail page (dynamic route)
│       ├── about.astro            # About the author
│       └── guestbook.astro        # Guestbook with Giscus
```

---

## Task 1: Project Scaffold

**Files:**
- Create: `astro.config.mjs`
- Create: `package.json`
- Create: `tsconfig.json`
- Create: `src/styles/global.css`
- Create: `src/layouts/BaseLayout.astro`
- Create: `public/favicon.svg`

- [ ] **Step 1: Initialize Astro project**

Run from the `poetry-website` directory:

```bash
cd "/c/Users/I350333/AI Workspace/poetry-website"
npm create astro@latest -- . --template minimal --install --no-git --typescript strict
```

Accept defaults. This creates `astro.config.mjs`, `package.json`, `tsconfig.json`, and basic `src/pages/index.astro`.

- [ ] **Step 2: Verify Astro installed correctly**

```bash
cd "/c/Users/I350333/AI Workspace/poetry-website"
npx astro --version
```

Expected: Astro version number (e.g., `astro@5.x.x`)

- [ ] **Step 3: Create global CSS**

Create `src/styles/global.css`:

```css
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700&family=Ma+Shan+Zheng&family=ZCOOL+XiaoWei&display=swap');

:root {
  --color-bg: #f5f0e8;
  --color-bg-end: #e8dcc8;
  --color-primary: #8b7355;
  --color-primary-light: #c4b39a;
  --color-text-title: #2c2c2c;
  --color-text-body: #3c3c3c;
  --color-text-secondary: #666;
  --color-text-muted: #999;
  --color-card-bg: rgba(255, 255, 255, 0.5);
  --color-border: rgba(139, 115, 85, 0.2);
  --color-tag-border: #c4b39a;
  --color-tag-text: #8b7355;

  --font-brush: 'Ma Shan Zheng', cursive;
  --font-serif: 'Noto Serif SC', 'Songti SC', serif;
  --font-subtitle: 'ZCOOL XiaoWei', serif;
}

*,
*::before,
*::after {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  font-size: 16px;
  scroll-behavior: smooth;
}

body {
  font-family: var(--font-serif);
  background: linear-gradient(135deg, var(--color-bg) 0%, var(--color-bg-end) 100%);
  color: var(--color-text-body);
  min-height: 100vh;
  line-height: 1.6;
}

a {
  color: var(--color-primary);
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

.tag {
  display: inline-block;
  font-size: 12px;
  color: var(--color-tag-text);
  border: 1px solid var(--color-tag-border);
  padding: 2px 10px;
  border-radius: 12px;
  cursor: pointer;
  transition: background 0.2s;
}

.tag:hover {
  background: rgba(139, 115, 85, 0.1);
}
```

- [ ] **Step 4: Create BaseLayout**

Create `src/layouts/BaseLayout.astro`:

```astro
---
interface Props {
  title: string;
  description?: string;
}

const { title, description = '古体诗词个人展示' } = Astro.props;
---

<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="description" content={description} />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <title>{title} | 墨韵诗笺</title>
  </head>
  <body>
    <slot />
  </body>
</html>

<style is:global>
  @import '../styles/global.css';
</style>
```

- [ ] **Step 5: Create favicon**

Create `public/favicon.svg`:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
  <text x="50" y="72" font-size="68" text-anchor="middle" font-family="serif" fill="#8b7355">墨</text>
</svg>
```

- [ ] **Step 6: Replace default index page with placeholder**

Replace `src/pages/index.astro`:

```astro
---
import BaseLayout from '../layouts/BaseLayout.astro';
---

<BaseLayout title="首页">
  <main style="display:flex;align-items:center;justify-content:center;min-height:100vh;">
    <h1 style="font-family:var(--font-brush);font-size:48px;color:var(--color-text-title);letter-spacing:8px;">
      墨韵诗笺
    </h1>
  </main>
</BaseLayout>
```

- [ ] **Step 7: Verify dev server starts**

```bash
cd "/c/Users/I350333/AI Workspace/poetry-website"
npx astro dev --port 4321
```

Open `http://localhost:4321` — should see "墨韵诗笺" in brush font on warm parchment background.

- [ ] **Step 8: Commit**

```bash
git init
git add -A
git commit -m "feat: scaffold Astro project with ink-wash classical styling"
```

---

## Task 2: Content Collection & Sample Poems

**Files:**
- Create: `src/content.config.ts`
- Create: `src/content/poems/qiu-ye-huai-yuan.md`
- Create: `src/content/poems/chun-ri-ou-cheng.md`
- Create: `src/content/poems/deng-gao-wang-yuan.md`
- Create: `src/content/poems/ye-yu-ji-bei.md`
- Create: `src/content/poems/jiang-pan-du-bu.md`
- Create: `public/audio/` (empty directory placeholder)

- [ ] **Step 1: Create content collection schema**

Create `src/content.config.ts`:

```typescript
import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const poems = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/poems' }),
  schema: z.object({
    title: z.string(),
    category: z.enum(['五言绝句', '七言绝句', '五言律诗', '七言律诗', '词']),
    tags: z.array(z.string()),
    date: z.coerce.date(),
    audio: z.string().optional(),
    note: z.string().optional(),
    featured: z.boolean().default(false),
  }),
});

export const collections = { poems };
```

- [ ] **Step 2: Create sample poem files**

Create `src/content/poems/qiu-ye-huai-yuan.md`:

```markdown
---
title: "秋夜怀远"
category: "七言绝句"
tags: ["思乡", "秋"]
date: 2024-10-15
note: "秋夜独坐，月光如水，忽忆远方故人。遂提笔写下此诗，聊寄思念之情。"
featured: true
---

露冷风清夜未央，
孤灯独坐忆潇湘。
遥知千里同明月，
不尽相思入梦长。
```

Create `src/content/poems/chun-ri-ou-cheng.md`:

```markdown
---
title: "春日偶成"
category: "五言绝句"
tags: ["春", "咏物"]
date: 2024-03-20
featured: true
---

东风拂柳绿丝长，
燕子归来认旧梁。
桃花落尽溪流远，
一片春光入画堂。
```

Create `src/content/poems/deng-gao-wang-yuan.md`:

```markdown
---
title: "登高望远"
category: "七言绝句"
tags: ["山水", "秋"]
date: 2024-09-09
note: "重阳登高，极目远眺，天地苍茫间顿生感慨。"
featured: true
---

天际苍茫云万里，
山头寂寞月孤圆。
登高不觉秋风冷，
一望长河落日边。
```

Create `src/content/poems/ye-yu-ji-bei.md`:

```markdown
---
title: "夜雨寄北"
category: "七言绝句"
tags: ["思乡", "秋"]
date: 2024-08-22
---

窗外潇潇雨不休，
灯前细语话从头。
何当共剪西窗烛，
却话巴山夜雨秋。
```

Create `src/content/poems/jiang-pan-du-bu.md`:

```markdown
---
title: "江畔独步"
category: "五言律诗"
tags: ["山水", "春"]
date: 2024-04-10
---

江流千古去无声，
独立斜阳万里情。
白鹭一行天际远，
青山两岸画中行。
风吹柳絮随波去，
雨打芭蕉入梦轻。
莫道春光留不住，
年年花发又清明。
```

- [ ] **Step 3: Create audio directory**

```bash
mkdir -p "/c/Users/I350333/AI Workspace/poetry-website/public/audio"
touch "/c/Users/I350333/AI Workspace/poetry-website/public/audio/.gitkeep"
```

- [ ] **Step 4: Verify content collection loads**

Temporarily edit `src/pages/index.astro` to test:

```astro
---
import BaseLayout from '../layouts/BaseLayout.astro';
import { getCollection } from 'astro:content';

const poems = await getCollection('poems');
---

<BaseLayout title="首页">
  <main style="padding:40px;text-align:center;">
    <h1 style="font-family:var(--font-brush);font-size:48px;color:var(--color-text-title);letter-spacing:8px;">
      墨韵诗笺
    </h1>
    <p style="margin-top:20px;color:var(--color-text-secondary);">
      共 {poems.length} 首诗词
    </p>
  </main>
</BaseLayout>
```

Run `npx astro dev --port 4321` and verify it shows "共 5 首诗词".

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat: add content collection schema and 5 sample poems"
```

---

## Task 3: Header Component

**Files:**
- Create: `src/components/Header.astro`
- Modify: `src/layouts/BaseLayout.astro`

- [ ] **Step 1: Create Header component**

Create `src/components/Header.astro`:

```astro
---
const currentPath = Astro.url.pathname;

const navItems = [
  { label: '首页', href: '/' },
  { label: '诗词', href: '/poems' },
  { label: '关于', href: '/about' },
  { label: '留言', href: '/guestbook' },
];
---

<header class="site-header">
  <a href="/" class="site-logo">墨韵诗笺</a>
  <nav class="site-nav">
    {navItems.map(item => (
      <a
        href={item.href}
        class:list={['nav-link', { active: currentPath === item.href || (item.href !== '/' && currentPath.startsWith(item.href)) }]}
      >
        {item.label}
      </a>
    ))}
  </nav>
  <button class="mobile-menu-btn" aria-label="菜单">
    <span></span>
    <span></span>
    <span></span>
  </button>
</header>

<style>
  .site-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 40px;
    border-bottom: 1px solid var(--color-border);
    background: rgba(245, 240, 232, 0.9);
    backdrop-filter: blur(8px);
    position: sticky;
    top: 0;
    z-index: 100;
  }

  .site-logo {
    font-family: var(--font-brush);
    font-size: 24px;
    color: var(--color-text-title);
    letter-spacing: 4px;
    text-decoration: none;
  }

  .site-nav {
    display: flex;
    gap: 30px;
  }

  .nav-link {
    font-size: 14px;
    color: var(--color-text-secondary);
    letter-spacing: 2px;
    text-decoration: none;
    padding-bottom: 4px;
    transition: color 0.2s;
  }

  .nav-link:hover {
    color: var(--color-text-title);
  }

  .nav-link.active {
    color: var(--color-text-title);
    font-weight: 600;
    border-bottom: 2px solid var(--color-primary);
  }

  .mobile-menu-btn {
    display: none;
    flex-direction: column;
    gap: 5px;
    background: none;
    border: none;
    cursor: pointer;
    padding: 4px;
  }

  .mobile-menu-btn span {
    display: block;
    width: 22px;
    height: 2px;
    background: var(--color-text-title);
    transition: all 0.3s;
  }

  @media (max-width: 768px) {
    .site-header { padding: 12px 20px; }
    .site-nav { display: none; }
    .site-nav.open {
      display: flex;
      flex-direction: column;
      position: absolute;
      top: 100%;
      left: 0;
      right: 0;
      background: rgba(245, 240, 232, 0.98);
      padding: 16px 20px;
      border-bottom: 1px solid var(--color-border);
      gap: 16px;
    }
    .mobile-menu-btn { display: flex; }
  }
</style>

<script>
  const btn = document.querySelector('.mobile-menu-btn');
  const nav = document.querySelector('.site-nav');
  btn?.addEventListener('click', () => nav?.classList.toggle('open'));
</script>
```

- [ ] **Step 2: Add Header to BaseLayout**

Replace `src/layouts/BaseLayout.astro`:

```astro
---
import Header from '../components/Header.astro';

interface Props {
  title: string;
  description?: string;
}

const { title, description = '古体诗词个人展示' } = Astro.props;
---

<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="description" content={description} />
    <link rel="icon" type="image/svg+xml" href="/favicon.svg" />
    <title>{title} | 墨韵诗笺</title>
  </head>
  <body>
    <Header />
    <slot />
  </body>
</html>

<style is:global>
  @import '../styles/global.css';
</style>
```

- [ ] **Step 3: Verify in browser**

Run `npx astro dev --port 4321`. Verify header shows with logo and nav links. Resize to mobile width and verify hamburger menu appears and toggles.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "feat: add sticky header with responsive mobile menu"
```

---

## Task 4: Sidebar Component

**Files:**
- Create: `src/components/Sidebar.astro`

- [ ] **Step 1: Create Sidebar component**

Create `src/components/Sidebar.astro`:

```astro
---
import { getCollection } from 'astro:content';

interface Props {
  currentCategory?: string;
  currentTag?: string;
}

const { currentCategory, currentTag } = Astro.props;
const poems = await getCollection('poems');

const categories = ['五言绝句', '七言绝句', '五言律诗', '七言律诗', '词'] as const;
const categoryCounts = new Map<string, number>();
for (const poem of poems) {
  const cat = poem.data.category;
  categoryCounts.set(cat, (categoryCounts.get(cat) ?? 0) + 1);
}

const tagCounts = new Map<string, number>();
for (const poem of poems) {
  for (const tag of poem.data.tags) {
    tagCounts.set(tag, (tagCounts.get(tag) ?? 0) + 1);
  }
}
const sortedTags = [...tagCounts.entries()].sort((a, b) => b[1] - a[1]);
---

<aside class="sidebar">
  <div class="sidebar-section">
    <input
      type="text"
      class="search-input"
      id="poem-search"
      placeholder="🔍 搜索诗词..."
      autocomplete="off"
    />
    <div class="search-results" id="search-results"></div>
  </div>

  <div class="sidebar-section">
    <h4 class="sidebar-title">分 类</h4>
    <nav class="sidebar-nav">
      <a
        href="/poems"
        class:list={['sidebar-link', { active: !currentCategory }]}
      >
        全部 ({poems.length})
      </a>
      {categories.map(cat => {
        const count = categoryCounts.get(cat) ?? 0;
        return count > 0 ? (
          <a
            href={`/poems?category=${encodeURIComponent(cat)}`}
            class:list={['sidebar-link', { active: currentCategory === cat }]}
          >
            {cat} ({count})
          </a>
        ) : null;
      })}
    </nav>
  </div>

  <div class="sidebar-section">
    <h4 class="sidebar-title">标 签</h4>
    <div class="tag-cloud">
      {sortedTags.map(([tag]) => (
        <a
          href={`/poems?tag=${encodeURIComponent(tag)}`}
          class:list={['tag', { active: currentTag === tag }]}
        >
          {tag}
        </a>
      ))}
    </div>
  </div>
</aside>

<style>
  .sidebar {
    width: 220px;
    flex-shrink: 0;
    padding: 24px 18px;
    border-right: 1px solid var(--color-border);
    background: rgba(139, 115, 85, 0.04);
    display: flex;
    flex-direction: column;
    gap: 24px;
    height: calc(100vh - 57px);
    position: sticky;
    top: 57px;
    overflow-y: auto;
  }

  .sidebar-section {}

  .sidebar-title {
    font-size: 12px;
    color: var(--color-primary);
    letter-spacing: 4px;
    margin-bottom: 12px;
    font-weight: 600;
  }

  .search-input {
    width: 100%;
    padding: 8px 14px;
    border: 1px solid var(--color-border);
    border-radius: 20px;
    background: rgba(255, 255, 255, 0.5);
    font-family: var(--font-serif);
    font-size: 13px;
    color: var(--color-text-body);
    outline: none;
    transition: border-color 0.2s;
  }

  .search-input:focus {
    border-color: var(--color-primary);
  }

  .search-input::placeholder {
    color: var(--color-text-muted);
  }

  .search-results {
    margin-top: 8px;
    display: none;
  }

  .search-results.visible {
    display: block;
  }

  .search-results :global(.search-item) {
    display: block;
    padding: 6px 10px;
    font-size: 13px;
    color: var(--color-text-body);
    text-decoration: none;
    border-radius: 6px;
    transition: background 0.2s;
  }

  .search-results :global(.search-item:hover) {
    background: rgba(139, 115, 85, 0.08);
  }

  .sidebar-nav {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .sidebar-link {
    font-size: 13px;
    color: var(--color-text-secondary);
    text-decoration: none;
    padding: 5px 8px;
    border-radius: 6px;
    transition: all 0.2s;
  }

  .sidebar-link:hover {
    background: rgba(139, 115, 85, 0.08);
    color: var(--color-text-body);
  }

  .sidebar-link.active {
    color: var(--color-text-title);
    font-weight: 600;
    background: rgba(139, 115, 85, 0.1);
  }

  .tag-cloud {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }

  .tag.active {
    background: rgba(139, 115, 85, 0.15);
    font-weight: 600;
  }

  @media (max-width: 768px) {
    .sidebar {
      width: 100%;
      height: auto;
      position: static;
      border-right: none;
      border-bottom: 1px solid var(--color-border);
      flex-direction: row;
      flex-wrap: wrap;
      padding: 16px;
      gap: 16px;
    }

    .sidebar-section {
      flex: 1;
      min-width: 150px;
    }
  }
</style>
```

- [ ] **Step 2: Verify sidebar renders**

We will integrate the sidebar in the poems list page (Task 5). For now, just verify the file has no syntax errors by running `npx astro check` (if available) or by importing it in the next task.

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "feat: add sidebar with categories, tags, and search input"
```

---

## Task 5: Poem Card & Poems List Page

**Files:**
- Create: `src/components/PoemCard.astro`
- Create: `src/pages/poems.astro`

- [ ] **Step 1: Create PoemCard component**

Create `src/components/PoemCard.astro`:

```astro
---
interface Props {
  title: string;
  slug: string;
  category: string;
  tags: string[];
  date: Date;
  excerpt: string;
  hasAudio: boolean;
}

const { title, slug, category, tags, date, excerpt, hasAudio } = Astro.props;

const dateStr = date.toLocaleDateString('zh-CN', {
  year: 'numeric',
  month: 'long',
  day: 'numeric',
});
---

<a href={`/poems/${slug}`} class="poem-card">
  <div class="poem-card-header">
    <h3 class="poem-card-title">{title}</h3>
    {hasAudio && <span class="audio-badge" title="有朗诵音频">🔊</span>}
  </div>
  <p class="poem-card-excerpt">{excerpt}</p>
  <div class="poem-card-footer">
    <div class="poem-card-tags">
      <span class="tag">{category}</span>
      {tags.map(tag => <span class="tag">{tag}</span>)}
    </div>
    <span class="poem-card-date">{dateStr}</span>
  </div>
</a>

<style>
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

  .audio-badge {
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
</style>
```

- [ ] **Step 2: Create poems list page**

Create `src/pages/poems.astro`:

```astro
---
import BaseLayout from '../layouts/BaseLayout.astro';
import Sidebar from '../components/Sidebar.astro';
import PoemCard from '../components/PoemCard.astro';
import { getCollection } from 'astro:content';

const url = Astro.url;
const categoryFilter = url.searchParams.get('category');
const tagFilter = url.searchParams.get('tag');

let poems = await getCollection('poems');

if (categoryFilter) {
  poems = poems.filter(p => p.data.category === categoryFilter);
}

if (tagFilter) {
  poems = poems.filter(p => p.data.tags.includes(tagFilter));
}

poems.sort((a, b) => b.data.date.getTime() - a.data.date.getTime());

function getExcerpt(body: string): string {
  const lines = body.trim().split('\n').filter(l => l.trim());
  return lines.slice(0, 2).join('，').replace(/，$/, '');
}

const pageTitle = categoryFilter ?? tagFilter ?? '全部诗词';
---

<BaseLayout title={pageTitle}>
  <div class="poems-layout">
    <Sidebar currentCategory={categoryFilter ?? undefined} currentTag={tagFilter ?? undefined} />
    <main class="poems-main">
      <div class="poems-header">
        <h2 class="poems-heading">{pageTitle}</h2>
        <span class="poems-count">共 {poems.length} 首</span>
      </div>
      <div class="poems-list">
        {poems.map(poem => (
          <PoemCard
            title={poem.data.title}
            slug={poem.id}
            category={poem.data.category}
            tags={poem.data.tags}
            date={poem.data.date}
            excerpt={getExcerpt(poem.body ?? '')}
            hasAudio={!!poem.data.audio}
          />
        ))}
      </div>
      {poems.length === 0 && (
        <p class="no-results">暂无符合条件的诗词</p>
      )}
    </main>
  </div>
</BaseLayout>

<style>
  .poems-layout {
    display: flex;
    min-height: calc(100vh - 57px);
  }

  .poems-main {
    flex: 1;
    padding: 28px 36px;
    max-width: 800px;
  }

  .poems-header {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    margin-bottom: 24px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--color-border);
  }

  .poems-heading {
    font-size: 18px;
    color: var(--color-text-title);
    font-weight: 600;
    letter-spacing: 2px;
  }

  .poems-count {
    font-size: 13px;
    color: var(--color-text-muted);
  }

  .poems-list {
    display: flex;
    flex-direction: column;
    gap: 14px;
  }

  .no-results {
    text-align: center;
    color: var(--color-text-muted);
    padding: 60px 0;
    font-size: 15px;
  }

  @media (max-width: 768px) {
    .poems-layout { flex-direction: column; }
    .poems-main { padding: 20px 16px; }
  }
</style>
```

- [ ] **Step 3: Verify in browser**

Run `npx astro dev --port 4321`, navigate to `http://localhost:4321/poems`. Verify:
- Sidebar shows with categories and tags
- 5 poem cards display with titles, excerpts, tags, dates
- Clicking a category link filters poems
- Clicking a tag filters poems
- Mobile responsive layout works

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "feat: add poems list page with sidebar navigation and filtering"
```

---

## Task 6: Poem Detail Page & PoemNav

**Files:**
- Create: `src/components/PoemNav.astro`
- Create: `src/pages/poems/[...slug].astro`

- [ ] **Step 1: Create PoemNav component**

Create `src/components/PoemNav.astro`:

```astro
---
interface Props {
  prevPoem?: { title: string; slug: string } | null;
  nextPoem?: { title: string; slug: string } | null;
}

const { prevPoem, nextPoem } = Astro.props;
---

<nav class="poem-nav">
  <div class="poem-nav-side">
    {prevPoem ? (
      <a href={`/poems/${prevPoem.slug}`} class="poem-nav-link">
        <span class="poem-nav-arrow">←</span>
        <span class="poem-nav-label">上一首</span>
        <span class="poem-nav-title">{prevPoem.title}</span>
      </a>
    ) : <span />}
  </div>
  <div class="poem-nav-side right">
    {nextPoem ? (
      <a href={`/poems/${nextPoem.slug}`} class="poem-nav-link right">
        <span class="poem-nav-label">下一首</span>
        <span class="poem-nav-title">{nextPoem.title}</span>
        <span class="poem-nav-arrow">→</span>
      </a>
    ) : <span />}
  </div>
</nav>

<style>
  .poem-nav {
    display: flex;
    justify-content: space-between;
    padding: 20px 40px;
    border-top: 1px solid var(--color-border);
    margin-top: 40px;
  }

  .poem-nav-side {
    max-width: 45%;
  }

  .poem-nav-link {
    display: flex;
    align-items: center;
    gap: 8px;
    text-decoration: none;
    color: var(--color-primary);
    font-size: 14px;
    transition: opacity 0.2s;
  }

  .poem-nav-link:hover {
    opacity: 0.7;
    text-decoration: none;
  }

  .poem-nav-link.right {
    text-align: right;
  }

  .poem-nav-arrow {
    font-size: 18px;
  }

  .poem-nav-label {
    font-size: 12px;
    color: var(--color-text-muted);
  }

  .poem-nav-title {
    font-weight: 600;
  }

  @media (max-width: 768px) {
    .poem-nav { padding: 16px 20px; }
  }
</style>
```

- [ ] **Step 2: Create poem detail page**

Create `src/pages/poems/[...slug].astro`:

```astro
---
import BaseLayout from '../../layouts/BaseLayout.astro';
import PoemNav from '../../components/PoemNav.astro';
import { getCollection, render } from 'astro:content';

export async function getStaticPaths() {
  const poems = await getCollection('poems');
  const sorted = poems.sort((a, b) => b.data.date.getTime() - a.data.date.getTime());

  return sorted.map((poem, index) => ({
    params: { slug: poem.id },
    props: {
      poem,
      prevPoem: index < sorted.length - 1
        ? { title: sorted[index + 1].data.title, slug: sorted[index + 1].id }
        : null,
      nextPoem: index > 0
        ? { title: sorted[index - 1].data.title, slug: sorted[index - 1].id }
        : null,
    },
  }));
}

const { poem, prevPoem, nextPoem } = Astro.props;
const { Content } = await render(poem);

const dateStr = poem.data.date.toLocaleDateString('zh-CN', {
  year: 'numeric',
  month: 'long',
  day: 'numeric',
});
---

<BaseLayout title={poem.data.title}>
  <main class="poem-detail">
    <nav class="breadcrumb">
      <a href="/">首页</a>
      <span class="sep">/</span>
      <a href={`/poems?category=${encodeURIComponent(poem.data.category)}`}>{poem.data.category}</a>
      <span class="sep">/</span>
      <span>{poem.data.title}</span>
    </nav>

    <article class="poem-article">
      <h1 class="poem-title">{poem.data.title}</h1>
      <p class="poem-meta">{poem.data.category} · {dateStr}</p>
      <div class="poem-divider"></div>
      <div class="poem-body">
        <Content />
      </div>
      <div class="poem-tags">
        <span class="tag">{poem.data.category}</span>
        {poem.data.tags.map(tag => <span class="tag">{tag}</span>)}
      </div>
      {poem.data.note && (
        <div class="poem-note">
          <h4>创 作 手 记</h4>
          <p>{poem.data.note}</p>
        </div>
      )}
    </article>

    <PoemNav prevPoem={prevPoem} nextPoem={nextPoem} />
  </main>
</BaseLayout>

<style>
  .poem-detail {
    max-width: 700px;
    margin: 0 auto;
  }

  .breadcrumb {
    padding: 14px 0;
    margin: 0 40px;
    font-size: 13px;
    color: var(--color-text-muted);
    border-bottom: 1px solid var(--color-border);
  }

  .breadcrumb a {
    color: var(--color-primary);
    text-decoration: none;
  }

  .breadcrumb a:hover {
    text-decoration: underline;
  }

  .breadcrumb .sep {
    margin: 0 8px;
    color: var(--color-text-muted);
  }

  .poem-article {
    text-align: center;
    padding: 50px 40px 30px;
  }

  .poem-title {
    font-family: var(--font-brush);
    font-size: 36px;
    color: var(--color-text-title);
    letter-spacing: 8px;
    margin-bottom: 10px;
    font-weight: normal;
  }

  .poem-meta {
    font-size: 14px;
    color: var(--color-text-muted);
    letter-spacing: 2px;
  }

  .poem-divider {
    width: 50px;
    height: 1px;
    background: var(--color-primary-light);
    margin: 20px auto 30px;
  }

  .poem-body {
    font-size: 20px;
    color: var(--color-text-body);
    line-height: 2.4;
    letter-spacing: 3px;
  }

  .poem-body :global(p) {
    margin-bottom: 0;
  }

  .poem-tags {
    margin-top: 30px;
    display: flex;
    justify-content: center;
    gap: 8px;
    flex-wrap: wrap;
  }

  .poem-note {
    margin-top: 36px;
    padding-top: 24px;
    border-top: 1px solid var(--color-border);
    text-align: left;
  }

  .poem-note h4 {
    font-size: 14px;
    color: var(--color-primary);
    letter-spacing: 4px;
    margin-bottom: 10px;
    font-weight: 600;
  }

  .poem-note p {
    font-size: 14px;
    color: var(--color-text-secondary);
    line-height: 1.9;
  }

  @media (max-width: 768px) {
    .poem-article { padding: 30px 20px 20px; }
    .breadcrumb { margin: 0 20px; }
    .poem-title { font-size: 28px; letter-spacing: 4px; }
    .poem-body { font-size: 18px; }
  }
</style>
```

- [ ] **Step 3: Verify in browser**

Run `npx astro dev --port 4321`, navigate to `http://localhost:4321/poems`, click a poem card. Verify:
- Breadcrumb navigation works
- Title displays in brush font
- Poem body displays centered with proper spacing
- Tags display
- Creation note shows (for poems that have it)
- Previous/next navigation shows correct poems
- Mobile layout works

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "feat: add poem detail page with breadcrumb and prev/next navigation"
```

---

## Task 7: Audio Player (Floating Button)

**Files:**
- Create: `src/components/AudioPlayer.astro`
- Modify: `src/pages/poems/[...slug].astro`

- [ ] **Step 1: Create AudioPlayer component**

Create `src/components/AudioPlayer.astro`:

```astro
---
interface Props {
  audioSrc: string;
}

const { audioSrc } = Astro.props;
---

<div class="audio-player" id="audio-player" data-src={audioSrc}>
  <button class="float-btn" id="audio-btn" aria-label="播放朗诵">
    <svg class="icon-play" viewBox="0 0 24 24" width="18" height="18">
      <polygon points="6,3 20,12 6,21" fill="#f5f0e8" />
    </svg>
    <svg class="icon-pause" viewBox="0 0 24 24" width="18" height="18" style="display:none">
      <rect x="5" y="3" width="4" height="18" fill="#f5f0e8" />
      <rect x="15" y="3" width="4" height="18" fill="#f5f0e8" />
    </svg>
    <div class="sound-wave wave-1"></div>
    <div class="sound-wave wave-2"></div>
  </button>
  <span class="float-label">聆听</span>
  <audio id="audio-el" preload="none">
    <source src={audioSrc} type="audio/mpeg" />
  </audio>
</div>

<style>
  .audio-player {
    position: fixed;
    bottom: 36px;
    right: 36px;
    z-index: 50;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
  }

  .float-btn {
    width: 52px;
    height: 52px;
    border-radius: 50%;
    background: var(--color-primary);
    border: none;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    box-shadow: 0 4px 16px rgba(139, 115, 85, 0.35);
    transition: all 0.2s;
    position: relative;
  }

  .float-btn:hover {
    transform: scale(1.1);
    box-shadow: 0 6px 24px rgba(139, 115, 85, 0.45);
  }

  .float-btn .icon-play {
    margin-left: 3px;
  }

  .float-label {
    font-size: 11px;
    color: var(--color-primary);
    letter-spacing: 2px;
  }

  .sound-wave {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 52px;
    height: 52px;
    border-radius: 50%;
    border: 1.5px solid rgba(139, 115, 85, 0.3);
    opacity: 0;
    pointer-events: none;
  }

  .audio-player.playing .sound-wave {
    animation: wave 1.8s ease-out infinite;
  }

  .audio-player.playing .wave-2 {
    animation-delay: 0.6s;
  }

  @keyframes wave {
    0% { width: 52px; height: 52px; opacity: 0.6; }
    100% { width: 100px; height: 100px; opacity: 0; }
  }

  @media (max-width: 768px) {
    .audio-player { bottom: 20px; right: 20px; }
    .float-btn { width: 44px; height: 44px; }
    .sound-wave { width: 44px; height: 44px; }
  }
</style>

<script>
  const player = document.getElementById('audio-player');
  const btn = document.getElementById('audio-btn');
  const audio = document.getElementById('audio-el') as HTMLAudioElement;
  const iconPlay = btn?.querySelector('.icon-play') as SVGElement;
  const iconPause = btn?.querySelector('.icon-pause') as SVGElement;

  btn?.addEventListener('click', () => {
    if (audio.paused) {
      audio.play();
      player?.classList.add('playing');
      iconPlay.style.display = 'none';
      iconPause.style.display = 'block';
    } else {
      audio.pause();
      player?.classList.remove('playing');
      iconPlay.style.display = 'block';
      iconPause.style.display = 'none';
    }
  });

  audio?.addEventListener('ended', () => {
    player?.classList.remove('playing');
    iconPlay.style.display = 'block';
    iconPause.style.display = 'none';
  });
</script>
```

- [ ] **Step 2: Add AudioPlayer to poem detail page**

In `src/pages/poems/[...slug].astro`, add the import at the top of the frontmatter:

```typescript
import AudioPlayer from '../../components/AudioPlayer.astro';
```

Add the component just before the closing `</main>` tag, after `<PoemNav>`:

```astro
    <PoemNav prevPoem={prevPoem} nextPoem={nextPoem} />

    {poem.data.audio && (
      <AudioPlayer audioSrc={`/audio/${poem.data.audio}`} />
    )}
  </main>
```

- [ ] **Step 3: Test with a sample audio file**

Update `src/content/poems/qiu-ye-huai-yuan.md` frontmatter to add:
```yaml
audio: "qiu-ye-huai-yuan.mp3"
```

Place any short MP3 in `public/audio/qiu-ye-huai-yuan.mp3` for testing (or verify that the button appears and only shows on poems with `audio` field). Poems without `audio` field should NOT show the button.

Run `npx astro dev --port 4321`, navigate to the poem detail page for "秋夜怀远". Verify:
- Floating button appears in bottom-right
- Button toggles play/pause
- Sound wave animation plays during playback
- Button does NOT appear on poems without audio (e.g., "春日偶成")

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "feat: add floating audio player with wave animation on poem detail"
```

---

## Task 8: Home Page

**Files:**
- Modify: `src/pages/index.astro`

- [ ] **Step 1: Build the home page**

Replace `src/pages/index.astro`:

```astro
---
import BaseLayout from '../layouts/BaseLayout.astro';
import PoemCard from '../components/PoemCard.astro';
import { getCollection } from 'astro:content';

const allPoems = await getCollection('poems');
const featured = allPoems
  .filter(p => p.data.featured)
  .sort((a, b) => b.data.date.getTime() - a.data.date.getTime())
  .slice(0, 3);

const latest = allPoems
  .sort((a, b) => b.data.date.getTime() - a.data.date.getTime())
  .slice(0, 5);

function getExcerpt(body: string): string {
  const lines = body.trim().split('\n').filter(l => l.trim());
  return lines.slice(0, 2).join('，').replace(/，$/, '');
}
---

<BaseLayout title="首页">
  <main class="home">
    <section class="hero">
      <h1 class="hero-title">墨韵诗笺</h1>
      <p class="hero-subtitle">一 纸 素 笺 · 半 卷 清 风</p>
      <div class="hero-divider"></div>
      <p class="hero-desc">以诗为径，以词为桥，记录心中山水</p>
    </section>

    {featured.length > 0 && (
      <section class="section">
        <h2 class="section-title">精 选 诗 词</h2>
        <div class="poem-list">
          {featured.map(poem => (
            <PoemCard
              title={poem.data.title}
              slug={poem.id}
              category={poem.data.category}
              tags={poem.data.tags}
              date={poem.data.date}
              excerpt={getExcerpt(poem.body ?? '')}
              hasAudio={!!poem.data.audio}
            />
          ))}
        </div>
      </section>
    )}

    <section class="section">
      <h2 class="section-title">最 新 发 布</h2>
      <div class="poem-list">
        {latest.map(poem => (
          <PoemCard
            title={poem.data.title}
            slug={poem.id}
            category={poem.data.category}
            tags={poem.data.tags}
            date={poem.data.date}
            excerpt={getExcerpt(poem.body ?? '')}
            hasAudio={!!poem.data.audio}
          />
        ))}
      </div>
    </section>

    <div class="home-cta">
      <a href="/poems" class="cta-link">浏览全部诗词 →</a>
    </div>
  </main>
</BaseLayout>

<style>
  .home {
    max-width: 700px;
    margin: 0 auto;
    padding: 0 40px 60px;
  }

  .hero {
    text-align: center;
    padding: 80px 0 50px;
  }

  .hero-title {
    font-family: var(--font-brush);
    font-size: 56px;
    color: var(--color-text-title);
    letter-spacing: 12px;
    font-weight: normal;
  }

  .hero-subtitle {
    font-family: var(--font-subtitle);
    font-size: 16px;
    color: var(--color-text-muted);
    letter-spacing: 6px;
    margin-top: 8px;
  }

  .hero-divider {
    width: 60px;
    height: 1px;
    background: var(--color-primary-light);
    margin: 24px auto;
  }

  .hero-desc {
    font-size: 15px;
    color: var(--color-text-secondary);
    letter-spacing: 2px;
  }

  .section {
    margin-top: 50px;
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

  .home-cta {
    text-align: center;
    margin-top: 50px;
  }

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

  .cta-link:hover {
    background: rgba(139, 115, 85, 0.08);
    text-decoration: none;
  }

  @media (max-width: 768px) {
    .home { padding: 0 20px 40px; }
    .hero { padding: 50px 0 30px; }
    .hero-title { font-size: 40px; letter-spacing: 6px; }
  }
</style>
```

- [ ] **Step 2: Verify in browser**

Run `npx astro dev --port 4321`. Verify:
- Hero section with brush font title and subtitle
- Featured poems section (3 poems marked `featured: true`)
- Latest poems section (all 5 sorted by date)
- "浏览全部诗词" link navigates to `/poems`
- Mobile responsive

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "feat: add home page with hero, featured and latest poems"
```

---

## Task 9: About Page & Guestbook Page

**Files:**
- Create: `src/pages/about.astro`
- Create: `src/pages/guestbook.astro`

- [ ] **Step 1: Create About page**

Create `src/pages/about.astro`:

```astro
---
import BaseLayout from '../layouts/BaseLayout.astro';
---

<BaseLayout title="关于">
  <main class="about-page">
    <h1 class="page-title">关 于</h1>
    <div class="page-divider"></div>

    <section class="about-section">
      <h2>作 者</h2>
      <p>
        此处填写你的个人介绍。可以写一段简短的自我描述，
        你是谁，为什么写诗词，诗词对你意味着什么。
      </p>
    </section>

    <section class="about-section">
      <h2>诗 词 观</h2>
      <p>
        此处填写你对诗词创作的理解和追求。
        你的写作理念，偏好的风格，欣赏的古人诗词等。
      </p>
    </section>

    <section class="about-section">
      <h2>联 系</h2>
      <p>
        如果你想与我交流诗词，欢迎在<a href="/guestbook">留言板</a>留言。
      </p>
    </section>
  </main>
</BaseLayout>

<style>
  .about-page {
    max-width: 600px;
    margin: 0 auto;
    padding: 50px 40px 80px;
  }

  .page-title {
    font-family: var(--font-brush);
    font-size: 36px;
    color: var(--color-text-title);
    letter-spacing: 8px;
    text-align: center;
    font-weight: normal;
  }

  .page-divider {
    width: 50px;
    height: 1px;
    background: var(--color-primary-light);
    margin: 20px auto 40px;
  }

  .about-section {
    margin-bottom: 36px;
  }

  .about-section h2 {
    font-size: 16px;
    color: var(--color-primary);
    letter-spacing: 4px;
    font-weight: 600;
    margin-bottom: 12px;
  }

  .about-section p {
    font-size: 15px;
    color: var(--color-text-secondary);
    line-height: 2;
    letter-spacing: 1px;
  }

  @media (max-width: 768px) {
    .about-page { padding: 30px 20px 60px; }
    .page-title { font-size: 28px; }
  }
</style>
```

- [ ] **Step 2: Create Guestbook page**

Create `src/pages/guestbook.astro`:

```astro
---
import BaseLayout from '../layouts/BaseLayout.astro';
---

<BaseLayout title="留言">
  <main class="guestbook-page">
    <h1 class="page-title">留 言</h1>
    <div class="page-divider"></div>
    <p class="page-desc">欢迎留下你的感想与交流，期待与你诗词相会。</p>

    <div class="giscus-container">
      <script
        src="https://giscus.app/client.js"
        data-repo="OWNER/REPO"
        data-repo-id="PLACEHOLDER"
        data-category="General"
        data-category-id="PLACEHOLDER"
        data-mapping="pathname"
        data-strict="0"
        data-reactions-enabled="1"
        data-emit-metadata="0"
        data-input-position="top"
        data-theme="light"
        data-lang="zh-CN"
        crossorigin="anonymous"
        async
      ></script>
      <noscript>
        <p style="text-align:center;color:var(--color-text-muted);padding:40px 0;">
          留言功能需要 JavaScript 支持。请在 GitHub 上的 Discussions 页面留言。
        </p>
      </noscript>
    </div>
  </main>
</BaseLayout>

<style>
  .guestbook-page {
    max-width: 700px;
    margin: 0 auto;
    padding: 50px 40px 80px;
  }

  .page-title {
    font-family: var(--font-brush);
    font-size: 36px;
    color: var(--color-text-title);
    letter-spacing: 8px;
    text-align: center;
    font-weight: normal;
  }

  .page-divider {
    width: 50px;
    height: 1px;
    background: var(--color-primary-light);
    margin: 20px auto 16px;
  }

  .page-desc {
    text-align: center;
    font-size: 14px;
    color: var(--color-text-muted);
    letter-spacing: 2px;
    margin-bottom: 40px;
  }

  .giscus-container {
    min-height: 300px;
  }

  @media (max-width: 768px) {
    .guestbook-page { padding: 30px 20px 60px; }
    .page-title { font-size: 28px; }
  }
</style>
```

**Note:** The Giscus `data-repo`, `data-repo-id`, `data-category`, and `data-category-id` are placeholders. They need to be replaced with actual values after creating a GitHub repository and enabling Discussions. Visit https://giscus.app to generate the correct configuration.

- [ ] **Step 3: Verify in browser**

Run `npx astro dev --port 4321`. Verify:
- `/about` shows the about page with placeholder content
- `/guestbook` shows the guestbook page (Giscus won't load with placeholder config, but layout should be correct)
- Header nav links work for both pages

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "feat: add about page and guestbook page with Giscus placeholder"
```

---

## Task 10: Client-Side Search

**Files:**
- Modify: `src/components/Sidebar.astro`
- Modify: `src/pages/poems.astro`

- [ ] **Step 1: Install Fuse.js**

```bash
cd "/c/Users/I350333/AI Workspace/poetry-website"
npm install fuse.js
```

- [ ] **Step 2: Generate search index at build time**

Add a search index script block to `src/pages/poems.astro`. Insert this right before the closing `</BaseLayout>`:

```astro
<script define:vars={{ searchData: poems.map(p => ({
  title: p.data.title,
  slug: p.id,
  category: p.data.category,
  tags: p.data.tags,
  body: (p.body ?? '').replace(/\n/g, ' ').trim(),
})) }}>
  window.__POEM_SEARCH_DATA__ = searchData;
</script>

<script>
  import Fuse from 'fuse.js';

  document.addEventListener('DOMContentLoaded', () => {
    const data = (window as any).__POEM_SEARCH_DATA__;
    if (!data) return;

    const fuse = new Fuse(data, {
      keys: [
        { name: 'title', weight: 2 },
        { name: 'body', weight: 1 },
        { name: 'tags', weight: 1.5 },
      ],
      threshold: 0.4,
      includeMatches: true,
    });

    const input = document.getElementById('poem-search') as HTMLInputElement;
    const results = document.getElementById('search-results');
    if (!input || !results) return;

    input.addEventListener('input', () => {
      const query = input.value.trim();
      if (!query) {
        results.classList.remove('visible');
        results.innerHTML = '';
        return;
      }

      const matches = fuse.search(query).slice(0, 8);
      if (matches.length === 0) {
        results.classList.add('visible');
        results.innerHTML = '<div class="search-item" style="color:var(--color-text-muted)">无结果</div>';
        return;
      }

      results.classList.add('visible');
      results.innerHTML = matches
        .map(m => `<a class="search-item" href="/poems/${m.item.slug}">${m.item.title} <span style="font-size:11px;color:var(--color-text-muted)">${m.item.category}</span></a>`)
        .join('');
    });
  });
</script>
```

**Note:** The `searchData` variable is passed from the server (Astro frontmatter) to the client via `define:vars`. This must be placed inside the poems page so the data is available. If using `getCollection` to get all poems, change the `define:vars` to use `allPoems` — the full unfiltered list. Update the frontmatter:

In `src/pages/poems.astro`, add to the frontmatter (before filtering):

```typescript
const allPoems = await getCollection('poems');
```

And use `allPoems` (not `poems`) for the search data so search always covers all poems regardless of current filter.

The full updated frontmatter becomes:

```typescript
import BaseLayout from '../layouts/BaseLayout.astro';
import Sidebar from '../components/Sidebar.astro';
import PoemCard from '../components/PoemCard.astro';
import { getCollection } from 'astro:content';

const url = Astro.url;
const categoryFilter = url.searchParams.get('category');
const tagFilter = url.searchParams.get('tag');

const allPoems = await getCollection('poems');
let poems = [...allPoems];

if (categoryFilter) {
  poems = poems.filter(p => p.data.category === categoryFilter);
}

if (tagFilter) {
  poems = poems.filter(p => p.data.tags.includes(tagFilter));
}

poems.sort((a, b) => b.data.date.getTime() - a.data.date.getTime());

function getExcerpt(body: string): string {
  const lines = body.trim().split('\n').filter(l => l.trim());
  return lines.slice(0, 2).join('，').replace(/，$/, '');
}

const pageTitle = categoryFilter ?? tagFilter ?? '全部诗词';
```

And the `define:vars` uses `allPoems`:

```astro
<script define:vars={{ searchData: allPoems.map(p => ({
  title: p.data.title,
  slug: p.id,
  category: p.data.category,
  tags: p.data.tags,
  body: (p.body ?? '').replace(/\n/g, ' ').trim(),
})) }}>
  window.__POEM_SEARCH_DATA__ = searchData;
</script>
```

- [ ] **Step 3: Verify search in browser**

Run `npx astro dev --port 4321`, navigate to `/poems`. Type "秋" in the search box. Verify:
- Dropdown appears with matching poems (秋夜怀远, 夜雨寄北, 登高望远)
- Clicking a search result navigates to the poem detail page
- Clearing the input hides the dropdown
- Searching "江" shows 江畔独步

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "feat: add client-side fuzzy search with Fuse.js"
```

---

## Task 11: Build & Final Verification

**Files:**
- Modify: `astro.config.mjs` (if needed for GitHub Pages)

- [ ] **Step 1: Run a full build**

```bash
cd "/c/Users/I350333/AI Workspace/poetry-website"
npx astro build
```

Expected: Build succeeds with no errors. Output in `dist/` directory.

- [ ] **Step 2: Preview production build**

```bash
npx astro preview --port 4321
```

Navigate to `http://localhost:4321` and verify all pages:
- Home page: hero, featured, latest
- Poems list: sidebar, cards, category/tag filtering
- Poem detail: title, body, note, tags, prev/next
- Audio player: floating button (appears only on poems with audio)
- About page: content renders
- Guestbook page: layout renders
- Search: works on poems page
- Mobile: all pages responsive

- [ ] **Step 3: Add .gitignore**

Create `.gitignore` if not already present:

```
node_modules/
dist/
.astro/
.superpowers/
```

- [ ] **Step 4: Final commit**

```bash
git add -A
git commit -m "feat: production build verified, add gitignore"
```

---

## Summary

| Task | Description | Key Files |
|------|-------------|-----------|
| 1 | Project scaffold | astro.config, global.css, BaseLayout |
| 2 | Content collection & sample poems | content.config.ts, 5 poem .md files |
| 3 | Header component | Header.astro, BaseLayout update |
| 4 | Sidebar component | Sidebar.astro |
| 5 | PoemCard & poems list page | PoemCard.astro, poems.astro |
| 6 | Poem detail page & navigation | [...slug].astro, PoemNav.astro |
| 7 | Audio player | AudioPlayer.astro |
| 8 | Home page | index.astro |
| 9 | About & guestbook pages | about.astro, guestbook.astro |
| 10 | Client-side search | Fuse.js integration |
| 11 | Build & final verification | Production build, .gitignore |
