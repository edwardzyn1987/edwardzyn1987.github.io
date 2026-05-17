import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const poems = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/poems' }),
  schema: z.object({
    title: z.string(),
    category: z.enum(['五言绝句', '七言绝句', '五言律诗', '七言律诗', '五言古诗', '词']),
    tags: z.array(z.string()),
    date: z.coerce.date(),
    video: z.string().optional(),
    note: z.string().optional(),
    featured: z.boolean().default(false),
    originalPoem: z.object({
      title: z.string(),
      author: z.string(),
      text: z.string(),
    }).optional(),
  }),
});

export const collections = { poems };
