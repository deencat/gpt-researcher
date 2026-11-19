'use client';

import { useCallback, useEffect, useState } from 'react';

type ComputerStatus = {
  ok?: boolean;
  enabled?: boolean;
  ready?: boolean;
  running?: boolean;
  mode?: string;
  embedUrl?: string | null;
  hint?: string;
  error?: string;
  dockerReady?: boolean;
  dockerMessage?: string;
};

/** Live view of the Batch3-style isolated desktop (noVNC). */
export function ComputerDesktop() {
  const [status, setStatus] = useState<ComputerStatus | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  const refresh = useCallback(async () => {
    try {
      const res = await fetch('/api/computer-use/status', { cache: 'no-store' });
      const data = (await res.json()) as ComputerStatus;
      setStatus(data);
      setError(data.error || '');
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }, []);

  useEffect(() => {
    void refresh();
    const id = window.setInterval(() => void refresh(), 8000);
    return () => window.clearInterval(id);
  }, [refresh]);

  const start = async () => {
    setBusy(true);
    setError('');
    try {
      const res = await fetch('/api/computer-use/start', { method: 'POST' });
      const data = (await res.json()) as ComputerStatus;
      if (!res.ok || data.ok === false) {
        setError(data.error || `Start failed (${res.status})`);
      }
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  };

  if (status && status.enabled === false) {
    return (
      <div className="p-4 text-[13.5px] text-ink-2">
        Computer use is off. Set <code className="font-code text-[12px]">COMPUTER_USE_ENABLED=true</code> on the
        backend.
      </div>
    );
  }

  const embed = status?.embedUrl;
  const running = Boolean(status?.running || status?.ready);

  return (
    <div className="flex h-full min-h-[280px] flex-col">
      <div className="flex flex-wrap items-center gap-3 border-b border-rule-soft px-3 py-2">
        <p className="font-code text-[11px] uppercase tracking-[0.12em] text-ink-3">
          {status?.mode || 'computer'} · {running ? 'live' : 'stopped'}
        </p>
        <button
          type="button"
          onClick={() => void start()}
          disabled={busy}
          className="gr-btn h-7 px-2.5 text-[12px] disabled:opacity-40"
        >
          {busy ? 'Starting…' : running ? 'Restart desktop' : 'Start desktop'}
        </button>
        <button type="button" onClick={() => void refresh()} className="text-[12px] text-ink-2 underline underline-offset-4">
          Refresh
        </button>
        {embed ? (
          <a href={embed} target="_blank" rel="noreferrer" className="text-[12px] text-ink-2 underline underline-offset-4">
            Open fullscreen
          </a>
        ) : null}
      </div>
      {error ? <p className="px-3 py-2 text-[13px] text-rubric">{error}</p> : null}
      {embed ? (
        <iframe
          title="Isolated computer desktop"
          src={embed}
          className="min-h-[320px] w-full flex-1 border-0 bg-black"
          allow="clipboard-read; clipboard-write"
        />
      ) : (
        <div className="flex flex-1 flex-col items-start justify-center gap-2 p-4 text-[13.5px] text-ink-2">
          <p>No live desktop yet. Start it, then ask chat to navigate a page — you will see the screen here.</p>
          {status?.hint ? <p className="text-[12px] text-ink-3">{status.hint}</p> : null}
        </div>
      )}
    </div>
  );
}
