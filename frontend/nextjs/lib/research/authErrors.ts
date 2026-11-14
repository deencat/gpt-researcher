/** Client-side handling for 401/403 from protected project APIs. :-) */

export const LOGIN_PATH = '/oauth2/sign_in';

export class AuthError extends Error {
  readonly status: 401 | 403;

  constructor(status: 401 | 403, message?: string) {
    super(message || (status === 403 ? 'You do not have access to this resource.' : 'Your session has expired. Sign in again to continue.'));
    this.name = 'AuthError';
    this.status = status;
  }
}

export function isAuthError(error: unknown): error is AuthError {
  return error instanceof AuthError;
}

/** Throw AuthError for 401/403; otherwise a generic Error with the status. */
export function throwForResponse(res: Response, fallbackMessage?: string): never {
  if (res.status === 401 || res.status === 403) {
    throw new AuthError(res.status);
  }
  throw new Error(fallbackMessage || `The backend answered with ${res.status}.`);
}

export function authErrorMessage(error: unknown): string {
  if (isAuthError(error)) return error.message;
  if (error instanceof Error) return error.message;
  return String(error);
}

/** Full-page or inline redirect to the oauth2-proxy sign-in flow. */
export function redirectToLogin(returnTo?: string) {
  if (typeof window === 'undefined') return;
  const rd = returnTo || `${window.location.pathname}${window.location.search}`;
  const url = `${LOGIN_PATH}?rd=${encodeURIComponent(rd)}`;
  window.location.assign(url);
}
