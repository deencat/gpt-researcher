import { NextResponse } from 'next/server';
import { backendBase, forwardHeaders } from '@/lib/backendProxy';

type Ctx = { params: { id: string } };

export async function GET(request: Request, { params }: Ctx) {
  try {
    const response = await fetch(`${backendBase()}/api/reports/${encodeURIComponent(params.id)}/chat`, {
      headers: forwardHeaders(request),
      cache: 'no-store',
    });
    const data = await response.json().catch(() => ({}));
    return NextResponse.json(data, { status: response.status });
  } catch {
    return NextResponse.json({ error: 'Failed to connect to backend service' }, { status: 500 });
  }
}

export async function POST(request: Request, { params }: Ctx) {
  try {
    const body = await request.text();
    const headers = new Headers(forwardHeaders(request));
    headers.set('Content-Type', 'application/json');
    const response = await fetch(`${backendBase()}/api/reports/${encodeURIComponent(params.id)}/chat`, {
      method: 'POST',
      headers,
      body,
    });
    const data = await response.json().catch(() => ({}));
    return NextResponse.json(data, { status: response.status });
  } catch {
    return NextResponse.json({ error: 'Failed to connect to backend service' }, { status: 500 });
  }
}
