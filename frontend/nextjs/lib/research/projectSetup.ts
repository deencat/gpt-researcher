/** Guided setup drafts for a project that only has a title. Domain-aware, not comedy-only. :-) */

export type SetupAnswers = {
  goal: string;
  languages: string[];
  formats: string[];
  materials: string[];
  constraints: string;
};

export type ProjectDomain = 'comedy' | 'travel' | 'general';

export const LANGUAGE_OPTIONS = [
  { id: 'en', label: 'English' },
  { id: 'zh-cn', label: 'Mainland Mandarin (普通话)' },
  { id: 'zh-yue', label: 'Hong Kong Cantonese (粵語)' },
  { id: 'zh-tw', label: 'Taiwan Mandarin (國語)' },
] as const;

export const FORMAT_OPTIONS = [
  { id: 'report', label: 'Research brief / report' },
  { id: 'itinerary', label: 'Itinerary / plan' },
  { id: 'shorts', label: 'Shorts / Reels / TikTok' },
  { id: 'youtube', label: 'YouTube videos' },
  { id: 'script', label: 'Scripts & talking points' },
  { id: 'notes', label: 'Notes & checklists' },
] as const;

export const MATERIAL_OPTIONS = [
  { id: 'sources', label: 'Trusted sources & citations' },
  { id: 'facts', label: 'Key facts & comparisons' },
  { id: 'places', label: 'Places, routes & logistics' },
  { id: 'budget', label: 'Costs, timing & bookings' },
  { id: 'hooks', label: 'Hooks & opening formulas' },
  { id: 'structures', label: 'Structures & outlines' },
  { id: 'trends', label: 'Trends by platform / season' },
  { id: 'creators', label: 'Creators & reference channels' },
  { id: 'culture', label: 'Culture, etiquette & taboos' },
  { id: 'dialect', label: 'Dialect / local language notes' },
  { id: 'packaging', label: 'Titles, captions & packaging' },
  { id: 'pipeline', label: 'Research → draft → ship workflow' },
] as const;

const labelOf = (options: readonly { id: string; label: string }[], id: string) =>
  options.find((o) => o.id === id)?.label ?? id;

const COMEDY_RE = /funny|comedy|humor|humour|joke|skit|meme|搞笑|喜劇|短劇|shorts?\s*comedy/;
const TRAVEL_RE =
  /travel|trip|tour|itinerary|vacation|holiday|flight|hotel|visa|旅|遊|旅行|之旅|首爾|ソウル|seoul|tokyo|osaka|japan|korea|韓國|日本|bangkok|singapore|paris|london/;

export function detectDomain(title: string, goal = ''): ProjectDomain {
  const text = `${title}\n${goal}`.toLowerCase();
  if (COMEDY_RE.test(text)) return 'comedy';
  if (TRAVEL_RE.test(text)) return 'travel';
  return 'general';
}

function guessLanguages(title: string): string[] {
  const t = title.toLowerCase();
  const languages: string[] = [];
  if (/\benglish\b|\ben\b/.test(t)) languages.push('en');
  if (/cantonese|粵|hong\s*kong|\bhk\b/.test(t)) languages.push('zh-yue');
  if (/taiwan|國語|繁體|台北|高雄/.test(t)) languages.push('zh-tw');
  if (/mandarin|普通话|簡體|\bchina\b|chinese|中文|北京|上海/.test(t)) {
    if (!languages.includes('zh-cn') && !languages.includes('zh-tw')) languages.push('zh-cn');
  }
  // Traditional Chinese title with no explicit market → prefer 國語 + English for travel/general. :-)
  if (!languages.length && /[\u3400-\u9fff]/.test(title)) {
    if (/[旅遊之首爾台]/u.test(title) || /台灣|臺/.test(title)) languages.push('zh-tw', 'en');
    else languages.push('zh-cn', 'en');
  }
  return languages;
}

function defaultsForDomain(domain: ProjectDomain, title: string): Partial<SetupAnswers> {
  const name = title.trim() || 'this project';
  if (domain === 'comedy') {
    return {
      goal: `Build a reusable research library for “${name}”: hooks, formats, cultural notes, and packaging ideas for funny short-form video.`,
      formats: ['shorts', 'youtube', 'script'],
      materials: ['hooks', 'structures', 'trends', 'creators', 'culture', 'dialect', 'packaging'],
    };
  }
  if (domain === 'travel') {
    return {
      goal: `Plan and research “${name}”: itinerary options, places worth the time, logistics, budget notes, and culture tips — practical enough to use on the trip.`,
      formats: ['itinerary', 'report', 'notes'],
      materials: ['places', 'budget', 'facts', 'culture', 'sources', 'pipeline'],
    };
  }
  return {
    goal: `Research hub for “${name}”: collect reliable sources, key findings, and next actions you can reuse across runs.`,
    formats: ['report', 'notes'],
    materials: ['sources', 'facts', 'structures', 'pipeline'],
  };
}

export function guessFromTitle(title: string): Partial<SetupAnswers> {
  const domain = detectDomain(title);
  const base = defaultsForDomain(domain, title);
  return {
    ...base,
    languages: guessLanguages(title),
    constraints: '',
  };
}

export function draftFromAnswers(title: string, answers: SetupAnswers) {
  const name = title.trim() || 'Untitled';
  const domain = detectDomain(title, answers.goal);
  const langs = answers.languages.map((id) => labelOf(LANGUAGE_OPTIONS, id));
  const formats = answers.formats.map((id) => labelOf(FORMAT_OPTIONS, id));
  const materials = answers.materials.map((id) => labelOf(MATERIAL_OPTIONS, id));
  const langLine = langs.length ? langs.join('; ') : 'languages still to confirm';
  const formatLine = formats.length ? formats.join('; ') : 'output formats still to confirm';

  const description = [
    answers.goal.trim() || `Research hub for ${name}.`,
    `Markets / languages: ${langLine}.`,
    `Output formats: ${formatLine}.`,
    materials.length ? `Collect: ${materials.join('; ')}.` : '',
    answers.constraints.trim() ? `Constraints: ${answers.constraints.trim()}` : '',
  ]
    .filter(Boolean)
    .join(' ');

  const mission =
    domain === 'comedy'
      ? 'Mission: help build a reusable source of data and materials for funny short-form video and social content.'
      : domain === 'travel'
        ? 'Mission: help plan and research this trip with practical itineraries, logistics, culture notes, and cited options — not generic tourism filler.'
        : 'Mission: help research this topic thoroughly, keep findings reusable across runs, and end with clear next actions.';

  const runRules =
    domain === 'comedy'
      ? [
          '1) Separate findings by language/market when humor differs.',
          '2) Prefer concrete examples (hooks, beat sheets, creator references, titles) over vague advice.',
          '3) Flag culture-sensitive jokes and platform policy risks.',
          '4) End with actionable next materials to gather (docs to upload, creators to watch, prompts to research next).',
          '5) Cite sources with links when possible.',
        ]
      : domain === 'travel'
        ? [
            '1) Prefer current, practical details (hours, transit, booking tips, seasonal caveats) over vague “must-see” lists.',
            '2) Split options by day / area when helpful; note time and cost tradeoffs.',
            '3) Call out scams, closures, visa/entry, and etiquette risks.',
            '4) End with a short next-actions list (what to book, what to verify, what to research next).',
            '5) Cite sources with links when possible.',
          ]
        : [
            '1) Lead with the strongest evidence and disagreements between sources.',
            '2) Prefer concrete, checkable claims over vague summaries.',
            '3) Flag uncertainty, bias, and what would change the conclusion.',
            '4) End with actionable next materials or follow-up research prompts.',
            '5) Cite sources with links when possible.',
          ];

  const chineseNote = answers.languages.some((id) => id.startsWith('zh-'))
    ? 'When Chinese is involved, always distinguish Mainland Mandarin (普通话), Hong Kong Cantonese (粵語), and Taiwan Mandarin (國語) — do not collapse them.'
    : '';

  const instructions = [
    `You are a research assistant for the project “${name}”.`,
    mission,
    `Primary languages/markets: ${langLine}.`,
    chineseNote,
    `Target formats: ${formatLine}.`,
    materials.length ? `Prioritize collecting: ${materials.join('; ')}.` : '',
    'For every research run:',
    ...runRules,
    answers.constraints.trim() ? `Extra constraints from the owner: ${answers.constraints.trim()}` : '',
  ]
    .filter(Boolean)
    .join('\n');

  const researchPrompts =
    domain === 'comedy'
      ? [
          `Best-performing funny short-form formats recently on YouTube Shorts, TikTok, and Instagram Reels for ${langLine}`,
          `How comedy hooks differ across the selected languages/markets for “${name}”`,
          `Creators and channels to study for funny shorts in these markets (with why they work)`,
          `Cultural taboos and platform rules that kill comedy in these markets`,
          `A reusable research → joke bank → script → package workflow for this project`,
        ]
      : domain === 'travel'
        ? [
            `Best 5–7 day itinerary options for “${name}” with transit between stops and time budgets`,
            `Neighborhoods / areas worth staying in for “${name}”, with tradeoffs (cost, transit, vibe)`,
            `Food, culture, and etiquette notes for “${name}” that a first-time visitor should know`,
            `Current logistics: visas/entry if relevant, transit passes, booking pitfalls, and common scams`,
            `A day-by-day packing / booking checklist derived from the best sources for “${name}”`,
          ]
        : [
            `Core overview of “${name}”: what matters most, with cited sources`,
            `Key debates or uncertainties around “${name}” and what evidence would settle them`,
            `Practical next steps or options someone acting on “${name}” should consider`,
            `A reusable research checklist and source list for ongoing work on “${name}”`,
          ];

  const documentIdeas =
    domain === 'comedy'
      ? [
          'Paste or upload transcripts of favorite funny shorts (one file per language).',
          'A swipe file of hooks/titles that worked.',
          'Notes on audiences you want (age, city, platform).',
          'Any brand/safety rules (words you never want used).',
        ]
      : domain === 'travel'
        ? [
            'Flight / hotel holds or confirmation screenshots.',
            'Must-see vs skip list from friends or past trips.',
            'Dietary needs, mobility limits, or travel companions.',
            'Budget range and travel dates.',
          ]
        : [
            'Background docs, PDFs, or notes you already trust.',
            'Questions you need answered by a deadline.',
            'Constraints (budget, market, audience, compliance).',
            'Examples of “good” output for this project.',
          ];

  return { description, instructions, researchPrompts, documentIdeas, domain };
}
