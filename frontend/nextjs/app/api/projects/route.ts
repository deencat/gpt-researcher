import { NextResponse } from 'next/server';
import { backendBase, forwardHeaders } from '@/lib/backendProxy';

export async function GET(request: Request) {
  const res = await fetch(`${backendBase()}/api/projects`, { headers: forwardHeaders(request), cache: 'no-store' });
  const data = await res.json().catch(() => ({}));
  return NextResponse.json(data, { status: res.status });
}

export async function POST(request: Request) {
  const body = await request.text();
  const headers = new Headers(forwardHeaders(request));
  headers.set('Content-Type', 'application/json');
  const res = await fetch(`${backendBase()}/api/projects`, { method: 'POST', headers, body });
  const data = await res.json().catch(() => ({}));
  return NextResponse.json(data, { status: res.status });
}
