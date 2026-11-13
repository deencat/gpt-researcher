/** Client helpers for Perplexity-style research Projects. :-) */

export interface Project {
  id: string;
  name: string;
  description: string;
  instructions: string;
  owner_email?: string;
  created_at: number;
  updated_at: number;
  documents: string[];
  document_count: number;
}

const json = async <T>(res: Response): Promise<T> => {
  if (!res.ok) throw new Error(`The backend answered with ${res.status}.`);
  return (await res.json()) as T;
};

export const listProjects = async () =>
  (await json<{ projects?: Project[] }>(await fetch('/api/projects', { cache: 'no-store' }))).projects ?? [];

export const getProject = async (id: string) => {
  const res = await fetch(`/api/projects/${encodeURIComponent(id)}`, { cache: 'no-store' });
  if (res.status === 404) return null;
  return (await json<{ project?: Project }>(res)).project ?? null;
};

export const createProject = async (input: { name: string; description?: string; instructions?: string }) =>
  (await json<{ project: Project }>(
    await fetch('/api/projects', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(input),
    }),
  )).project;

export const updateProject = async (
  id: string,
  patch: Partial<Pick<Project, 'name' | 'description' | 'instructions'>>,
) =>
  (await json<{ project: Project }>(
    await fetch(`/api/projects/${encodeURIComponent(id)}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(patch),
    }),
  )).project;

export const deleteProject = async (id: string) => {
  const res = await fetch(`/api/projects/${encodeURIComponent(id)}`, { method: 'DELETE' });
  if (!res.ok && res.status !== 404) throw new Error(`The backend answered with ${res.status}.`);
};

export const uploadProjectDocument = async (projectId: string, file: File) => {
  const body = new FormData();
  body.append('file', file);
  return json<{ filename: string }>(
    await fetch(`/api/projects/${encodeURIComponent(projectId)}/documents`, { method: 'POST', body }),
  );
};

export const deleteProjectDocument = async (projectId: string, filename: string) => {
  const res = await fetch(
    `/api/projects/${encodeURIComponent(projectId)}/documents/${encodeURIComponent(filename)}`,
    { method: 'DELETE' },
  );
  if (!res.ok && res.status !== 404) throw new Error(`The backend answered with ${res.status}.`);
};

export const getMe = async () => {
  try {
    return (await json<{ email?: string }>(await fetch('/api/me', { cache: 'no-store' }))).email ?? '';
  } catch {
    return '';
  }
};
