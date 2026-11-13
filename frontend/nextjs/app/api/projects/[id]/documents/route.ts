import { NextResponse } from 'next/server';
import { backendBase, forwardHeaders } from '@/lib/backendProxy';

type Ctx = { params: { id: string } };

export async function GET(request: Request, { params }: Ctx) {
  const res = await fetch(`${backendBase()}/api/projects/${encodeURIComponent(params.id)}/documents`, {
    headers: forwardHeaders(request),
    cache: 'no-store',
  });
  const data = await res.json().catch(() => ({}));
  return NextResponse.json(data, { status: res.status });
}

export async function POST(request: Request, { params }: Ctx) {
  const form = await request.formData();
  const headers = new Headers();
  const email = request.headers.get('x-auth-request-email');
  const user = request.headers.get('x-auth-request-user');
  if (email) headers.set('X-Auth-Request-Email', email);
  if (user) headers.set('X-Auth-Request-User', user);
  const res = await fetch(`${backendBase()}/api/projects/${encodeURIComponent(params.id)}/documents`, {
    method: 'POST',
    headers,
    body: form,
  });
  const data = await res.json().catch(() => ({}));
  return NextResponse.json(data, { status: res.status });
}
