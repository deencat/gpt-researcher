import { NextResponse } from 'next/server';
import { backendBase, forwardHeaders } from '@/lib/backendProxy';

type Ctx = { params: { id: string; filename: string } };

export async function DELETE(request: Request, { params }: Ctx) {
  const res = await fetch(
    `${backendBase()}/api/projects/${encodeURIComponent(params.id)}/documents/${encodeURIComponent(params.filename)}`,
    { method: 'DELETE', headers: forwardHeaders(request) },
  );
  const data = await res.json().catch(() => ({}));
  return NextResponse.json(data, { status: res.status });
}
