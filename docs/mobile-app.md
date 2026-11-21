# Hexsenses mobile app (Face ID + voice chat)

Thin Expo (React Native) client under `/mobile`. It is **not** a full research UI port — only:

1. **Google sign-in once** via the existing oauth2-proxy site  
2. **Face ID / biometrics** to unlock the stored session on later opens  
3. **Voice chat** (speech → `/api/chat` → spoken reply)

## Why this shape

| Need | Approach |
| --- | --- |
| Face ID | `expo-local-authentication` after a Secure Store session exists (Apple does not use Face ID as the identity provider) |
| Voice | `expo-speech-recognition` + `expo-speech` around the existing FastAPI `/api/chat` |
| Auth | Browser auth session → `/mobile/auth` bridge → `hexsenses://auth?email=…` |

The full Next.js research UI stays on the web. The app unlocks and talks.

## Run locally

```bash
cd mobile
npm install
npx expo start
```

Use a **development build** for Face ID and on-device speech (`npx expo run:ios` / EAS). Expo Go does not fully support Face ID.

Optional:

```bash
EXPO_PUBLIC_API_BASE=https://research.hexsenses.com
```

## Store builds

```bash
cd mobile
npx eas-cli@latest build --platform ios
npx eas-cli@latest build --platform android
```

Configure Apple / Google Play credentials in EAS. Bundle IDs: `com.hexsenses.research`.

## Server pieces

- `frontend/nextjs/app/mobile/auth/route.ts` — after Google login, redirects into the app with the signed-in email  
- Chat uses `POST /api/chat` with a short voice-mode context string (no full report required)

## Follow-ups

- Cookie / JWT passthrough so `/api/chat` works when the mobile WebView cookie jar is empty  
- Cantonese / `zh-HK` speech locale toggle  
- Optional report picker so voice chat can ground on a specific research run  
