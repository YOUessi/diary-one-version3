# Diary One 2.0 handoff

This folder is the 2026-10-16 internal-beta snapshot. Server secrets are not included.

Preview BFF URL already set in `apps/mobile/eas.json`:

`https://bff.diary.luxe`

## Remaining tasks

1. Apple Developer → Identifiers → `com.nexleap.diaryone.dev` → enable Sign in with Apple.
   After the App Store Connect app exists, put its numeric Apple ID into `apps/mobile/eas.json` → `submit.preview.ios.ascAppId`.
2. Optional Google sign-in: set these in `eas.json` → `build.preview.env`:
   - `EXPO_PUBLIC_GOOGLE_WEB_CLIENT_ID`
   - `EXPO_PUBLIC_GOOGLE_IOS_CLIENT_ID`
   Email OTP and Apple sign-in can ship without them.
3. Build and submit TestFlight:

```powershell
cd Diary-one-version2.0/apps/mobile
npx eas-cli login
npx eas-cli build --profile preview --platform ios
npx eas-cli submit --profile preview --platform ios
```

Full notes: `docs/TEAM_PACK_HANDOFF.md`.

Do not commit DashScope keys, SMTP passwords, or the server `.env`. Do not change `EXPO_PUBLIC_DEV_BFF_URL` back to a temporary tunnel.
