#!/usr/bin/env python3
"""
Compress public/videos/*.mp4 to a web-friendly bitrate before HLS segmentation.

Skip rules (any one matches → skip):
  - file size < 5 MB
  - video bitrate < 2 Mbps
  - height <= 720

Compression params:
  - scale to 720p (height=720, width auto, even)
  - H.264 high profile, level 4.0, preset slow
  - video bitrate 1500 kbps (max 2000, buf 3000)
  - AAC 96 kbps audio
  - +faststart so the moov atom is at the head — progressive playback starts
    as soon as the first KB arrives.

Idempotent: re-running skips files that already meet the targets.
Atomic replace: writes <name>.compressed.mp4 first, mv overwrites on success.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except (AttributeError, OSError):
    pass

VIDEOS_DIR = Path(__file__).resolve().parent.parent / "public" / "videos"

SIZE_SKIP_MB = 5.0
BITRATE_SKIP_KBPS = 2000
HEIGHT_SKIP = 720

TARGET_HEIGHT = 720
TARGET_VIDEO_KBPS = 1500
TARGET_VIDEO_MAX_KBPS = 2000
TARGET_VIDEO_BUF_KBPS = 3000
TARGET_AUDIO_KBPS = 96


def require_tool(name: str) -> None:
    if shutil.which(name) is None:
        sys.exit(f"ERROR: '{name}' not found on PATH. Install ffmpeg first.")


def ffprobe_meta(mp4: Path) -> dict:
    """Return {bitrate_kbps, height, size_mb} from ffprobe."""
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=height,bit_rate",
        "-show_entries", "format=size,bit_rate",
        "-of", "default=noprint_wrappers=1",
        str(mp4),
    ]
    out = subprocess.run(cmd, capture_output=True, text=True, check=True, encoding="utf-8", errors="replace")
    meta = {"bitrate_kbps": 0, "height": 0, "size_mb": 0.0}
    stream_bitrate = None
    format_bitrate = None
    for line in out.stdout.splitlines():
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        v = v.strip()
        if v == "N/A" or not v:
            continue
        if k == "height":
            meta["height"] = int(v)
        elif k == "bit_rate":
            try:
                if stream_bitrate is None:
                    stream_bitrate = int(v) // 1000
                else:
                    format_bitrate = int(v) // 1000
            except ValueError:
                pass
        elif k == "size":
            try:
                meta["size_mb"] = int(v) / (1024 * 1024)
            except ValueError:
                pass
    # Prefer stream bitrate; fall back to format bitrate.
    meta["bitrate_kbps"] = stream_bitrate or format_bitrate or 0
    return meta


def should_skip(meta: dict) -> tuple[bool, str]:
    if meta["size_mb"] < SIZE_SKIP_MB:
        return True, f"<{SIZE_SKIP_MB}MB"
    if meta["bitrate_kbps"] and meta["bitrate_kbps"] < BITRATE_SKIP_KBPS:
        return True, f"<{BITRATE_SKIP_KBPS}kbps"
    if meta["height"] and meta["height"] <= HEIGHT_SKIP:
        return True, f"<={HEIGHT_SKIP}p"
    return False, ""


def compress_one(mp4: Path) -> dict:
    """Compress in place. Returns dict with status + before/after meta."""
    before = ffprobe_meta(mp4)
    skip, reason = should_skip(before)
    if skip:
        return {"name": mp4.name, "status": "skipped", "reason": reason, "before": before, "after": before}

    tmp = mp4.with_suffix(".compressed.mp4")
    cmd = [
        "ffmpeg", "-y", "-i", str(mp4),
        "-vf", f"scale=-2:{TARGET_HEIGHT}",
        "-c:v", "libx264",
        "-preset", "slow",
        "-b:v", f"{TARGET_VIDEO_KBPS}k",
        "-maxrate", f"{TARGET_VIDEO_MAX_KBPS}k",
        "-bufsize", f"{TARGET_VIDEO_BUF_KBPS}k",
        "-profile:v", "high",
        "-level", "4.0",
        "-c:a", "aac",
        "-b:a", f"{TARGET_AUDIO_KBPS}k",
        "-movflags", "+faststart",
        str(tmp),
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, encoding="utf-8", errors="replace")
    except subprocess.CalledProcessError as e:
        if tmp.exists():
            tmp.unlink()
        return {"name": mp4.name, "status": "error", "reason": (e.stderr or "")[-300:], "before": before, "after": before}

    after = ffprobe_meta(tmp)
    # Sanity check: compressed should be smaller. If not, abort.
    if after["size_mb"] >= before["size_mb"] * 0.95:
        tmp.unlink()
        return {"name": mp4.name, "status": "no-gain", "reason": "compressed not smaller", "before": before, "after": after}

    # Atomic-ish replace.
    mp4.unlink()
    tmp.rename(mp4)
    return {"name": mp4.name, "status": "compressed", "reason": "", "before": before, "after": after}


def main() -> None:
    require_tool("ffmpeg")
    require_tool("ffprobe")
    if not VIDEOS_DIR.is_dir():
        sys.exit(f"ERROR: videos directory not found: {VIDEOS_DIR}")

    mp4s = sorted(VIDEOS_DIR.glob("*.mp4"))
    if not mp4s:
        sys.exit("No .mp4 files found in public/videos/")

    print(f"Found {len(mp4s)} .mp4 files. Target: {TARGET_HEIGHT}p / {TARGET_VIDEO_KBPS}kbps\n")

    rows: list[dict] = []
    for i, mp4 in enumerate(mp4s, 1):
        print(f"[{i}/{len(mp4s)}] {mp4.name}", flush=True)
        try:
            row = compress_one(mp4)
        except Exception as e:
            row = {"name": mp4.name, "status": "error", "reason": str(e), "before": {}, "after": {}}
        b = row.get("before", {})
        a = row.get("after", {})
        if row["status"] == "compressed":
            print(f"   compressed: {b.get('size_mb',0):.1f}MB/{b.get('bitrate_kbps',0)}kbps -> "
                  f"{a.get('size_mb',0):.1f}MB/{a.get('bitrate_kbps',0)}kbps")
        elif row["status"] == "skipped":
            print(f"   skipped ({row['reason']}): {b.get('size_mb',0):.1f}MB/{b.get('bitrate_kbps',0)}kbps "
                  f"{b.get('height',0)}p")
        else:
            print(f"   {row['status']}: {row['reason']}")
        rows.append(row)

    print("\n=== Summary ===")
    by = {"compressed": 0, "skipped": 0, "error": 0, "no-gain": 0}
    saved_mb = 0.0
    for r in rows:
        by[r["status"]] = by.get(r["status"], 0) + 1
        if r["status"] == "compressed":
            saved_mb += r["before"]["size_mb"] - r["after"]["size_mb"]
    print(f"Compressed: {by['compressed']}, skipped: {by['skipped']}, "
          f"errors: {by['error']}, no-gain: {by['no-gain']}")
    print(f"Saved: {saved_mb:.1f} MB")


if __name__ == "__main__":
    main()
