import { NextResponse } from 'next/server';
import { backendBase, forwardHeaders } from '@/lib/backendProxy';

export async function POST(request: Request) {
  try {
    const form = await request.formData();
    const headers = new Headers(forwardHeaders(request));
    // Let fetch set multipart boundary. :-)
    headers.delete('content-type');
    const response = await fetch(`${backendBase()}/api/documents/extract`, {
      method: 'POST',
      headers,
      body: form,
    });
    const data = await response.json().catch(() => ({}));
    return NextResponse.json(data, { status: response.status });
  } catch {
    return NextResponse.json({ error: 'Failed to connect to backend service' }, { status: 500 });
  }
}
