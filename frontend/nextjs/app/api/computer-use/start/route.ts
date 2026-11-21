import { backendBase, forwardHeaders } from '@/lib/backendProxy';

export async function POST(request: Request) {
  const response = await fetch(`${backendBase()}/api/computer-use/start`, {
    method: 'POST',
    headers: forwardHeaders(request),
  });
  const body = await response.text();
  return new Response(body, {
    status: response.status,
    headers: { 'Content-Type': response.headers.get('Content-Type') || 'application/json' },
  });
}
