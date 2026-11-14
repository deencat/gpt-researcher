/** Playbook templates mirrored from gpt_researcher/playbooks. :-) */

export type PlaybookOption = {
  id: string;
  name: string;
  description: string;
};

/** Bundled playbooks known to the frontend without a network round-trip. */
export const PLAYBOOK_OPTIONS: PlaybookOption[] = [
  {
    id: 'comedy_shorts',
    name: 'Comedy shorts',
    description: 'Multilingual funny short-form briefs — hooks, titles, script outline',
  },
];

export const PLAYBOOK_VALUES = ['', ...PLAYBOOK_OPTIONS.map((p) => p.id)];

export const LANGUAGE_OPTIONS = [
  { id: 'en', label: 'English' },
  { id: 'zh-cn', label: 'Mainland Mandarin (普通话)' },
  { id: 'zh-yue', label: 'Hong Kong Cantonese (粵語)' },
  { id: 'zh-tw', label: 'Taiwan Mandarin (國語)' },
] as const;

export const DEFAULT_PLAYBOOK_LANGUAGES = LANGUAGE_OPTIONS.map((l) => l.id);

export function playbookLabel(id?: string) {
  if (!id) return 'None';
  return PLAYBOOK_OPTIONS.find((p) => p.id === id)?.name || id;
}
