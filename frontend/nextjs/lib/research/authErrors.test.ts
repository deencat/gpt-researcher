import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest';
import {
  AuthError,
  authErrorMessage,
  isAuthError,
  LOGIN_PATH,
  redirectToLogin,
  throwForResponse,
} from './authErrors';

describe('authErrors', () => {
  it('detects AuthError instances', () => {
    expect(isAuthError(new AuthError(401))).toBe(true);
    expect(isAuthError(new Error('nope'))).toBe(false);
  });

  it('throwForResponse maps 401/403 to AuthError', () => {
    expect(() => throwForResponse({ status: 401 } as Response)).toThrow(AuthError);
    expect(() => throwForResponse({ status: 403 } as Response)).toThrow(AuthError);
    try {
      throwForResponse({ status: 500 } as Response);
    } catch (e) {
      expect(isAuthError(e)).toBe(false);
      expect((e as Error).message).toContain('500');
    }
  });

  it('authErrorMessage prefers AuthError copy', () => {
    expect(authErrorMessage(new AuthError(401))).toMatch(/session has expired/i);
    expect(authErrorMessage(new Error('boom'))).toBe('boom');
  });

  describe('redirectToLogin', () => {
    const original = window.location;

    beforeEach(() => {
      // jsdom location.assign is not always stubbable without replacing location
      Object.defineProperty(window, 'location', {
        configurable: true,
        value: {
          ...original,
          pathname: '/projects',
          search: '?x=1',
          assign: vi.fn(),
        },
      });
    });

    afterEach(() => {
      Object.defineProperty(window, 'location', { configurable: true, value: original });
    });

    it('sends the browser to oauth2 sign-in with return path', () => {
      redirectToLogin();
      expect(window.location.assign).toHaveBeenCalledWith(
        `${LOGIN_PATH}?rd=${encodeURIComponent('/projects?x=1')}`,
      );
    });
  });
});
