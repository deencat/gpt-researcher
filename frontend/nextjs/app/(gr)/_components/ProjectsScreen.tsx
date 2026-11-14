'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import {
  authErrorMessage,
  createProject,
  isAuthError,
  listProjects,
  type Project,
} from '@/lib/research/projects';
import { useLinks } from './mode';
import SessionExpired from './SessionExpired';
import { Eye } from './ui';

export default function ProjectsScreen() {
  const links = useLinks();
  const router = useRouter();
  const [projects, setProjects] = useState<Project[]>([]);
  const [status, setStatus] = useState<'loading' | 'ready' | 'error' | 'auth'>('loading');
  const [name, setName] = useState('');
  const [creating, setCreating] = useState(false);
  const [problem, setProblem] = useState('');
  const [authMessage, setAuthMessage] = useState('');

  const refresh = async () => {
    setStatus('loading');
    setAuthMessage('');
    try {
      setProjects(await listProjects());
      setStatus('ready');
    } catch (e) {
      if (isAuthError(e)) {
        setAuthMessage(authErrorMessage(e));
        setStatus('auth');
        return;
      }
      setStatus('error');
    }
  };

  useEffect(() => {
    void refresh();
  }, []);

  const create = async () => {
    if (!name.trim() || creating) return;
    setCreating(true);
    setProblem('');
    try {
      const project = await createProject({ name: name.trim() });
      router.push(links.project(project.id));
    } catch (e) {
      if (isAuthError(e)) {
        setAuthMessage(authErrorMessage(e));
        setStatus('auth');
      } else {
        setProblem(authErrorMessage(e));
      }
    } finally {
      setCreating(false);
    }
  };

  return (
    <main className="mx-auto w-full max-w-[920px] px-5 pb-20 pt-10 md:px-8">
      <Eye>Projects</Eye>
      <h1 className="mt-3 font-display text-[34px] font-medium tracking-[-0.02em] sm:text-[40px]">Your research folders</h1>
      <p className="mt-3 max-w-[42em] text-[15.5px] leading-relaxed text-ink-2">
        Like Perplexity Projects: keep documents, system instructions, and research runs together in one place. Only you can see your projects.
      </p>

      {status === 'auth' && <SessionExpired message={authMessage} className="mt-6" />}

      <section className="mt-10 border border-rule-soft bg-paper px-5 py-5 sm:px-6">
        <h2 className="text-[15px] font-semibold">New project</h2>
        <div className="mt-3 flex flex-col gap-3 sm:flex-row">
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && void create()}
            placeholder="e.g. Nvidia earnings, EU AI Act"
            className="h-11 flex-1 border border-rule bg-transparent px-3 text-[14.5px] outline-none focus:border-ink"
          />
          <button type="button" disabled={!name.trim() || creating || status === 'auth'} onClick={() => void create()} className="gr-btn h-11 px-5 disabled:opacity-40">
            Create
          </button>
        </div>
        {problem && <p className="mt-3 text-[13.5px] text-rubric">{problem}</p>}
      </section>

      <section className="mt-10">
        {status === 'loading' && <p className="text-[14px] text-ink-3">Loading projects…</p>}
        {status === 'error' && (
          <p className="text-[14px] text-rubric">
            Could not load projects.{' '}
            <button type="button" className="underline" onClick={() => void refresh()}>
              Retry
            </button>
          </p>
        )}
        {status === 'ready' && projects.length === 0 && (
          <p className="text-[14.5px] text-ink-3">No projects yet. Create one to add documents and instructions.</p>
        )}
        <ul className="divide-y divide-rule-soft border-t border-rule-soft">
          {projects.map((project) => (
            <li key={project.id}>
              <Link href={links.project(project.id)} className="flex items-start justify-between gap-4 py-5 transition-colors hover:bg-ink/[0.02]">
                <div>
                  <h3 className="text-[16px] font-semibold tracking-[-0.01em]">{project.name}</h3>
                  {project.description ? (
                    <p className="mt-1 text-[13.5px] text-ink-3">{project.description}</p>
                  ) : project.instructions ? (
                    <p className="mt-1 line-clamp-2 text-[13.5px] text-ink-3">{project.instructions}</p>
                  ) : null}
                  <p className="mt-2 font-code text-[11px] tracking-[0.04em] text-ink-3">
                    {project.document_count} document{project.document_count === 1 ? '' : 's'}
                  </p>
                </div>
                <span className="mt-1 text-[13px] text-ink-2">Open →</span>
              </Link>
            </li>
          ))}
        </ul>
      </section>
    </main>
  );
}
