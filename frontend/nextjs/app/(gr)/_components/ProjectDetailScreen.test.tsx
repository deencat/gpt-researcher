import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthError } from '@/lib/research/authErrors';

const getProject = vi.fn();
const deleteProject = vi.fn();
const deleteProjectDocument = vi.fn();
const updateProject = vi.fn();
const uploadProjectDocument = vi.fn();
const listReports = vi.fn();
const push = vi.fn();

vi.mock('next/navigation', () => ({
  useRouter: () => ({ push, replace: vi.fn(), back: vi.fn(), prefetch: vi.fn() }),
  usePathname: () => '/',
}));

vi.mock('@/lib/research/projects', async () => {
  const actual = await vi.importActual<typeof import('@/lib/research/projects')>('@/lib/research/projects');
  return {
    ...actual,
    getProject: (...args: unknown[]) => getProject(...args),
    deleteProject: (...args: unknown[]) => deleteProject(...args),
    deleteProjectDocument: (...args: unknown[]) => deleteProjectDocument(...args),
    updateProject: (...args: unknown[]) => updateProject(...args),
    uploadProjectDocument: (...args: unknown[]) => uploadProjectDocument(...args),
  };
});

vi.mock('@/lib/research/reports', () => ({
  listReports: (...args: unknown[]) => listReports(...args),
  summarize: (r: { id: string; question?: string }) => ({
    id: r.id,
    title: r.question || r.id,
    question: r.question || '',
    date: 'today',
    type: 'Summary',
    project_id: 'proj_1',
  }),
}));

vi.mock('./preferences', () => ({
  useBrief: () => [{}, vi.fn()],
}));

vi.mock('./ProjectSetupCoach', () => ({
  default: () => null,
}));

vi.mock('./ui', () => ({
  Eye: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

import ProjectDetailScreen from './ProjectDetailScreen';

const project = {
  id: 'proj_1',
  name: 'Comedy shorts',
  description: 'Demo',
  instructions: 'Be funny',
  created_at: 1,
  updated_at: 1,
  documents: ['hooks.md'],
  document_count: 1,
};

describe('ProjectDetailScreen', () => {
  beforeEach(() => {
    getProject.mockReset();
    deleteProject.mockReset();
    deleteProjectDocument.mockReset();
    updateProject.mockReset();
    uploadProjectDocument.mockReset();
    listReports.mockReset();
    push.mockReset();
    listReports.mockResolvedValue([]);
    vi.spyOn(window, 'confirm').mockReturnValue(true);
  });

  it('shows session-expired when the project fetch is unauthorized', async () => {
    getProject.mockRejectedValue(new AuthError(401));
    render(<ProjectDetailScreen projectId="proj_1" />);
    expect(await screen.findByRole('alert')).toHaveTextContent(/session has expired/i);
  });

  it('surfaces delete-document failures instead of failing silently', async () => {
    getProject.mockResolvedValue(project);
    deleteProjectDocument.mockRejectedValue(new Error('Could not remove this document.'));
    const user = userEvent.setup();
    render(<ProjectDetailScreen projectId="proj_1" />);
    expect(await screen.findByText('hooks.md')).toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: /^remove$/i }));
    await waitFor(() => {
      expect(screen.getByText(/could not remove this document/i)).toBeInTheDocument();
    });
  });

  it('surfaces delete-project failures and stays on the page', async () => {
    getProject.mockResolvedValue(project);
    deleteProject.mockRejectedValue(new Error('Could not delete this project.'));
    const user = userEvent.setup();
    render(<ProjectDetailScreen projectId="proj_1" />);
    expect(await screen.findByDisplayValue('Comedy shorts')).toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: /delete project/i }));
    await waitFor(() => {
      expect(screen.getByText(/could not delete this project/i)).toBeInTheDocument();
    });
    expect(push).not.toHaveBeenCalled();
  });

  it('shows auth UI when delete project returns 401', async () => {
    getProject.mockResolvedValue(project);
    deleteProject.mockRejectedValue(new AuthError(401));
    const user = userEvent.setup();
    render(<ProjectDetailScreen projectId="proj_1" />);
    await screen.findByDisplayValue('Comedy shorts');
    await user.click(screen.getByRole('button', { name: /delete project/i }));
    expect(await screen.findByRole('alert')).toHaveTextContent(/session has expired/i);
  });
});
