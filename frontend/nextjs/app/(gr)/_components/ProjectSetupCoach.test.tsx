import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';
import { AuthError } from '@/lib/research/authErrors';
import ProjectSetupCoach from './ProjectSetupCoach';

describe('ProjectSetupCoach', () => {
  it('shows session-expired when apply fails with 401', async () => {
    const onApply = vi.fn().mockRejectedValue(new AuthError(401));
    const onClose = vi.fn();
    const user = userEvent.setup();

    render(
      <ProjectSetupCoach
        title="Funny beauty shorts EN 粤语"
        open
        onClose={onClose}
        onApply={onApply}
      />,
    );

    // Goal → languages → formats → materials → constraints → review
    await user.type(screen.getByPlaceholderText(/multilingual joke/i), 'Build a joke bank');
    await user.click(screen.getByRole('button', { name: /^continue$/i }));
    // languages may already be guessed from title; ensure at least one then continue
    const continueBtn = screen.getByRole('button', { name: /^continue$/i });
    if ((continueBtn as HTMLButtonElement).disabled) {
      await user.click(screen.getByRole('button', { name: /english/i }));
    }
    await user.click(screen.getByRole('button', { name: /^continue$/i }));
    await user.click(screen.getByRole('button', { name: /^continue$/i }));
    await user.click(screen.getByRole('button', { name: /^continue$/i }));
    await user.click(screen.getByRole('button', { name: /^continue$/i }));

    await user.click(screen.getByRole('button', { name: /apply to project fields/i }));
    await waitFor(() => {
      expect(screen.getByRole('alert')).toHaveTextContent(/session has expired/i);
    });
    expect(onClose).not.toHaveBeenCalled();
  });

  it('closes after a successful apply', async () => {
    const onApply = vi.fn().mockResolvedValue(undefined);
    const onClose = vi.fn();
    const user = userEvent.setup();

    render(<ProjectSetupCoach title="Research pack" open onClose={onClose} onApply={onApply} />);

    await user.type(screen.getByRole('textbox'), 'Ship weekly shorts');
    // Walk remaining steps quickly by selecting defaults where required
    for (let i = 0; i < 5; i += 1) {
      const cont = screen.queryByRole('button', { name: /^continue$/i });
      if (!cont) break;
      if ((cont as HTMLButtonElement).disabled) {
        // pick first chip in the fieldset if present
        const chips = screen.queryAllByRole('button').filter((b) => b.className.includes('border'));
        if (chips[0]) await user.click(chips[0]);
      }
      if (!(cont as HTMLButtonElement).disabled) await user.click(cont);
    }
    const apply = await screen.findByRole('button', { name: /apply to project fields/i });
    await user.click(apply);
    await waitFor(() => expect(onApply).toHaveBeenCalled());
    expect(onClose).toHaveBeenCalled();
  });
});
