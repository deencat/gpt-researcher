/** Client helpers for Perplexity-style research Projects. :-) */

import { AuthError, throwForResponse } from './authErrors';

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

export { AuthError, isAuthError, authErrorMessage, redirectToLogin, LOGIN_PATH } from './authErrors';

const json = async <T>(res: Response): Promise<T> => {
  if (!res.ok) throwForResponse(res);
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
  if (res.status === 404) return;
  if (!res.ok) throwForResponse(res, 'Could not delete this project.');
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
  if (res.status === 404) return;
  if (!res.ok) throwForResponse(res, 'Could not remove this document.');
};

export const getMe = async () => {
  try {
    return (await json<{ email?: string }>(await fetch('/api/me', { cache: 'no-store' }))).email ?? '';
  } catch (error) {
    if (error instanceof AuthError) throw error;
    return '';
  }
};
