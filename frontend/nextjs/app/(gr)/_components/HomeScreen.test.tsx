import { render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthError } from '@/lib/research/authErrors';

const getProject = vi.fn();
const setBrief = vi.fn();
let briefValue: Record<string, unknown> = {
  report_type: 'research_report',
  report_source: 'web',
  tone: 'Objective',
  domains: [],
  mcp_enabled: false,
  mcp_strategy: 'fast',
  mcp_configs: '',
};

vi.mock('next/navigation', () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn(), back: vi.fn(), prefetch: vi.fn() }),
  usePathname: () => '/',
}));

vi.mock('@/lib/research/projects', async () => {
  const actual = await vi.importActual<typeof import('@/lib/research/projects')>('@/lib/research/projects');
  return {
    ...actual,
    getProject: (...args: unknown[]) => getProject(...args),
  };
});

vi.mock('@/lib/research/live', () => ({
  startResearch: vi.fn(() => 'run_1'),
}));

vi.mock('@/lib/research/mcp', () => ({
  checkMcp: () => ({ state: 'ok' }),
}));

vi.mock('./backend', () => ({
  useBackend: () => ({
    status: 'online',
    host: 'localhost:8000',
    documents: [],
    upload: vi.fn(),
  }),
}));

vi.mock('./Brief', () => ({
  default: () => <div data-testid="brief" />,
}));

vi.mock('./Favicon', () => ({
  FaviconStack: () => null,
}));

vi.mock('./preferences', () => ({
  useBrief: () => [briefValue, setBrief],
  openSettings: vi.fn(),
}));

vi.mock('./ui', () => ({
  Arrow: () => null,
  Connection: () => null,
}));

vi.mock('./useReports', () => ({
  useReports: () => ({ rows: [] }),
}));

import HomeScreen from './HomeScreen';

describe('HomeScreen project bootstrap', () => {
  beforeEach(() => {
    getProject.mockReset();
    setBrief.mockReset();
    briefValue = {
      report_type: 'research_report',
      report_source: 'web',
      tone: 'Objective',
      domains: [],
      mcp_enabled: false,
      mcp_strategy: 'fast',
      mcp_configs: '',
    };
    window.history.replaceState({}, '', '/?project=proj_1');
  });

  it('uses a functional setBrief update so the brief is not stale', async () => {
    getProject.mockResolvedValue({
      id: 'proj_1',
      name: 'Salon comedy',
      description: '',
      instructions: '',
      documents: [],
      document_count: 0,
      created_at: 1,
      updated_at: 1,
    });
    render(<HomeScreen />);
    await waitFor(() => expect(setBrief).toHaveBeenCalled());
    const updater = setBrief.mock.calls[0][0];
    expect(typeof updater).toBe('function');
    const next = updater({ ...briefValue, tone: 'Humorous' });
    expect(next.project_id).toBe('proj_1');
    expect(next.report_source).toBe('web');
    expect(next.tone).toBe('Humorous');
  });

  it('links to the project via the dynamic /projects/:id route', async () => {
    getProject.mockResolvedValue({
      id: 'proj_1',
      name: 'Salon comedy',
      description: 'x',
      instructions: 'y',
      documents: ['a.md'],
      document_count: 1,
      created_at: 1,
      updated_at: 1,
    });
    // Simulate brief already carrying project_id after bootstrap
    setBrief.mockImplementation((fn: (prev: Record<string, unknown>) => Record<string, unknown>) => {
      briefValue = typeof fn === 'function' ? fn(briefValue) : fn;
    });
    const { rerender } = render(<HomeScreen />);
    await waitFor(() => expect(setBrief).toHaveBeenCalled());
    briefValue = {
      ...briefValue,
      project_id: 'proj_1',
      report_source: 'hybrid',
    };
    rerender(<HomeScreen />);
    const link = await screen.findByRole('link', { name: /salon comedy/i });
    expect(link).toHaveAttribute('href', '/projects/proj_1');
    expect(screen.getByText(/uploaded project documents are included/i)).toBeInTheDocument();
  });

  it('shows session-expired when project bootstrap gets 401', async () => {
    getProject.mockRejectedValue(new AuthError(401));
    render(<HomeScreen />);
    expect(await screen.findByRole('alert')).toHaveTextContent(/session has expired/i);
  });
});
