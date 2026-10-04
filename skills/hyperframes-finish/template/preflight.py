#!/usr/bin/env python3
"""Can the HyperFrames finish run in this session? A quick check before starting.

  python3 preflight.py [--video URL]

The finish needs Node, Python and ffmpeg, and it downloads the render (from
HeyGen), GSAP, the fonts and the HyperFrames renderer (from npm), and a headless
Chrome (from Google). Claude Code can do all of that. A Cowork session usually
can't: its sandbox has no ffmpeg, or blocks those downloads.

Prints one line per check and, last, READY or HAND OFF. Exits 0 when ready.
Pass --video with the render's video_url to check that HeyGen's file host is
reachable too. Nothing is installed or changed.
"""
import argparse, shutil, subprocess, sys, urllib.request

def ok_cmd(cmd):
    exe = shutil.which(cmd[0])
    if not exe:
        return False, "not installed"
    try:
        # The full path, so Windows can run npx.cmd too.
        out = subprocess.run([exe, *cmd[1:]], capture_output=True, text=True, timeout=20)
        line = (out.stdout or out.stderr).strip().splitlines()
        return out.returncode == 0, line[0][:60] if line else ""
    except Exception as e:
        return False, str(e)[:60]

def ok_url(url, listing=False):
    """Reachable means the real server answered. A sandbox that blocks the host answers
    with its own error instead. For a bucket listing (listing=True), Google's own
    "access denied" reply still proves the host is reachable."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "preflight", "Range": "bytes=0-0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status < 400, f"HTTP {r.status}"
    except urllib.error.HTTPError as e:
        body = e.read(400).decode("utf-8", "replace")
        if listing and e.code == 403 and "<Error>" in body:
            return True, "reachable"
        return False, f"HTTP {e.code}"
    except Exception as e:
        return False, str(getattr(e, "reason", e))[:60]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", help="the render's video_url, to check HeyGen's file host")
    a = ap.parse_args()
    checks = [
        ("Node", ok_cmd(["node", "-v"])),
        ("npx", ok_cmd(["npx", "--version"])),
        ("Python", ok_cmd([sys.executable, "-V"])),
        ("ffmpeg", ok_cmd(["ffmpeg", "-version"])),
        ("ffprobe", ok_cmd(["ffprobe", "-version"])),
        ("npm (GSAP, fonts, renderer)", ok_url("https://registry.npmjs.org/gsap")),
        ("Chrome download", ok_url("https://storage.googleapis.com/chrome-for-testing-public/", listing=True)),
    ]
    if a.video:
        checks.append(("HeyGen file host", ok_url(a.video)))
    for name, (good, note) in checks:
        print(f"{'ok  ' if good else 'FAIL'}  {name}{': ' + note if note else ''}")
    ready = all(good for _, (good, _) in checks)
    print("READY" if ready else "HAND OFF: run the finish in Claude Code (see the hyperframes-finish skill)")
    sys.exit(0 if ready else 1)

if __name__ == "__main__":
    main()
