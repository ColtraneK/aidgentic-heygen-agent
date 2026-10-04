#!/usr/bin/env python3
"""Write the plain graphics plate: a 1080x1920 PNG in one colour, with no ffmpeg needed.

  python3 plate.py "#101418" plate.png [--size 1080x1920]
"""
import argparse, struct, zlib

def png(path, w, h, rgb):
    row = b"\x00" + bytes(rgb) * w
    raw = zlib.compress(row * h, 9)
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
                + chunk(b"IDAT", raw) + chunk(b"IEND", b""))

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("colour")
    ap.add_argument("out")
    ap.add_argument("--size", default="1080x1920")
    a = ap.parse_args()
    hx = a.colour.lstrip("#")
    w, h = map(int, a.size.split("x"))
    png(a.out, w, h, [int(hx[i:i + 2], 16) for i in (0, 2, 4)])
    print(f"wrote {a.out}: {w}x{h} #{hx}")
