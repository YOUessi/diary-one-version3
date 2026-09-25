# Web source snapshot state

Snapshot date: 2026-09-17  
Source base commit: `4336bc80d56777158dd00c58b5be6e8caac6a2e9`  
Source worktree at capture: dirty; current tracked and untracked working files are included in this snapshot.  
Git history: not included.  
Dependencies/build caches: not included.  
Credentials, `.env*`, media, run audits and model replies: not included.

Verification performed before capture:

- `npm run build`: passed;
- `npm run lint`: passed;
- `npm test`: 58 tests, 57 passed, 1 failed;
- failure: runtime-policy version handshake ambiguity, documented in the parent handoff `04_V175_INTEGRATION_TASK.md`.

This source snapshot is the current local test-lab implementation. It is not a V1.75 Web integration and must not be published as one.
