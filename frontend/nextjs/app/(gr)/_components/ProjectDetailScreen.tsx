'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useEffect, useRef, useState } from 'react';
import {
  deleteProject,
  deleteProjectDocument,
  getProject,
  updateProject,
  uploadProjectDocument,
  type Project,
} from '@/lib/research/projects';
import { listReports, summarize, type ReportRow } from '@/lib/research/reports';
import { DEFAULT_BRIEF, type BriefValue } from '@/lib/research/brief';
import { useBrief } from './preferences';
import { useLinks } from './mode';
import { Eye } from './ui';

export default function ProjectDetailScreen({ projectId }: { projectId: string }) {
  const links = useLinks();
  const router = useRouter();
  const [, setBrief] = useBrief();
  const picker = useRef<HTMLInputElement>(null);
  const [project, setProject] = useState<Project | null>(null);
  const [instructions, setInstructions] = useState('');
  const [description, setDescription] = useState('');
  const [name, setName] = useState('');
  const [rows, setRows] = useState<ReportRow[]>([]);
  const [status, setStatus] = useState<'loading' | 'ready' | 'missing' | 'error'>('loading');
  const [saving, setSaving] = useState(false);
  const [note, setNote] = useState('');

  const refresh = async () => {
    setStatus('loading');
    try {
      const next = await getProject(projectId);
      if (!next) {
        setStatus('missing');
        return;
      }
      setProject(next);
      setName(next.name);
      setDescription(next.description || '');
      setInstructions(next.instructions || '');
      const reports = await listReports();
      setRows(reports.filter((r) => r.project_id === projectId).map(summarize));
      setStatus('ready');
    } catch {
      setStatus('error');
    }
  };

  useEffect(() => {
    void refresh();
  }, [projectId]);

  const save = async () => {
    if (!project || saving) return;
    setSaving(true);
    setNote('');
    try {
      const next = await updateProject(project.id, { name, description, instructions });
      setProject(next);
      setNote('Saved.');
    } catch (e) {
      setNote(e instanceof Error ? e.message : String(e));
    } finally {
      setSaving(false);
    }
  };

  const upload = async (files: FileList | null) => {
    if (!files?.length || !project) return;
    setNote('');
    try {
      for (const file of Array.from(files)) {
        await uploadProjectDocument(project.id, file);
      }
      await refresh();
      setNote('Documents uploaded.');
    } catch (e) {
      setNote(e instanceof Error ? e.message : String(e));
    }
  };

  const removeDoc = async (filename: string) => {
    if (!project) return;
    await deleteProjectDocument(project.id, filename);
    await refresh();
  };

  const researchHere = () => {
    const brief: BriefValue = {
      ...DEFAULT_BRIEF,
      project_id: projectId,
      report_source: (project?.documents.length ?? 0) > 0 ? 'hybrid' : 'web',
    };
    setBrief(brief);
    router.push(`${links.home}?project=${encodeURIComponent(projectId)}`);
  };

  const remove = async () => {
    if (!project || !window.confirm(`Delete project “${project.name}”? Documents stay removed.`)) return;
    await deleteProject(project.id);
    router.push(links.projects);
  };

  if (status === 'loading') {
    return <main className="mx-auto max-w-[920px] px-5 py-16 text-[14px] text-ink-3">Loading project…</main>;
  }
  if (status === 'missing') {
    return (
      <main className="mx-auto max-w-[920px] px-5 py-16">
        <p className="text-rubric">Project not found.</p>
        <Link href={links.projects} className="mt-4 inline-block underline">
          Back to projects
        </Link>
      </main>
    );
  }
  if (status === 'error' || !project) {
    return (
      <main className="mx-auto max-w-[920px] px-5 py-16">
        <p className="text-rubric">Could not load this project.</p>
        <button type="button" className="mt-4 underline" onClick={() => void refresh()}>
          Retry
        </button>
      </main>
    );
  }

  return (
    <main className="mx-auto w-full max-w-[920px] px-5 pb-24 pt-10 md:px-8">
      <Link href={links.projects} className="text-[13.5px] text-ink-2 hover:text-ink">
        ← Projects
      </Link>
      <Eye className="mt-6">Project</Eye>
      <div className="mt-3 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="w-full border-0 bg-transparent font-display text-[34px] font-medium tracking-[-0.02em] outline-none sm:text-[40px]"
        />
        <div className="flex flex-wrap gap-2">
          <button type="button" className="gr-btn h-10 px-4" onClick={researchHere}>
            Research in project
          </button>
          <button type="button" className="gr-btn-line h-10 px-4" disabled={saving} onClick={() => void save()}>
            Save
          </button>
        </div>
      </div>

      <label className="mt-8 block text-[13px] font-medium text-ink-2">
        Description
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={2}
          className="mt-2 w-full border border-rule-soft bg-transparent px-3 py-2 text-[14.5px] outline-none focus:border-ink"
          placeholder="What this project is for"
        />
      </label>

      <label className="mt-6 block text-[13px] font-medium text-ink-2">
        System instructions
        <span className="mt-1 block font-normal text-ink-3">Applied to every research run in this project (like Perplexity Project instructions).</span>
        <textarea
          value={instructions}
          onChange={(e) => setInstructions(e.target.value)}
          rows={6}
          maxLength={8000}
          className="mt-2 w-full border border-rule-soft bg-transparent px-3 py-2 font-code text-[13px] outline-none focus:border-ink"
          placeholder={'e.g. Always cite sources. Prefer SEC filings. Write for an investor audience.'}
        />
      </label>

      <section className="mt-10">
        <div className="flex items-center justify-between gap-4">
          <h2 className="text-[15px] font-semibold">Documents</h2>
          <button type="button" className="gr-btn-line h-9 px-3 text-[13px]" onClick={() => picker.current?.click()}>
            + Add files
          </button>
          <input ref={picker} type="file" multiple className="hidden" onChange={(e) => void upload(e.target.files)} />
        </div>
        {project.documents.length === 0 ? (
          <p className="mt-4 text-[14px] text-ink-3">No documents yet. Uploads stay private to your account and this project.</p>
        ) : (
          <ul className="mt-4 divide-y divide-rule-soft border-t border-rule-soft">
            {project.documents.map((filename) => (
              <li key={filename} className="flex items-center justify-between gap-4 py-3 text-[14px]">
                <span className="font-code text-[13px]">{filename}</span>
                <button type="button" className="text-ink-3 hover:text-rubric" onClick={() => void removeDoc(filename)}>
                  Remove
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="mt-12">
        <h2 className="text-[15px] font-semibold">Research in this project</h2>
        {rows.length === 0 ? (
          <p className="mt-4 text-[14px] text-ink-3">No runs yet. Start one with “Research in project”.</p>
        ) : (
          <ul className="mt-4 divide-y divide-rule-soft border-t border-rule-soft">
            {rows.map((row) => (
              <li key={row.id}>
                <Link href={links.report(row.id)} className="block py-4 hover:bg-ink/[0.02]">
                  <div className="text-[15px] font-medium">{row.title || row.question}</div>
                  <div className="mt-1 font-code text-[11px] text-ink-3">
                    {row.date} · {row.type}
                  </div>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>

      {note && <p className="mt-8 text-[13.5px] text-ink-2">{note}</p>}

      <button type="button" className="mt-12 text-[13.5px] text-rubric underline" onClick={() => void remove()}>
        Delete project
      </button>
    </main>
  );
}
