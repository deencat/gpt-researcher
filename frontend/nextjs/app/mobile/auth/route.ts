import { headers } from 'next/headers';
import { NextRequest, NextResponse } from 'next/server';

/**
 * Auth bridge for the Hexsenses mobile app.
 * After oauth2-proxy Google sign-in, redirect back into the app with the email. :-)
 */
export async function GET(req: NextRequest) {
  const h = await headers();
  const email =
    h.get('x-auth-request-email') ||
    h.get('x-forwarded-email') ||
    h.get('X-Auth-Request-Email') ||
    h.get('X-Forwarded-Email');

  const redirectParam = req.nextUrl.searchParams.get('redirect_uri');
  const fallback = 'hexsenses://auth';
  let target: URL;
  try {
    target = new URL(redirectParam || fallback);
  } catch {
    target = new URL(fallback);
  }

  // Only allow the Hexsenses app scheme (or http(s) for local Expo web). :-)
  const allowed =
    target.protocol === 'hexsenses:' ||
    target.protocol === 'exp:' ||
    target.hostname === 'localhost' ||
    target.hostname === '127.0.0.1';
  if (!allowed) {
    return NextResponse.json({ error: 'Invalid redirect_uri' }, { status: 400 });
  }

  if (!email) {
    // Not authenticated yet: send the browser through the site root so oauth2-proxy
    // can challenge, then return here. :-)
    const returnTo = new URL('/mobile/auth', req.nextUrl.origin);
    if (redirectParam) returnTo.searchParams.set('redirect_uri', redirectParam);
    return NextResponse.redirect(new URL(`/?rd=${encodeURIComponent(returnTo.toString())}`, req.nextUrl.origin));
  }

  target.searchParams.set('email', email.trim().toLowerCase());
  return NextResponse.redirect(target.toString());
}
