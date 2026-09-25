"""Validate or explicitly run frozen V1.75 on an already-normalized Bundle."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / "src"))

from diary_one_ci import codex_d5_research as research
from diary_one_ci.bundle import load_app_library_bundle
from diary_one_ci.x01_server import _resolve_qwen_api_key


ENDPOINT = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--confirm-dashscope-beijing", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    bundle = load_app_library_bundle(args.manifest)
    summary = {
        "status": "BUNDLE_VALIDATED_NO_API",
        "manifest": str(args.manifest.resolve()),
        "assets": len(bundle.manifest["assets"]),
        "research_profile": research.profile(),
        "external_destination_if_live": ENDPOINT,
    }
    if not args.live:
        if args.confirm_dashscope_beijing or args.output is not None:
            parser.error("--confirm-dashscope-beijing and --output are live-only")
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return

    if not args.confirm_dashscope_beijing:
        parser.error("Live execution requires --confirm-dashscope-beijing")
    if args.output is None:
        parser.error("Live execution requires a new --output path")
    if args.output.exists():
        parser.error("Refusing to overwrite an existing output")

    key, credential_source = _resolve_qwen_api_key()
    if not key:
        parser.error("No DashScope credential found in Keychain or DASHSCOPE_API_KEY")
    gateway = research.make_gateway(key)
    report = research.run_research(args.manifest, gateway)
    envelope = {
        "algorithm_candidate": "V1.75",
        "quality_status": "REAL_CHAIN_RETURNED_NOT_HUMAN_ACCEPTED",
        "credential_source": credential_source,
        "external_destination": ENDPOINT,
        **report,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(envelope, stream, ensure_ascii=False, indent=2, default=str)
        stream.write("\n")
    print(args.output.resolve())


if __name__ == "__main__":
    main()
