import { NextResponse } from 'next/server';
import { backendBase, forwardHeaders } from '@/lib/backendProxy';

export async function GET(request: Request) {
  const res = await fetch(`${backendBase()}/api/me`, { headers: forwardHeaders(request), cache: 'no-store' });
  const data = await res.json().catch(() => ({}));
  return NextResponse.json(data, { status: res.status });
}
