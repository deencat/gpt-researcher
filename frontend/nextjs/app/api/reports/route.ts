import { NextResponse } from 'next/server';
import { backendBase, forwardHeaders } from '@/lib/backendProxy';

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const queryString = searchParams.toString();
    const endpoint = queryString ? `/api/reports?${queryString}` : '/api/reports';
    const response = await fetch(`${backendBase()}${endpoint}`, {
      headers: forwardHeaders(request),
      cache: 'no-store',
    });
    const data = await response.json().catch(() => ({ reports: [] }));
    if (!data.reports) data.reports = [];
    return NextResponse.json(data, { status: response.status });
  } catch {
    return NextResponse.json({ error: 'Failed to connect to backend service' }, { status: 500 });
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.text();
    const headers = new Headers(forwardHeaders(request));
    headers.set('Content-Type', 'application/json');
    const response = await fetch(`${backendBase()}/api/reports`, { method: 'POST', headers, body });
    const data = await response.json().catch(() => ({}));
    return NextResponse.json(data, { status: response.status });
  } catch {
    return NextResponse.json({ error: 'Failed to connect to backend service' }, { status: 500 });
  }
}
