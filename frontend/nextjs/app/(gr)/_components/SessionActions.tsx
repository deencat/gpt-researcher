'use client';

import { useRouter } from 'next/navigation';
import { useEffect, useId, useState } from 'react';
import { listProjects, type Project } from '@/lib/research/projects';
import { deleteReport, reportsStore, setReportProject } from '@/lib/research/reports';
import { popoverPanel, usePopover } from './popover';
import { useLinks } from './mode';

type Props = {
  reportId: string;
  projectId?: string | null;
  onProjectChange?: (projectId: string | null) => void;
  compact?: boolean;
};

export default function SessionActions({ reportId, projectId = null, onProjectChange, compact }: Props) {
  const router = useRouter();
  const links = useLinks();
  const projectMenu = usePopover<HTMLDivElement>();
  const moreMenu = usePopover<HTMLDivElement>();
  const projectListId = useId();
  const moreId = useId();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loadingProjects, setLoadingProjects] = useState(false);
  const [busy, setBusy] = useState(false);
  const [note, setNote] = useState('');

  useEffect(() => {
    if (!projectMenu.open) return;
    let alive = true;
    setLoadingProjects(true);
    listProjects()
      .then((rows) => {
        if (alive) setProjects(rows);
      })
      .catch(() => {
        if (alive) setNote('Could not load projects.');
      })
      .finally(() => {
        if (alive) setLoadingProjects(false);
      });
    return () => {
      alive = false;
    };
  }, [projectMenu.open]);

  const current = projects.find((p) => p.id === projectId);

  const assign = async (next: string | null) => {
    if (busy) return;
    setBusy(true);
    setNote('');
    try {
      await setReportProject(reportId, next);
      onProjectChange?.(next);
      projectMenu.setOpen(false);
      void reportsStore.refresh();
    } catch (e) {
      setNote(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  };

  const removeSession = async () => {
    if (busy) return;
    const ok = window.confirm('Delete this research session? This cannot be undone.');
    if (!ok) return;
    setBusy(true);
    setNote('');
    try {
      await deleteReport(reportId);
      reportsStore.drop(reportId);
      moreMenu.setOpen(false);
      router.push(links.archive);
    } catch (e) {
      setNote(e instanceof Error ? e.message : String(e));
      setBusy(false);
    }
  };

  const item = 'flex w-full items-center px-4 py-2.5 text-left text-[14px] font-medium transition-colors hover:bg-paper disabled:opacity-50';

  return (
    <div className="flex items-center gap-2">
      <div ref={projectMenu.root} className="relative">
        <button
          type="button"
          aria-haspopup="menu"
          aria-expanded={projectMenu.open}
          aria-controls={projectListId}
          disabled={busy}
          onClick={() => projectMenu.setOpen(!projectMenu.open)}
          className="gr-btn-line gap-2.5"
        >
          {compact ? 'Project' : current ? `In ${current.name}` : projectId ? 'In project' : 'Add to project'}
        </button>
        {projectMenu.open && (
          <div id={projectListId} role="menu" aria-label="Projects" data-popover className={`${popoverPanel} right-0 w-[min(280px,calc(100vw-24px))] py-2`}>
            {loadingProjects && <p className="px-4 py-2 text-[13px] text-ink-3">Loading projects…</p>}
            {!loadingProjects && projects.length === 0 && (
              <p className="px-4 py-2 text-[13px] text-ink-3">
                No projects yet.{' '}
                <a href={links.projects} className="underline">
                  Create one
                </a>
              </p>
            )}
            {projects.map((p) => (
              <button
                key={p.id}
                type="button"
                role="menuitemradio"
                aria-checked={p.id === projectId}
                disabled={busy || p.id === projectId}
                className={item}
                onClick={() => void assign(p.id)}
              >
                {p.name}
                {p.id === projectId ? <span className="ml-auto font-code text-[10px] uppercase tracking-[0.1em] text-ink-3">Current</span> : null}
              </button>
            ))}
            {projectId && (
              <>
                <div className="my-1.5 h-px bg-rule-soft" />
                <button type="button" role="menuitem" disabled={busy} className={`${item} text-rubric`} onClick={() => void assign(null)}>
                  Remove from project
                </button>
              </>
            )}
          </div>
        )}
      </div>

      <div ref={moreMenu.root} className="relative">
        <button
          type="button"
          aria-haspopup="menu"
          aria-expanded={moreMenu.open}
          aria-controls={moreId}
          disabled={busy}
          onClick={() => moreMenu.setOpen(!moreMenu.open)}
          className="gr-btn-line gap-2.5"
          aria-label="Session actions"
        >
          ···
        </button>
        {moreMenu.open && (
          <div id={moreId} role="menu" aria-label="Session actions" data-popover className={`${popoverPanel} right-0 w-[220px] py-2`}>
            <button type="button" role="menuitem" disabled={busy} className={`${item} text-rubric`} onClick={() => void removeSession()}>
              Delete session
            </button>
          </div>
        )}
      </div>

      {note && (
        <span role="alert" className="sr-only">
          {note}
        </span>
      )}
      {note && <span className="hidden max-w-[160px] truncate text-[12px] text-rubric sm:inline">{note}</span>}
    </div>
  );
}
