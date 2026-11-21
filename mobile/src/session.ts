import * as SecureStore from 'expo-secure-store';

const EMAIL_KEY = 'hexsenses.email';
const UNLOCKED_KEY = 'hexsenses.unlocked';

export type Session = {
  email: string;
};

export async function getSession(): Promise<Session | null> {
  const email = await SecureStore.getItemAsync(EMAIL_KEY);
  if (!email) return null;
  return { email };
}

export async function saveSession(email: string): Promise<void> {
  await SecureStore.setItemAsync(EMAIL_KEY, email.trim().toLowerCase());
  await SecureStore.setItemAsync(UNLOCKED_KEY, '1');
}

export async function clearSession(): Promise<void> {
  await SecureStore.deleteItemAsync(EMAIL_KEY);
  await SecureStore.deleteItemAsync(UNLOCKED_KEY);
}

export async function markLocked(): Promise<void> {
  await SecureStore.deleteItemAsync(UNLOCKED_KEY);
}

export async function isUnlocked(): Promise<boolean> {
  return (await SecureStore.getItemAsync(UNLOCKED_KEY)) === '1';
}

export async function markUnlocked(): Promise<void> {
  await SecureStore.setItemAsync(UNLOCKED_KEY, '1');
}
