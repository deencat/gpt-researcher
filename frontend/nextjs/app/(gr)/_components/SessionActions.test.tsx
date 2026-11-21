import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const listProjects = vi.fn();
const setReportProject = vi.fn();
const deleteReport = vi.fn();
const refresh = vi.fn();
const drop = vi.fn();
const push = vi.fn();

vi.mock('next/navigation', () => ({
  useRouter: () => ({ push, replace: vi.fn(), back: vi.fn(), prefetch: vi.fn() }),
}));

vi.mock('@/lib/research/projects', () => ({
  listProjects: (...args: unknown[]) => listProjects(...args),
}));

vi.mock('@/lib/research/reports', () => ({
  setReportProject: (...args: unknown[]) => setReportProject(...args),
  deleteReport: (...args: unknown[]) => deleteReport(...args),
  reportsStore: { refresh: () => refresh(), drop: (...args: unknown[]) => drop(...args) },
}));

vi.mock('./mode', () => ({
  useLinks: () => ({ archive: '/archive', projects: '/projects', project: (id: string) => `/projects/${id}`, home: '/', report: (id: string) => `/research/${id}` }),
}));

import SessionActions from './SessionActions';

describe('SessionActions', () => {
  beforeEach(() => {
    listProjects.mockReset();
    setReportProject.mockReset();
    deleteReport.mockReset();
    refresh.mockReset();
    drop.mockReset();
    push.mockReset();
    listProjects.mockResolvedValue([{ id: 'proj_1', name: 'Salon comedy', description: '', instructions: '', documents: [], document_count: 0, created_at: 1, updated_at: 1 }]);
    setReportProject.mockResolvedValue({});
    deleteReport.mockResolvedValue(undefined);
  });

  it('assigns a report to a project', async () => {
    render(<SessionActions reportId="rep_1" />);
    await userEvent.click(screen.getByRole('button', { name: /add to project/i }));
    await screen.findByRole('menuitemradio', { name: /salon comedy/i });
    await userEvent.click(screen.getByRole('menuitemradio', { name: /salon comedy/i }));
    await waitFor(() => expect(setReportProject).toHaveBeenCalledWith('rep_1', 'proj_1'));
  });

  it('removes a report from its project', async () => {
    render(<SessionActions reportId="rep_1" projectId="proj_1" />);
    await userEvent.click(screen.getByRole('button', { name: /in project|in salon/i }));
    await screen.findByRole('menuitem', { name: /remove from project/i });
    await userEvent.click(screen.getByRole('menuitem', { name: /remove from project/i }));
    await waitFor(() => expect(setReportProject).toHaveBeenCalledWith('rep_1', null));
  });
});
