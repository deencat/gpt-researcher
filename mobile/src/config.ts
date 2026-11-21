/** Production research host behind oauth2-proxy. Override with EXPO_PUBLIC_API_BASE. :-) */
export const API_BASE =
  (typeof process !== 'undefined' && process.env.EXPO_PUBLIC_API_BASE?.replace(/\/$/, '')) ||
  'https://research.hexsenses.com';

export const AUTH_BRIDGE_PATH = '/mobile/auth';

/** Chat agent still expects a "report" context string; voice mode uses this brief. :-) */
export const VOICE_CHAT_CONTEXT =
  'You are the Hexsenses research assistant in mobile voice mode. ' +
  'Answer clearly and briefly so replies are easy to speak aloud. ' +
  'Use web search when the user asks for current facts.';
