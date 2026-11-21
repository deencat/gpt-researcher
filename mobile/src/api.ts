import { API_BASE, VOICE_CHAT_CONTEXT } from './config';

export type ChatTurn = { role: 'user' | 'assistant'; content: string };

export async function askVoiceChat(messages: ChatTurn[]): Promise<string> {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    credentials: 'include',
    body: JSON.stringify({
      report: VOICE_CHAT_CONTEXT,
      messages: messages.map(({ role, content }) => ({ role, content })),
    }),
  });
  const data = (await res.json()) as {
    response?: { content?: string };
    error?: string;
  };
  const content = data.response?.content?.trim();
  if (!res.ok || !content) {
    throw new Error(data.error || `Chat failed (${res.status}). Sign in on the web host if cookies expired.`);
  }
  return content;
}
