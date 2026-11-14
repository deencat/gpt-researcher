/** Shared Next → FastAPI proxy helpers. :-) */

export function backendBase() {
  return (
    process.env.GPTR_BACKEND_URL ||
    process.env.NEXT_PUBLIC_BACKEND_URL ||
    process.env.NEXT_PUBLIC_GPTR_API_URL ||
    'http://localhost:8000'
  ).replace(/\/+$/, '');
}

export function forwardHeaders(request: Request): HeadersInit {
  const headers = new Headers();
  const email = request.headers.get('x-auth-request-email');
  const user = request.headers.get('x-auth-request-user');
  if (email) headers.set('X-Auth-Request-Email', email);
  if (user) headers.set('X-Auth-Request-User', user);
  const contentType = request.headers.get('content-type');
  if (contentType) headers.set('Content-Type', contentType);
  return headers;
}
