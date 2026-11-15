import { describe, expect, it } from 'vitest';
import { detectDomain, draftFromAnswers, guessFromTitle } from './projectSetup';

describe('detectDomain', () => {
  it('detects comedy only when comedy cues are present', () => {
    expect(detectDomain('Funny beauty shorts EN 粤语')).toBe('comedy');
    expect(detectDomain('Salon comedy channel')).toBe('comedy');
  });

  it('detects travel for Seoul / 之旅 style titles', () => {
    expect(detectDomain('首爾之旅')).toBe('travel');
    expect(detectDomain('Seoul trip 2026')).toBe('travel');
  });

  it('defaults to general otherwise', () => {
    expect(detectDomain('Q4 competitor landscape')).toBe('general');
  });
});

describe('guessFromTitle', () => {
  it('does not inject funny-video wording into a Seoul trip project', () => {
    const g = guessFromTitle('首爾之旅');
    expect(g.goal).toMatch(/首爾之旅/);
    expect(g.goal).not.toMatch(/funny videos|jokes|shorts/i);
    expect(g.formats).toEqual(expect.arrayContaining(['itinerary', 'report']));
    expect(g.formats).not.toEqual(expect.arrayContaining(['shorts']));
  });

  it('still offers comedy defaults for an explicit comedy title', () => {
    const g = guessFromTitle('Multilingual funny beauty shorts');
    expect(g.goal).toMatch(/funny short-form/i);
    expect(g.formats).toEqual(expect.arrayContaining(['shorts']));
  });
});

describe('draftFromAnswers', () => {
  it('writes travel instructions and prompts for 首爾之旅', () => {
    const draft = draftFromAnswers('首爾之旅', {
      goal: 'Plan a 6-day Seoul trip for a couple',
      languages: ['zh-tw', 'en'],
      formats: ['itinerary', 'report'],
      materials: ['places', 'budget', 'culture'],
      constraints: 'No car; prefer metro',
    });
    expect(draft.domain).toBe('travel');
    expect(draft.instructions).toMatch(/itinerar|logistics|trip/i);
    expect(draft.instructions).not.toMatch(/funniest possible videos/i);
    expect(draft.researchPrompts.join('\n')).toMatch(/Seoul|首爾|itinerary/i);
    expect(draft.researchPrompts.join('\n')).not.toMatch(/funny short-form|joke bank/i);
  });
});
