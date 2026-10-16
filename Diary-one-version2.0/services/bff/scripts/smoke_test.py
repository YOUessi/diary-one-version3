"""Quick smoke test against local BFF (no multipart). Run after docker compose up."""

import os
import sys
import urllib.request

BASE = os.environ.get("BFF_URL", "http://127.0.0.1:8790")


def main() -> int:
    url = f"{BASE.rstrip('/')}/health"
    try:
        with urllib.request.urlopen(url, timeout=5) as res:
            body = res.read().decode()
            print(f"OK {res.status} {body}")
            return 0
    except Exception as exc:
        print(f"FAIL {url}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
