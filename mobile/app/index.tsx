import * as Linking from 'expo-linking';
import { router } from 'expo-router';
import * as WebBrowser from 'expo-web-browser';
import { useCallback, useEffect, useState } from 'react';
import { ActivityIndicator, Pressable, StyleSheet, Text, View } from 'react-native';
import { API_BASE, AUTH_BRIDGE_PATH } from '../src/config';
import { biometricsAvailable, unlockWithBiometrics } from '../src/biometrics';
import { clearSession, getSession, isUnlocked, markLocked, markUnlocked, saveSession } from '../src/session';
import { colors } from '../src/theme';

WebBrowser.maybeCompleteAuthSession();

export default function GateScreen() {
  const [email, setEmail] = useState<string | null>(null);
  const [ready, setReady] = useState(false);
  const [busy, setBusy] = useState(false);
  const [note, setNote] = useState('');
  const [canBio, setCanBio] = useState(false);

  const refresh = useCallback(async () => {
    const session = await getSession();
    setEmail(session?.email ?? null);
    setCanBio(await biometricsAvailable());
    setReady(true);
    if (session && (await isUnlocked())) {
      router.replace('/voice');
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const signIn = async () => {
    setBusy(true);
    setNote('');
    try {
      const redirectUri = Linking.createURL('auth');
      const authUrl = `${API_BASE}${AUTH_BRIDGE_PATH}?redirect_uri=${encodeURIComponent(redirectUri)}`;
      const result = await WebBrowser.openAuthSessionAsync(authUrl, redirectUri);
      if (result.type !== 'success' || !result.url) {
        setNote(result.type === 'cancel' ? 'Sign-in cancelled.' : 'Sign-in did not finish.');
        return;
      }
      const parsed = Linking.parse(result.url);
      const nextEmail =
        (typeof parsed.queryParams?.email === 'string' && parsed.queryParams.email) ||
        (typeof parsed.queryParams?.user === 'string' && parsed.queryParams.user);
      if (!nextEmail) {
        setNote('Signed in, but no email came back from the auth bridge.');
        return;
      }
      await saveSession(nextEmail);
      setEmail(nextEmail);
      router.replace('/voice');
    } catch (e) {
      setNote(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  };

  const unlock = async () => {
    setBusy(true);
    setNote('');
    try {
      if (!(await unlockWithBiometrics())) {
        setNote('Face ID / biometrics cancelled.');
        return;
      }
      await markUnlocked();
      router.replace('/voice');
    } catch (e) {
      setNote(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  };

  const signOut = async () => {
    await clearSession();
    setEmail(null);
    setNote('Signed out on this device.');
  };

  if (!ready) {
    return (
      <View style={styles.center}>
        <ActivityIndicator color={colors.ink} />
      </View>
    );
  }

  return (
    <View style={styles.screen}>
      <Text style={styles.brand}>Hexsenses</Text>
      <Text style={styles.title}>Research voice</Text>
      <Text style={styles.copy}>
        Sign in once with Google on the research site. After that, unlock with Face ID (or fingerprint) and talk to the
        assistant.
      </Text>

      {email ? (
        <>
          <Text style={styles.meta}>Signed in as {email}</Text>
          <Pressable
            style={[styles.btn, (!canBio || busy) && styles.btnDisabled]}
            disabled={!canBio || busy}
            onPress={() => void unlock()}
          >
            <Text style={styles.btnText}>{canBio ? 'Unlock with Face ID' : 'Biometrics unavailable'}</Text>
          </Pressable>
          <Pressable
            style={styles.linkBtn}
            onPress={() => {
              void markUnlocked().then(() => router.replace('/voice'));
            }}
          >
            <Text style={styles.link}>Continue without biometrics</Text>
          </Pressable>
          <Pressable style={styles.linkBtn} onPress={() => void signOut()}>
            <Text style={styles.link}>Sign out</Text>
          </Pressable>
        </>
      ) : (
        <Pressable style={[styles.btn, busy && styles.btnDisabled]} disabled={busy} onPress={() => void signIn()}>
          <Text style={styles.btnText}>{busy ? 'Opening Google…' : 'Sign in with Google'}</Text>
        </Pressable>
      )}

      {!!note && <Text style={styles.note}>{note}</Text>}

      <Pressable
        style={styles.linkBtn}
        onPress={() => {
          void markLocked();
          setNote('Locked. Use Face ID next time.');
        }}
      >
        <Text style={styles.linkMuted}>Lock app</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  center: { flex: 1, alignItems: 'center', justifyContent: 'center', backgroundColor: colors.paper },
  screen: { flex: 1, backgroundColor: colors.paper, paddingHorizontal: 28, paddingTop: 96 },
  brand: { fontSize: 15, fontWeight: '700', letterSpacing: 0.4, color: colors.ink, marginBottom: 18 },
  title: { fontSize: 34, fontWeight: '600', color: colors.ink, marginBottom: 12 },
  copy: { fontSize: 16, lineHeight: 24, color: colors.ink2, marginBottom: 28 },
  meta: { fontSize: 14, color: colors.ink3, marginBottom: 16 },
  btn: {
    backgroundColor: colors.ink,
    paddingVertical: 16,
    paddingHorizontal: 18,
    alignItems: 'center',
  },
  btnDisabled: { opacity: 0.45 },
  btnText: { color: colors.paperHi, fontSize: 16, fontWeight: '600' },
  linkBtn: { marginTop: 18 },
  link: { fontSize: 15, color: colors.rubric, fontWeight: '600' },
  linkMuted: { fontSize: 13, color: colors.ink3 },
  note: { marginTop: 18, fontSize: 14, color: colors.rubric, lineHeight: 20 },
});
