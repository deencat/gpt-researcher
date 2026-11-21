import { router } from 'expo-router';
import * as Speech from 'expo-speech';
import { ExpoSpeechRecognitionModule, useSpeechRecognitionEvent } from 'expo-speech-recognition';
import { useEffect, useMemo, useState } from 'react';
import { ActivityIndicator, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { askVoiceChat, type ChatTurn } from '../src/api';
import { getSession, isUnlocked, markLocked } from '../src/session';
import { colors } from '../src/theme';

export default function VoiceChatScreen() {
  const [turns, setTurns] = useState<ChatTurn[]>([]);
  const [draft, setDraft] = useState('');
  const [listening, setListening] = useState(false);
  const [thinking, setThinking] = useState(false);
  const [error, setError] = useState('');
  const [email, setEmail] = useState('');

  useEffect(() => {
    void (async () => {
      const session = await getSession();
      if (!session || !(await isUnlocked())) {
        router.replace('/');
        return;
      }
      setEmail(session.email);
    })();
  }, []);

  useSpeechRecognitionEvent('result', (event) => {
    const text = event.results[0]?.transcript?.trim() ?? '';
    if (text) setDraft(text);
  });
  useSpeechRecognitionEvent('end', () => setListening(false));
  useSpeechRecognitionEvent('error', (event) => {
    setListening(false);
    setError(event.message || 'Speech recognition failed.');
  });

  const canSend = useMemo(() => Boolean(draft.trim()) && !thinking && !listening, [draft, thinking, listening]);

  const startListening = async () => {
    setError('');
    Speech.stop();
    const perm = await ExpoSpeechRecognitionModule.requestPermissionsAsync();
    if (!perm.granted) {
      setError('Microphone / speech permission is required for voice chat.');
      return;
    }
    setDraft('');
    setListening(true);
    ExpoSpeechRecognitionModule.start({
      lang: 'en-US',
      interimResults: true,
      continuous: false,
    });
  };

  const stopListening = () => {
    ExpoSpeechRecognitionModule.stop();
    setListening(false);
  };

  const send = async () => {
    const q = draft.trim();
    if (!q || thinking) return;
    setThinking(true);
    setError('');
    const next: ChatTurn[] = [...turns, { role: 'user', content: q }];
    setTurns(next);
    setDraft('');
    try {
      const answer = await askVoiceChat(next);
      setTurns([...next, { role: 'assistant', content: answer }]);
      Speech.speak(answer, { language: 'en-US', rate: 0.96 });
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setThinking(false);
    }
  };

  const lock = async () => {
    Speech.stop();
    stopListening();
    await markLocked();
    router.replace('/');
  };

  return (
    <View style={styles.screen}>
      <Text style={styles.meta}>{email}</Text>
      <ScrollView style={styles.thread} contentContainerStyle={styles.threadPad}>
        {turns.length === 0 && (
          <Text style={styles.empty}>
            Tap Mic, ask a research question, stop, then Ask. Replies are spoken aloud.
          </Text>
        )}
        {turns.map((t, i) => (
          <View key={`${t.role}-${i}`} style={[styles.bubble, t.role === 'user' ? styles.user : styles.assistant]}>
            <Text style={t.role === 'user' ? styles.userText : styles.assistantText}>{t.content}</Text>
          </View>
        ))}
        {thinking && <ActivityIndicator color={colors.ink} style={{ marginTop: 12 }} />}
      </ScrollView>

      {!!draft && (
        <View style={styles.draftBox}>
          <Text style={styles.draftLabel}>{listening ? 'Listening…' : 'Heard'}</Text>
          <Text style={styles.draft}>{draft}</Text>
        </View>
      )}
      {!!error && <Text style={styles.error}>{error}</Text>}

      <View style={styles.row}>
        <Pressable
          style={[styles.mic, listening && styles.micOn]}
          onPress={() => void (listening ? stopListening() : startListening())}
        >
          <Text style={[styles.micText, listening && styles.micTextOn]}>{listening ? 'Stop' : 'Mic'}</Text>
        </Pressable>
        <Pressable style={[styles.send, !canSend && styles.disabled]} disabled={!canSend} onPress={() => void send()}>
          <Text style={styles.sendText}>Ask</Text>
        </Pressable>
        <Pressable style={styles.lock} onPress={() => void lock()}>
          <Text style={styles.lockText}>Lock</Text>
        </Pressable>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.paper, paddingHorizontal: 16, paddingBottom: 24 },
  meta: { fontSize: 12, color: colors.ink3, marginTop: 8, marginBottom: 4 },
  thread: { flex: 1 },
  threadPad: { paddingVertical: 12, gap: 10 },
  empty: { fontSize: 15, lineHeight: 22, color: colors.ink2, paddingTop: 24 },
  bubble: { padding: 14, maxWidth: '92%' },
  user: { alignSelf: 'flex-end', backgroundColor: colors.ink },
  assistant: { alignSelf: 'flex-start', backgroundColor: colors.paperHi, borderWidth: 1, borderColor: colors.rule },
  userText: { fontSize: 15, lineHeight: 22, color: colors.paperHi },
  assistantText: { fontSize: 15, lineHeight: 22, color: colors.ink },
  draftBox: { borderTopWidth: 1, borderTopColor: colors.rule, paddingTop: 10, marginBottom: 8 },
  draftLabel: { fontSize: 11, letterSpacing: 0.8, textTransform: 'uppercase', color: colors.ink3, marginBottom: 4 },
  draft: { fontSize: 16, color: colors.ink, lineHeight: 22 },
  error: { color: colors.rubric, marginBottom: 8, fontSize: 13 },
  row: { flexDirection: 'row', gap: 10, alignItems: 'center' },
  mic: { flex: 1, backgroundColor: colors.paperHi, borderWidth: 1, borderColor: colors.ink, paddingVertical: 16, alignItems: 'center' },
  micOn: { backgroundColor: colors.rubric, borderColor: colors.rubric },
  micText: { color: colors.ink, fontWeight: '700', fontSize: 16 },
  micTextOn: { color: colors.paperHi },
  send: { flex: 1, backgroundColor: colors.ink, paddingVertical: 16, alignItems: 'center' },
  sendText: { color: colors.paperHi, fontWeight: '700', fontSize: 16 },
  disabled: { opacity: 0.4 },
  lock: { paddingHorizontal: 12, paddingVertical: 16 },
  lockText: { color: colors.ink3, fontWeight: '600' },
});
