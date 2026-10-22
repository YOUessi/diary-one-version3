"""Replace a local JSON snapshot only after its complete contents reach disk."""
import json
import os
import tempfile
from pathlib import Path


def write_json_atomic(path: Path, value) -> None:
    data = json.dumps(value, ensure_ascii=False, allow_nan=False).encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)
