/** Build follow-up questions grounded in this run's query and report. :-) */

const SKIP_HEADING =
  /^(executive\s+summary|introduction|conclusion|sources?|references|table\s+of\s+contents|overview|abstract)\b/i;

function unique(items: string[]): string[] {
  const seen = new Set<string>();
  const out: string[] = [];
  for (const item of items) {
    const key = item.trim().toLowerCase();
    if (!key || seen.has(key)) continue;
    seen.add(key);
    out.push(item.trim());
  }
  return out;
}

function reportTitle(report: string): string {
  return report.match(/^#\s+(.+)$/m)?.[1]?.replace(/[*_`]/g, '').trim() ?? '';
}

function sectionHeadings(report: string, limit = 6): string[] {
  return [...report.matchAll(/^#{2,3}\s+(.+)$/gm)]
    .map((m) => m[1].replace(/[*_`#]/g, '').trim())
    .filter((h) => h.length >= 4 && h.length <= 90 && !SKIP_HEADING.test(h));
}

/** Short label for templates — prefer a crisp title over a long pasted query. */
export function topicLabel(query: string, report: string, max = 72): string {
  const title = reportTitle(report);
  const raw = (title || query).replace(/\s+/g, ' ').trim();
  if (!raw) return 'this report';
  if (raw.length <= max) return raw;
  const clause = query.split(/[.?!\n]/)[0]?.replace(/\s+/g, ' ').trim() || raw;
  if (clause.length <= max) return clause;
  return `${clause.slice(0, max - 1).trimEnd()}…`;
}

/**
 * Suggest follow-ups for the chat panel.
 * Never returns the old Nvidia demo chips; always ties prompts to this run.
 */
export function suggestFollowUps(query: string, report: string, limit = 4): string[] {
  const q = query.replace(/\s+/g, ' ').trim();
  const body = report.slice(0, 8000);
  const topic = topicLabel(q, report);
  const headings = sectionHeadings(report);
  const moneyOrChain = /\b(xrp|txid|transaction|transfer|wallet|withdraw|deposit|fee|ledger|exchange|tangem|bitunix|crypto|btc|eth)\b/i.test(
    `${q}\n${body}`,
  );
  const stockish = /\b(stock|shares?|revenue|earnings|rally|valuation|market\s+cap)\b/i.test(`${q}\n${body}`);

  const core: string[] = moneyOrChain
    ? [
        'Which fees, reserves, or exchange deductions best explain the shortfall in this report?',
        'How can I independently verify the received amount on a public explorer?',
        'What exact details should I send to support next?',
        'Are there alternative explanations the sources leave open?',
      ]
    : stockish
      ? [
          `What could weaken the case made in this report about ${topic}?`,
          'Which figures or sources are doing the most work in the conclusion?',
          'What would change this conclusion?',
          'What should I watch next based on these sources?',
        ]
      : [
          `What are the strongest findings about ${topic}?`,
          'Which sources matter most, and what do they actually show?',
          'What would change this conclusion?',
          'What should I verify or research next?',
        ];

  // Interleave the first section heading so suggestions stay report-specific. :-)
  const candidates: string[] = [];
  if (core[0]) candidates.push(core[0]);
  if (headings[0]) candidates.push(`Go deeper on “${headings[0]}” using the cited sources.`);
  candidates.push(...core.slice(1));
  for (const heading of headings.slice(1)) {
    candidates.push(`Go deeper on “${heading}” using the cited sources.`);
  }
  if (q.length > 20 && q.length < 160) {
    candidates.push(`Answer my original question more directly: ${q}`);
  }

  return unique(candidates).slice(0, limit);
}
