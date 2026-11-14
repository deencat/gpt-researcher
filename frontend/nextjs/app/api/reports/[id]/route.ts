import { NextResponse } from 'next/server';
import { backendBase, forwardHeaders } from '@/lib/backendProxy';

type Ctx = { params: { id: string } };

export async function GET(request: Request, { params }: Ctx) {
  const response = await fetch(`${backendBase()}/api/reports/${encodeURIComponent(params.id)}`, {
    headers: forwardHeaders(request),
    cache: 'no-store',
  });
  const data = await response.json().catch(() => ({}));
  return NextResponse.json(data, { status: response.status });
}

export async function PUT(request: Request, { params }: Ctx) {
  const body = await request.text();
  const headers = new Headers(forwardHeaders(request));
  headers.set('Content-Type', 'application/json');
  const response = await fetch(`${backendBase()}/api/reports/${encodeURIComponent(params.id)}`, {
    method: 'PUT',
    headers,
    body,
  });
  const data = await response.json().catch(() => ({}));
  return NextResponse.json(data, { status: response.status });
}

export async function DELETE(request: Request, { params }: Ctx) {
  const response = await fetch(`${backendBase()}/api/reports/${encodeURIComponent(params.id)}`, {
    method: 'DELETE',
    headers: forwardHeaders(request),
  });
  const data = await response.json().catch(() => ({}));
  return NextResponse.json(data, { status: response.status });
}
