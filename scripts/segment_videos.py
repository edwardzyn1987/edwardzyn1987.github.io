#!/usr/bin/env python3
"""
Segment public/videos/*.mp4 into HLS playlists for fast mobile playback.

For each <basename>.mp4:
  - Output: public/videos/<basename>/playlist.m3u8 + seg000.ts, seg001.ts, ...
  - Pass 1: stream copy (no re-encode, zero quality loss). Requires keyframes
    near each segment boundary, otherwise segment durations drift.
  - Pass 2 (fallback): re-encode H.264 at CRF 18 with GOP=2s, audio copy.
  - Idempotent: skip if playlist.m3u8 already exists.

The original .mp4 stays in place as fallback for the player.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

# Windows: ensure stdout/stderr accept UTF-8 (Chinese filenames in output).
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except (AttributeError, OSError):
    pass

VIDEOS_DIR = Path(__file__).resolve().parent.parent / "public" / "videos"
SEGMENT_SECONDS = 4
KEYFRAME_TOLERANCE = 0.5  # seconds — allow drift around the 4s boundary


def require_tool(name: str) -> None:
    if shutil.which(name) is None:
        sys.exit(f"ERROR: '{name}' not found on PATH. Install ffmpeg first.")


def ffprobe_keyframe_times(mp4: Path) -> list[float]:
    """Return list of keyframe timestamps (seconds) for the video stream."""
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-skip_frame", "nokey",
        "-show_entries", "frame=pts_time",
        "-of", "csv=p=0",
        str(mp4),
    ]
    out = subprocess.run(cmd, capture_output=True, text=True, check=True)
    times: list[float] = []
    for line in out.stdout.splitlines():
        line = line.strip().rstrip(",")
        if not line:
            continue
        try:
            times.append(float(line))
        except ValueError:
            pass
    return times


def keyframes_aligned(keyframes: list[float], duration: float) -> bool:
    """
    Check whether keyframes fall close to multiples of SEGMENT_SECONDS.
    A keyframe must exist within KEYFRAME_TOLERANCE of every segment boundary
    (excluding the final partial segment).
    """
    if not keyframes:
        return False
    boundary = SEGMENT_SECONDS
    while boundary < duration - KEYFRAME_TOLERANCE:
        nearest = min(keyframes, key=lambda t: abs(t - boundary))
        if abs(nearest - boundary) > KEYFRAME_TOLERANCE:
            return False
        boundary += SEGMENT_SECONDS
    return True


def media_duration(mp4: Path) -> float:
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "csv=p=0",
        str(mp4),
    ]
    out = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def clear_dir(d: Path) -> None:
    for f in d.iterdir():
        f.unlink()


def run_hls_copy(mp4: Path, out_dir: Path) -> bool:
    cmd = [
        "ffmpeg", "-y", "-i", str(mp4),
        "-c", "copy",
        "-bsf:v", "h264_mp4toannexb",
        "-hls_time", str(SEGMENT_SECONDS),
        "-hls_segment_type", "mpegts",
        "-hls_list_size", "0",
        "-hls_segment_filename", str(out_dir / "seg%03d.ts"),
        "-f", "hls", str(out_dir / "playlist.m3u8"),
    ]
    result = subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="replace")
    return result.returncode == 0


def run_hls_reencode(mp4: Path, out_dir: Path) -> None:
    # Capped-CRF (constrained quality): CRF drives quality, maxrate hard-caps the
    # bitrate so uneven/high-motion segments can't balloon. This replaced the old
    # bare "-crf 18" which produced 4-6 MB segments that stalled playback over the
    # CDN. -force_key_frames places a keyframe exactly every SEGMENT_SECONDS so the
    # HLS splitter aligns cleanly even on fractional-fps sources (25.1, 24.7, …),
    # which the old fixed "-g 48" could not. Audio is stream-copied (sources are
    # already AAC ~100 kbps — re-encoding would add loss for nothing).
    cmd = [
        "ffmpeg", "-y", "-i", str(mp4),
        "-c:v", "libx264", "-crf", "23",
        "-maxrate", "1500k", "-bufsize", "3000k", "-preset", "medium",
        "-force_key_frames", f"expr:gte(t,n_forced*{SEGMENT_SECONDS})",
        "-c:a", "copy",
        "-hls_time", str(SEGMENT_SECONDS),
        "-hls_segment_type", "mpegts",
        "-hls_list_size", "0",
        "-hls_segment_filename", str(out_dir / "seg%03d.ts"),
        "-f", "hls", str(out_dir / "playlist.m3u8"),
    ]
    subprocess.run(cmd, check=True, capture_output=True, encoding="utf-8", errors="replace")


def folder_size_mb(d: Path) -> float:
    return sum(f.stat().st_size for f in d.iterdir() if f.is_file()) / (1024 * 1024)


def segment_count(d: Path) -> int:
    return sum(1 for f in d.glob("seg*.ts"))


def segment_one(mp4: Path, force: bool = False) -> dict:
    basename = mp4.stem
    out_dir = VIDEOS_DIR / basename
    playlist = out_dir / "playlist.m3u8"

    if playlist.exists() and not force:
        return {
            "name": basename,
            "mode": "skipped",
            "segments": segment_count(out_dir),
            "size_mb": folder_size_mb(out_dir),
        }

    out_dir.mkdir(parents=True, exist_ok=True)
    if force:
        clear_dir(out_dir)  # re-segment from scratch: drop old segments + playlist

    duration = media_duration(mp4)
    keyframes = ffprobe_keyframe_times(mp4)
    aligned = keyframes_aligned(keyframes, duration)

    mode = "copy"
    if aligned and run_hls_copy(mp4, out_dir):
        # success — keep output
        pass
    else:
        clear_dir(out_dir)
        run_hls_reencode(mp4, out_dir)
        mode = "reencode"

    return {
        "name": basename,
        "mode": mode,
        "segments": segment_count(out_dir),
        "size_mb": folder_size_mb(out_dir),
    }


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Segment public/videos/*.mp4 into HLS.")
    parser.add_argument("--force", action="store_true",
                        help="Re-segment even if playlist.m3u8 already exists (clears the folder first).")
    parser.add_argument("--only", metavar="FILE",
                        help="Restrict to the video basenames listed (one per line) in FILE.")
    args = parser.parse_args()

    require_tool("ffmpeg")
    require_tool("ffprobe")

    if not VIDEOS_DIR.is_dir():
        sys.exit(f"ERROR: videos directory not found: {VIDEOS_DIR}")

    mp4s = sorted(VIDEOS_DIR.glob("*.mp4"))
    if not mp4s:
        sys.exit("No .mp4 files found in public/videos/")

    if args.only:
        # splitlines() handles CRLF/LF/CR — do NOT use split("\n") (leaves \r → no match).
        wanted = {line.strip() for line in Path(args.only).read_text(encoding="utf-8").splitlines() if line.strip()}
        mp4s = [m for m in mp4s if m.stem in wanted]
        missing = wanted - {m.stem for m in mp4s}
        print(f"--only: {len(wanted)} names requested, {len(mp4s)} matched"
              + (f", {len(missing)} not found: {sorted(missing)[:3]}…" if missing else ""))
        if not mp4s:
            sys.exit("ERROR: --only matched no videos (check names / CRLF).")

    print(f"Processing {len(mp4s)} .mp4 files. Output dir: {VIDEOS_DIR}"
          + (" [--force]" if args.force else "") + "\n")

    rows: list[dict] = []
    for i, mp4 in enumerate(mp4s, 1):
        print(f"[{i}/{len(mp4s)}] {mp4.name} ... ", end="", flush=True)
        try:
            row = segment_one(mp4, force=args.force)
            print(f"{row['mode']:8} segments={row['segments']:3} size={row['size_mb']:6.2f} MB")
        except subprocess.CalledProcessError as e:
            print("FAILED")
            print(f"  stderr: {(e.stderr or '')[-500:]}")
            row = {"name": mp4.stem, "mode": "ERROR", "segments": 0, "size_mb": 0.0}
        rows.append(row)

    print("\n=== Summary ===")
    print(f"{'name':<50} {'mode':>9} {'segs':>5} {'size_MB':>8}")
    print("-" * 76)
    for r in rows:
        name = r["name"][:48]
        print(f"{name:<50} {r['mode']:>9} {r['segments']:>5} {r['size_mb']:>8.2f}")

    total = sum(r["size_mb"] for r in rows)
    by_mode: dict[str, int] = {}
    for r in rows:
        by_mode[r["mode"]] = by_mode.get(r["mode"], 0) + 1
    print("-" * 76)
    print(f"Total HLS output: {total:.2f} MB across {len(rows)} videos")
    print(f"By mode: {by_mode}")


if __name__ == "__main__":
    main()
