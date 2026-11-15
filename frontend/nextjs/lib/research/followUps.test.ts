import { describe, expect, it } from 'vitest';
import { suggestFollowUps, topicLabel } from './followUps';

describe('suggestFollowUps', () => {
  it('grounds XRP / transfer reports in fees and verification, not Nvidia chips', () => {
    const query =
      'I transferred 5 XRP from my Bitunix account to Tangem wallet. Why did I receive way less? TXID 4D3DD9B1';
    const report = `# Investigation Report: Why a 5 XRP Withdrawal Appeared as Way Less

## Executive Summary (Finding and Opinion)
Fees and reserves.

## XRPL reserve and destination tags
Details.

## Bitunix withdrawal fees
More details.
`;
    const qs = suggestFollowUps(query, report);
    expect(qs.length).toBeGreaterThan(0);
    expect(qs.join(' ')).not.toMatch(/data centers|stop the rally/i);
    expect(qs.some((q) => /fee|shortfall|verify|explorer|support/i.test(q))).toBe(true);
  });

  it('uses section headings when present', () => {
    const qs = suggestFollowUps('Salon comedy hooks for Hong Kong', `# Comedy shorts brief\n\n## Hook formulas\n...\n\n## Culture notes\n...`);
    expect(qs.some((q) => /Hook formulas|Culture notes/i.test(q))).toBe(true);
    expect(qs.join(' ')).not.toMatch(/data centers/i);
  });

  it('returns a stable short list', () => {
    const qs = suggestFollowUps('Why is Nvidia stock going up?', '# Nvidia\n\n## Revenue\nData.');
    expect(qs.length).toBeLessThanOrEqual(4);
    expect(new Set(qs).size).toBe(qs.length);
  });
});

describe('topicLabel', () => {
  it('prefers the report title over a long query', () => {
    expect(topicLabel('long pasted query '.repeat(20), '# Short title\n\nBody')).toBe('Short title');
  });
});
