/** Guided setup drafts for a project that only has a title. :-) */

export type SetupAnswers = {
  goal: string;
  languages: string[];
  formats: string[];
  materials: string[];
  constraints: string;
};

export const LANGUAGE_OPTIONS = [
  { id: 'en', label: 'English' },
  { id: 'zh-cn', label: 'Mainland Mandarin (普通话)' },
  { id: 'zh-yue', label: 'Hong Kong Cantonese (粵語)' },
  { id: 'zh-tw', label: 'Taiwan Mandarin (國語)' },
] as const;

export const FORMAT_OPTIONS = [
  { id: 'shorts', label: 'Shorts / Reels / TikTok' },
  { id: 'youtube', label: 'YouTube videos' },
  { id: 'script', label: 'Scripts & punch-up notes' },
] as const;

export const MATERIAL_OPTIONS = [
  { id: 'hooks', label: 'Hooks & opening formulas' },
  { id: 'structures', label: 'Joke / sketch structures' },
  { id: 'trends', label: 'Trending formats by platform' },
  { id: 'creators', label: 'Creators & reference channels' },
  { id: 'culture', label: 'Culture-specific humor & taboos' },
  { id: 'dialect', label: 'Dialect / slang punchlines' },
  { id: 'packaging', label: 'Titles, thumbnails, captions' },
  { id: 'pipeline', label: 'Research → script → shoot workflow' },
] as const;

const labelOf = (options: readonly { id: string; label: string }[], id: string) =>
  options.find((o) => o.id === id)?.label ?? id;

export function guessFromTitle(title: string): Partial<SetupAnswers> {
  const t = title.toLowerCase();
  const languages: string[] = [];
  if (/\benglish\b|en\b/.test(t)) languages.push('en');
  if (/cantonese|粵|hong\s*kong|hk\b/.test(t)) languages.push('zh-yue');
  if (/taiwan|國語|繁體/.test(t)) languages.push('zh-tw');
  if (/mandarin|普通话|簡體|china|chinese|中文/.test(t)) {
    if (!languages.includes('zh-cn') && !languages.includes('zh-tw')) languages.push('zh-cn');
  }
  if (!languages.length && /funny|comedy|humor|humour|joke|video|short|creator|youtube/.test(t)) {
    languages.push('en', 'zh-cn', 'zh-yue', 'zh-tw');
  }

  const formats: string[] = [];
  if (/short|reel|tiktok|shorts/.test(t)) formats.push('shorts');
  if (/youtube|video|creator/.test(t)) formats.push('youtube', 'shorts');
  if (!formats.length) formats.push('shorts', 'youtube');

  const materials = ['hooks', 'structures', 'trends', 'creators', 'culture', 'dialect', 'packaging'];
  const goal = title.trim()
    ? `Build a living research library for “${title.trim()}”: source formats, jokes, cultural notes, and packaging ideas that help produce world-class funny videos and shorts.`
    : '';

  return { goal, languages, formats, materials, constraints: '' };
}

export function draftFromAnswers(title: string, answers: SetupAnswers) {
  const langs = answers.languages.map((id) => labelOf(LANGUAGE_OPTIONS, id));
  const formats = answers.formats.map((id) => labelOf(FORMAT_OPTIONS, id));
  const materials = answers.materials.map((id) => labelOf(MATERIAL_OPTIONS, id));
  const langLine = langs.length ? langs.join('; ') : 'languages still to confirm';
  const formatLine = formats.length ? formats.join('; ') : 'video formats still to confirm';

  const description = [
    answers.goal.trim() || `Research hub for ${title.trim() || 'this project'}.`,
    `Markets / languages: ${langLine}.`,
    `Output formats: ${formatLine}.`,
    materials.length ? `Collect: ${materials.join('; ')}.` : '',
    answers.constraints.trim() ? `Constraints: ${answers.constraints.trim()}` : '',
  ]
    .filter(Boolean)
    .join(' ');

  const instructions = [
    `You are a research assistant for the project “${title.trim() || 'Untitled'}”.`,
    `Mission: help build a reusable source of data and materials for creating the funniest possible videos/shorts for YouTube and social media.`,
    `Primary languages/markets: ${langLine}.`,
    `When Chinese is involved, always distinguish Mainland Mandarin (普通话), Hong Kong Cantonese (粵語), and Taiwan Mandarin (國語) — do not collapse them. Note slang, tone, taboos, and what travels vs what stays local.`,
    `Target formats: ${formatLine}.`,
    materials.length ? `Prioritize collecting: ${materials.join('; ')}.` : '',
    'For every research run:',
    '1) Separate findings by language/market when humor differs.',
    '2) Prefer concrete examples (hooks, beat sheets, creator references, titles) over vague advice.',
    '3) Flag culture-sensitive jokes and platform policy risks.',
    '4) End with actionable next materials to gather (docs to upload, creators to watch, prompts to research next).',
    '5) Cite sources with links when possible.',
    answers.constraints.trim() ? `Extra constraints from the creator: ${answers.constraints.trim()}` : '',
  ]
    .filter(Boolean)
    .join('\n');

  const researchPrompts = [
    `Best-performing funny short-form formats in 2024–2026 on YouTube Shorts, TikTok, and Instagram Reels for ${langLine}`,
    `How comedy hooks differ across English, Mainland Mandarin, Hong Kong Cantonese, and Taiwan Mandarin short videos`,
    `Creators and channels to study for world-class funny shorts in English and Chinese markets (with why they work)`,
    `Cultural taboos and platform rules that kill comedy in Mainland China, Hong Kong, Taiwan, and English-speaking YouTube`,
    `A reusable research → joke bank → script → package workflow for multilingual funny shorts`,
  ];

  const documentIdeas = [
    'Paste or upload transcripts of your favorite funny shorts (one file per language).',
    'A swipe file of hooks/titles that made you laugh.',
    'Notes on audiences you want (age, city, platform).',
    'Any brand/safety rules (words you never want used).',
  ];

  return { description, instructions, researchPrompts, documentIdeas };
}
