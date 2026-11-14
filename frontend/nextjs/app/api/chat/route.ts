import { NextResponse } from 'next/server';
import { backendBase, forwardHeaders } from '@/lib/backendProxy';

export async function POST(request: Request) {
  try {
    const body = await request.text();
    const headers = new Headers(forwardHeaders(request));
    headers.set('Content-Type', 'application/json');
    const response = await fetch(`${backendBase()}/api/chat`, {
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
