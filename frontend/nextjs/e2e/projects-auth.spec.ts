import { expect, test } from '@playwright/test';

/**
 * E2E coverage for the PR #2 project-screen auth UX.
 * APIs are mocked so the suite does not need a live FastAPI backend.
 */

test.describe('Projects auth UX', () => {
  test('projects list shows Sign in on 401', async ({ page }) => {
    await page.route('**/api/projects', async (route) => {
      if (route.request().method() === 'GET') {
        await route.fulfill({
          status: 401,
          contentType: 'application/json',
          body: JSON.stringify({ detail: 'Authentication required' }),
        });
        return;
      }
      await route.fallback();
    });

    await page.goto('/projects');
    await expect(page.getByText(/your session has expired/i)).toBeVisible();
    await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible();
  });

  test('home project bootstrap shows session-expired on 401', async ({ page }) => {
    await page.route('**/api/projects/proj_e2e', async (route) => {
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Authentication required' }),
      });
    });
    // Avoid unrelated backend-offline noise by stubbing the docs listing the home screen pings.
    await page.route('**/api/**', async (route) => {
      const url = route.request().url();
      if (url.includes('/api/projects/proj_e2e')) {
        await route.fulfill({
          status: 401,
          contentType: 'application/json',
          body: JSON.stringify({ detail: 'Authentication required' }),
        });
        return;
      }
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ files: [], reports: [], documents: [] }),
      });
    });

    await page.goto('/?project=proj_e2e');
    await expect(page.getByText(/your session has expired/i)).toBeVisible();
  });

  test('project detail delete surfaces an error when DELETE fails', async ({ page }) => {
    await page.route('**/api/projects/proj_e2e', async (route) => {
      if (route.request().method() === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            project: {
              id: 'proj_e2e',
              name: 'E2E Project',
              description: 'Has setup',
              instructions: 'Be careful',
              documents: [],
              document_count: 0,
              created_at: 1,
              updated_at: 1,
            },
          }),
        });
        return;
      }
      if (route.request().method() === 'DELETE') {
        await route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({ detail: 'boom' }),
        });
        return;
      }
      await route.fallback();
    });
    await page.route('**/api/reports**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ reports: [] }),
      });
    });

    page.on('dialog', (dialog) => dialog.accept());
    await page.goto('/projects/proj_e2e');
    await expect(page.locator('input').filter({ hasText: '' }).first()).toBeVisible();
    await expect(page.locator('input[value="E2E Project"]')).toBeVisible();
    await page.getByRole('button', { name: /delete project/i }).click();
    await expect(page.getByText(/could not delete|answered with 500/i)).toBeVisible();
  });
});
