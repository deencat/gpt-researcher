import { NextResponse } from 'next/server';
import { backendBase, forwardHeaders } from '@/lib/backendProxy';

export const dynamic = 'force-dynamic';

export async function POST(request: Request, { params }: { params: { id: string } }) {
  const body = await request.text();
  const res = await fetch(`${backendBase()}/api/projects/${encodeURIComponent(params.id)}/produce-pack`, {
    method: 'POST',
    headers: forwardHeaders(request),
    body,
    cache: 'no-store',
  });
  const text = await res.text();
  return new NextResponse(text, {
    status: res.status,
    headers: { 'Content-Type': res.headers.get('Content-Type') || 'application/json' },
  });
}
