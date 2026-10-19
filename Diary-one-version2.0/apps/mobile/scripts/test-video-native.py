#!/usr/bin/env python3
"""Real macOS AVFoundation regression; synthetic fixtures only, no network.

Run npm run test:video-native. FFMPEG/FFPROBE override PATH discovery;
DIARY_VIDEO_TEST_OUT retains fixtures/report at a chosen output directory.
Unsupported platforms/tools exit 2, not a successful or silently skipped test.
"""
from pathlib import Path
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile


def main():
    tools = {name: os.environ.get(name.upper()) or shutil.which(name)
             for name in ("ffmpeg", "ffprobe", "xcrun")}
    if platform.system() != "Darwin" or not all(tools.values()):
        print(json.dumps({"status": "UNSUPPORTED", "reason": "Requires macOS, Xcode/Swift, ffmpeg and ffprobe", "tools": tools}))
        return 2
    root = Path(__file__).resolve().parents[1]
    out = Path(os.environ["DIARY_VIDEO_TEST_OUT"]).expanduser().resolve() if os.environ.get("DIARY_VIDEO_TEST_OUT") else Path(tempfile.mkdtemp(prefix="diary-video-native-"))
    out.mkdir(parents=True, exist_ok=True)
    report = {"status": "RUNNING", "scope": "Actual app Swift timeline + macOS AVFoundation. No ONNX, UIKit or cloud calls.", "output": str(out), "cases": []}
    helper = root / "modules/diary-one-vision/ios/VideoFrameTimeline.swift"
    report["helper_sha256"] = hashlib.sha256(helper.read_bytes()).hexdigest()
    # Swift requires the top-level entry point to be named main.swift when
    # compiling multiple files. The helper is compiled directly from the repo.
    shutil.copyfile(root / "scripts/video-timeline-main.swift", out / "main.swift")
    build = subprocess.run([tools["xcrun"], "swiftc", "-O", str(helper), str(out / "main.swift"), "-o", str(out / "video-test")], capture_output=True, text=True, timeout=180)
    (out / "compile.txt").write_text(build.stdout + build.stderr)
    if build.returncode:
        raise RuntimeError(f"Swift harness compilation failed; see {out / 'compile.txt'}")
    encode = ["-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-movflags", "+faststart"]
    fixtures = []

    def generate(name, args, expected="ACCEPT"):
        file = out / f"{name}.mp4"
        command = [tools["ffmpeg"], "-y", "-nostdin", "-v", "error", *args, str(file)]
        generated = subprocess.run(command, capture_output=True, text=True, timeout=60)
        if generated.returncode:
            raise RuntimeError(f"Fixture {name} failed: {generated.stderr}")
        fixture = {"name": name, "file": file, "expected": expected, "generation_argv": command}
        fixtures.append(fixture)
        return fixture

    base = generate("fractional_10s_tail", ["-f", "lavfi", "-i", "testsrc2=size=320x180:rate=30:duration=10.01", *encode])
    offset = generate("positive_16ms", ["-f", "lavfi", "-i", "testsrc2=size=320x180:rate=30:duration=3", "-vf", "settb=1/1000,setpts=PTS+16", "-enc_time_base", "1/1000", "-fps_mode", "passthrough", *encode])
    generate("one_fps", ["-f", "lavfi", "-i", "testsrc2=size=320x180:rate=1:duration=11", *encode])
    generate("vfr", ["-f", "lavfi", "-i", "testsrc2=size=320x180:rate=30:duration=10", "-vf", "select='eq(n,0)+eq(n,1)+eq(n,27)+eq(n,75)+eq(n,150)+eq(n,270)'", "-fps_mode", "vfr", *encode])
    rotated = generate("rotated_90", ["-display_rotation:v:0", "90", "-i", str(base["file"]), "-c", "copy", "-movflags", "+faststart"])
    generate("one_ms", ["-f", "lavfi", "-i", "testsrc2=size=320x180:rate=1000", "-frames:v", "1", *encode])
    generate("empty_video_window", ["-f", "lavfi", "-i", "testsrc2=size=320x180:rate=1/20:duration=40", *encode], "REJECT")
    generate("audio_only", ["-f", "lavfi", "-i", "sine=frequency=440:duration=3", "-c:a", "aac", "-movflags", "+faststart"], "REJECT")
    for percentage in (90, 98):
        file = out / f"truncated_{percentage}.mp4"
        source = base["file"].read_bytes()
        file.write_bytes(source[:len(source) * percentage // 100])
        fixtures.append({"name": f"truncated_{percentage}", "file": file, "expected": "REJECT", "derivative_of": str(base["file"])})
    # Assert the intended positive offset was actually encoded. A 30fps time
    # base can otherwise round 16ms down to 0 and silently invalidate the test.
    probe = subprocess.run([tools["ffprobe"], "-v", "error", "-show_entries", "stream=start_time", "-of", "json", str(offset["file"])], capture_output=True, text=True, timeout=20)
    offset_start = float(json.loads(probe.stdout)["streams"][0]["start_time"])
    if abs(offset_start - .016) > .000001:
        raise AssertionError(f"Fixture has wrong start time: {offset_start}")
    report["positive_fixture_start_ms"] = offset_start * 1000
    rotation_probe = subprocess.run([tools["ffprobe"], "-v", "error", "-show_entries", "stream_side_data=rotation", "-of", "json", str(rotated["file"])], capture_output=True, text=True, timeout=20)
    rotations = [entry.get("rotation") for stream in json.loads(rotation_probe.stdout).get("streams", [])
                 for entry in stream.get("side_data_list", []) if "rotation" in entry]
    if not any(abs(float(value)) == 90 for value in rotations):
        raise AssertionError(f"Fixture rotation metadata missing or wrong: {rotations}")
    report["rotation_fixture_degrees"] = rotations
    def frame_times(name):
        fixture = next(item for item in fixtures if item["name"] == name)
        details = subprocess.run([tools["ffprobe"], "-v", "error", "-select_streams", "v:0", "-show_entries", "frame=best_effort_timestamp_time:format=duration", "-of", "json", str(fixture["file"])], capture_output=True, text=True, timeout=20)
        if details.returncode:
            raise AssertionError(f"Cannot inspect valid fixture {name}: {details.stderr}")
        data = json.loads(details.stdout)
        return [float(frame["best_effort_timestamp_time"]) for frame in data["frames"]], float(data["format"]["duration"])
    vfr_times, _ = frame_times("vfr")
    if len({round(b - a, 6) for a, b in zip(vfr_times, vfr_times[1:])}) <= 1:
        raise AssertionError("VFR fixture has no varying frame interval")
    low_times, _ = frame_times("one_fps")
    if len(low_times) < 2 or any(abs(b - a - 1) > .000001 for a, b in zip(low_times, low_times[1:])):
        raise AssertionError("Low FPS fixture does not contain one frame per second")
    _, tail_duration = frame_times("fractional_10s_tail")
    if not 10 < tail_duration < 10.1:
        raise AssertionError(f"Fractional-tail fixture has wrong duration: {tail_duration}")
    report["fixture_checks"] = {"vfr_sample_times_seconds": vfr_times, "low_fps_sample_count": len(low_times), "tail_duration_seconds": tail_duration}
    for fixture in fixtures:
        file = fixture["file"]
        record = {**fixture, "file": str(file), "sha256": hashlib.sha256(file.read_bytes()).hexdigest()}
        try:
            run = subprocess.run([str(out / "video-test"), str(file)], capture_output=True, text=True, timeout=60)
            (out / f"{fixture['name']}-stderr.txt").write_text(run.stderr)
            if run.returncode:
                raise RuntimeError(f"Native process exited {run.returncode}")
            result = json.loads(run.stdout)[0]
            record["result"] = result
            record["passed"] = result["status"] == fixture["expected"]
            if fixture["name"] == "rotated_90" and result["status"] == "ACCEPT":
                record["passed"] &= all(row["width"] == 180 and row["height"] == 320 for row in result["decoded_probes"])
            if fixture["name"] == "positive_16ms" and result["status"] == "ACCEPT":
                record["passed"] &= min(row["actual_ms"] for row in result["decoded_probes"]) >= 16
        except (subprocess.TimeoutExpired, ValueError, RuntimeError) as error:
            record["passed"] = False
            record["harness_error"] = str(error)
        report["cases"].append(record)
        (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
        print(f"{'PASS' if record['passed'] else 'FAIL'} {fixture['name']}: expected {fixture['expected']}", flush=True)
    report["passed"] = sum(row["passed"] for row in report["cases"])
    report["failed"] = len(fixtures) - report["passed"]
    report["status"] = "PASS" if not report["failed"] else "FAIL"
    (out / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "passed": report["passed"], "failed": report["failed"], "report": str(out / 'report.json')}))
    return 0 if not report["failed"] else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as error:
        print(json.dumps({"status": "ERROR", "error": str(error)}), file=sys.stderr)
        sys.exit(1)
