import { backendBase, forwardHeaders } from '@/lib/backendProxy';

export async function GET(request: Request) {
  const response = await fetch(`${backendBase()}/api/computer-use/status`, {
    headers: forwardHeaders(request),
    cache: 'no-store',
  });
  const body = await response.text();
  return new Response(body, {
    status: response.status,
    headers: { 'Content-Type': response.headers.get('Content-Type') || 'application/json' },
  });
}
