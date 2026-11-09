#!/usr/bin/env python3
"""Local read-only, HTTP Range-enabled video source player for Diary One.

Security properties: loopback only, exact source IDs from six authoritative
sanitized bundle.json files, no arbitrary path queries, no modification or
upload of any source file. Serves the Chapter review and bytes from original
10-second source MP4s. Browser trims to a 3-second window on playback.
"""
from __future__ import annotations

import argparse
from functools import partial
from http import HTTPStatus
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import json
import logging
import os
from pathlib import Path
import re
import subprocess
import sys
import threading
from urllib.parse import urlsplit, unquote

HOME = Path.home()
ROOT = HOME / "Documents/Nexleap/work_logs/evidence"
REVIEW = ROOT / "sydney-six-offset-image-vs-video-20261109"
VIDEOS = HOME / "Downloads/视频切分_10s_悉尼_20261027/sydney"
OFFSETS = (10,20,30,50,60,70)
DEFAULT_PORT = 8810
FFMPEG = HOME / "miniforge3/bin/ffmpeg"
CACHE = REVIEW / "live_preview_cache"
_ENCODE_LOCK = threading.Lock()
ASSET_RE = re.compile(r"^sydney_(?:01|02|03|05|06|07)_(\d{6})$")


def allowed_sources() -> dict[str, Path]:
    allowed: dict[str, Path] = {}
    source_root = VIDEOS.resolve()
    for offset in OFFSETS:
        p = ROOT / f"sydney-intro-cut-72s-20261105/offset_{offset:03d}/input/bundle.json"
        data = json.loads(p.read_text())
        if len(data.get("assets", [])) != 160:
            raise ValueError(f"Unexpected Sydney source bundle size: {p}")
        for asset in data["assets"]:
            name = asset["asset_id"]
            match = ASSET_RE.fullmatch(name)
            if not match:
                raise ValueError(f"Unrecognized source identifier {name}")
            index = int(match.group(1))
            original_start = (index - 1) * 10
            if original_start < 80:
                raise ValueError(f"Intro media was not excluded: {name}")
            found = list(VIDEOS.glob(f"sydney_{index:06d}_*.mp4"))
            if len(found) != 1:
                raise FileNotFoundError(f"Source clip not uniquely located: {name}")
            source = found[0].resolve()
            if source_root not in source.parents:
                raise ValueError(f"Unsafe video source outside clip directory: {name}")
            if name in allowed:
                raise ValueError(f"Duplicated source ID: {name}")
            allowed[name] = source
    if len(allowed) != 960:
        raise ValueError(f"Expected 960 known video assets, got {len(allowed)}")
    return allowed


class PreviewHandler(SimpleHTTPRequestHandler):
    sources: dict[str, Path] = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(REVIEW), **kwargs)

    def log_message(self, fmt, *args):
        # Include only HTTP status and source ID; keep paths and tokens private.
        logging.info("%s - %s", self.address_string(), fmt % args)

    def _http_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cross-Origin-Resource-Policy", "cross-origin")

    def do_HEAD(self):
        self._handle_request(head_only=True)

    def do_GET(self):
        self._handle_request(head_only=False)

    def _handle_request(self, head_only:bool):
        path = unquote(urlsplit(self.path).path)
        if path == "/favicon.ico":
            self.send_response(HTTPStatus.NO_CONTENT)
            self.send_header("Content-Length","0")
            self.end_headers()
            return
        if path.startswith("/api/live3s/"):
            pattern = re.fullmatch(r"/api/live3s/(sydney_(?:01|02|03|05|06|07)_\d{6})/(\d{1,4})\.mp4",path)
            if not pattern:
                self.send_error(HTTPStatus.NOT_FOUND,"Invalid Live preview source")
                return
            asset,focus_text=pattern.groups()
            focus_ms=int(focus_text)
            if asset not in self.sources or not (0<=focus_ms<10000):
                self.send_error(HTTPStatus.NOT_FOUND,"Original video or focus PTS unavailable")
                return
            try:
                real_movie=self._clip_3s(asset,focus_ms)
            except Exception as exc:
                logging.exception("Live encoding failure %s focus %d",asset,focus_ms)
                self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR,"Live preview failed")
                return
            return self._serve_source(real_movie,head_only=head_only)
        if path == "/healthz":
            body = json.dumps({"ok": True, "video_assets": len(self.sources),
                               "player": "cached_real_3s_clip", "server": "loopback"}).encode()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self._http_headers()
            self.end_headers()
            if not head_only:
                self.wfile.write(body)
            return
        if path == "/":
            self.path = "/SIX_GROUPS_JPEG_VS_VIDEO_REAL_CHAPTER_COMPARISON.html"
            return super().do_HEAD() if head_only else super().do_GET()
        if path.startswith("/api/source/"):
            aid = path.removeprefix("/api/source/").removesuffix(".mp4")
            if path != f"/api/source/{aid}.mp4" or aid not in self.sources:
                self.send_error(HTTPStatus.NOT_FOUND,"Unknown source video")
                return
            return self._serve_source(self.sources[aid],head_only=head_only)
        return super().do_HEAD() if head_only else super().do_GET()

    def _clip_3s(self, asset:str, focus_ms:int) -> Path:
        """Render on first click, reuse the same real source clip on subsequent plays."""
        CACHE.mkdir(exist_ok=True,parents=True)
        source=self.sources[asset]
        output=CACHE/f"{asset}_focus{focus_ms:04d}_3s.mp4"
        if output.is_file() and output.stat().st_size>1000 and output.stat().st_mtime>=source.stat().st_mtime:
            return output
        with _ENCODE_LOCK:
            # Race-safe: check after acquiring lock.
            if output.is_file() and output.stat().st_size>1000 and output.stat().st_mtime>=source.stat().st_mtime:
                return output
            start=max(0.0,min(focus_ms/1000.0-1.5,7.0))
            temp=CACHE/f".{asset}_focus{focus_ms:04d}.tmp.mp4"
            command=[str(FFMPEG),"-hide_banner","-loglevel","error",
                     "-nostdin","-y",
                     "-ss",f"{start:.3f}","-i",str(source),"-t","3.0",
                     "-an","-vf","fps=24,scale=960:540:flags=bicubic,format=yuv420p",
                     "-c:v","libx264","-preset","veryfast","-crf","26",
                     "-movflags","+faststart",str(temp)]
            try:
                result=subprocess.run(command,capture_output=True,text=True,timeout=90)
                if result.returncode!=0 or not temp.is_file() or temp.stat().st_size<2000:
                    raise RuntimeError(f"FFmpeg 3s preview failed code={result.returncode}: {result.stderr[-350:]}")
                os.replace(temp,output)
            finally:
                temp.unlink(missing_ok=True)
            return output

    def _serve_source(self, video:Path, head_only:bool):
        length=video.stat().st_size
        range_header=self.headers.get("Range")
        start=0
        end=length-1
        code=HTTPStatus.OK
        if range_header:
            pattern=re.fullmatch(r"bytes=(\d*)-(\d*)",range_header.strip())
            if not pattern:
                self._unsatisfiable(length)
                return
            a,b=pattern.groups()
            if not a and not b:
                self._unsatisfiable(length)
                return
            if not a:
                count=int(b)
                if count<=0:
                    self._unsatisfiable(length)
                    return
                start=max(0,length-count)
            else:
                start=int(a)
                end=int(b) if b else length-1
            if start>=length or end<start:
                self._unsatisfiable(length)
                return
            end=min(end,length-1)
            code=HTTPStatus.PARTIAL_CONTENT
        self.send_response(code)
        self.send_header("Content-Type","video/mp4")
        self.send_header("Accept-Ranges","bytes")
        self.send_header("Content-Length",str(end-start+1))
        self.send_header("Cache-Control","private,max-age=600")
        if code==HTTPStatus.PARTIAL_CONTENT:
            self.send_header("Content-Range",f"bytes {start}-{end}/{length}")
        self._http_headers()
        self.end_headers()
        if head_only:return
        remaining=end-start+1
        try:
            with video.open("rb") as f:
                f.seek(start)
                while remaining:
                    blob=f.read(min(1024*1024,remaining))
                    if not blob:break
                    self.wfile.write(blob)
                    remaining-=len(blob)
        except (BrokenPipeError,ConnectionResetError):
            pass

    def _unsatisfiable(self,length):
        self.send_response(HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE)
        self.send_header("Content-Range",f"bytes */{length}")
        self.send_header("Content-Length","0")
        self._http_headers()
        self.end_headers()


def serve(port:int=DEFAULT_PORT):
    if not REVIEW.is_dir() or not (REVIEW/"SIX_GROUPS_JPEG_VS_VIDEO_REAL_CHAPTER_COMPARISON.html").is_file():
        raise FileNotFoundError("Review HTML not found")
    PreviewHandler.sources=allowed_sources()
    httpd=ThreadingHTTPServer(("127.0.0.1",port),PreviewHandler)
    httpd.daemon_threads=True
    print(f"READY http://127.0.0.1:{port}/ | original 10s source assets {len(PreviewHandler.sources)}",flush=True)
    try:
        httpd.serve_forever(poll_interval=.2)
    finally:
        httpd.server_close()


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--port",type=int,default=DEFAULT_PORT)
    args=parser.parse_args()
    if args.port<1024 or args.port>65535:
        raise ValueError("Port out of supported range")
    logging.basicConfig(level=logging.WARNING)
    serve(args.port)
