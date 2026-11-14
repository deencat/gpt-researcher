import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthError } from '@/lib/research/authErrors';

const listProjects = vi.fn();
const createProject = vi.fn();
const push = vi.fn();

vi.mock('next/navigation', () => ({
  useRouter: () => ({ push, replace: vi.fn(), back: vi.fn(), prefetch: vi.fn() }),
  usePathname: () => '/',
}));

vi.mock('@/lib/research/projects', async () => {
  const actual = await vi.importActual<typeof import('@/lib/research/projects')>('@/lib/research/projects');
  return {
    ...actual,
    listProjects: (...args: unknown[]) => listProjects(...args),
    createProject: (...args: unknown[]) => createProject(...args),
  };
});

vi.mock('./ui', () => ({
  Eye: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

import ProjectsScreen from './ProjectsScreen';

describe('ProjectsScreen', () => {
  beforeEach(() => {
    listProjects.mockReset();
    createProject.mockReset();
    push.mockReset();
  });

  it('shows session-expired UI when listing projects returns 401', async () => {
    listProjects.mockRejectedValue(new AuthError(401));
    render(<ProjectsScreen />);
    expect(await screen.findByRole('alert')).toHaveTextContent(/session has expired/i);
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });

  it('renders the empty state when the user has no projects', async () => {
    listProjects.mockResolvedValue([]);
    render(<ProjectsScreen />);
    expect(await screen.findByText(/no projects yet/i)).toBeInTheDocument();
  });

  it('surfaces auth errors when create fails with 403', async () => {
    listProjects.mockResolvedValue([]);
    createProject.mockRejectedValue(new AuthError(403));
    const user = userEvent.setup();
    render(<ProjectsScreen />);
    await screen.findByText(/no projects yet/i);
    await user.type(screen.getByPlaceholderText(/nvidia/i), 'Salon shorts');
    await user.click(screen.getByRole('button', { name: /^create$/i }));
    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent(/do not have access|session has expired/i);
    });
  });
});
