# TrackMe PWA Icon Generator
# Generates 192x192 and 512x512 PNG icons using pure Python (no dependencies)
# Run: python generate_icons.py

import struct
import zlib
import os


def create_png(width, height, filepath):
    """Create a simple PNG icon: indigo circle with white T"""

    def make_pixel(x, y):
        """Return (R, G, B, A) for pixel at (x, y)"""
        cx, cy = width // 2, height // 2
        radius = width * 0.38

        # Distance from center
        dx, dy = x - cx, y - cy
        dist = (dx * dx + dy * dy) ** 0.5

        # Background (transparent)
        if dist > radius + 2:
            return (0x0F, 0x17, 0x2A, 255)  # dark bg
        elif dist > radius:
            return (0x63, 0x66, 0xF1, 255)  # indigo ring (anti-alias)
        else:
            # Inside circle — check if pixel is on the "T" letter
            bar_top = height * 0.28
            bar_bottom = height * 0.42
            stem_top = height * 0.38
            stem_bottom = height * 0.62
            stem_left = width * 0.42
            stem_right = width * 0.58
            bar_left = width * 0.30
            bar_right = width * 0.70

            # Horizontal bar of T
            if bar_top <= y <= bar_bottom and bar_left <= x <= bar_right:
                return (255, 255, 255, 255)
            # Vertical stem of T
            if stem_top <= y <= stem_bottom and stem_left <= x <= stem_right:
                return (255, 255, 255, 255)

            # Circle fill
            return (0x63, 0x66, 0xF1, 255)

    # ── Build raw pixel data ──
    raw_data = b""
    for y in range(height):
        raw_data += b"\x00"  # filter byte for each row
        for x in range(width):
            r, g, b, a = make_pixel(x, y)
            raw_data += struct.pack("BBBB", r, g, b, a)

    # ── PNG encoding ──
    def make_chunk(chunk_type, data):
        chunk = chunk_type + data
        crc = struct.pack(">I", zlib.crc32(chunk) & 0xFFFFFFFF)
        return struct.pack(">I", len(data)) + chunk + crc

    # PNG signature
    png = b"\x89PNG\r\n\x1a\n"

    # IHDR chunk
    ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    png += make_chunk(b"IHDR", ihdr_data)

    # IDAT chunk (compressed image data)
    compressed = zlib.compress(raw_data)
    png += make_chunk(b"IDAT", compressed)

    # IEND chunk
    png += make_chunk(b"IEND", b"")

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "wb") as f:
        f.write(png)
    print(f"  [OK] Created {filepath} ({os.path.getsize(filepath):,} bytes)")


if __name__ == "__main__":
    public_dir = os.path.join(os.path.dirname(__file__), "..", "frontend", "public")
    os.makedirs(public_dir, exist_ok=True)

    print("Generating PWA icons...")
    create_png(192, 192, os.path.join(public_dir, "icon-192.png"))
    create_png(512, 512, os.path.join(public_dir, "icon-512.png"))
    print("Done! Icons ready in frontend/public/")
