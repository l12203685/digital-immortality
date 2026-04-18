#!/usr/bin/env python3
"""
generate_icons.py — Convert icon.svg to PNG at required sizes for Chrome extension.

Requirements:
  pip install cairosvg   (preferred, pure Python)
  OR: pip install Pillow + cairosvg
  OR if neither: uses Inkscape CLI if available.

Run from the icons/ directory:
  python generate_icons.py
"""
from __future__ import annotations
import subprocess
import sys
from pathlib import Path

SIZES = [16, 32, 48, 128]
SVG   = Path(__file__).parent / "icon.svg"


def try_cairosvg():
    try:
        import cairosvg  # noqa: F401
        return True
    except ImportError:
        return False


def try_inkscape():
    try:
        r = subprocess.run(["inkscape", "--version"], capture_output=True, timeout=5)
        return r.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def generate_with_cairosvg():
    import cairosvg
    for sz in SIZES:
        out = SVG.parent / f"icon{sz}.png"
        cairosvg.svg2png(url=str(SVG), write_to=str(out), output_width=sz, output_height=sz)
        print(f"  generated {out.name}")


def generate_with_inkscape():
    for sz in SIZES:
        out = SVG.parent / f"icon{sz}.png"
        subprocess.run([
            "inkscape", str(SVG),
            "--export-type=png",
            f"--export-filename={out}",
            f"--export-width={sz}",
            f"--export-height={sz}",
        ], check=True, capture_output=True)
        print(f"  generated {out.name}")


def generate_fallback_with_pillow():
    """
    Pillow can't render SVG. This creates a simple colored square as a
    placeholder so the extension loads without errors while you install
    a proper SVG renderer.
    """
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print("ERROR: neither cairosvg nor Pillow is installed.")
        print("Install with: pip install cairosvg")
        sys.exit(1)

    for sz in SIZES:
        img = Image.new("RGBA", (sz, sz), (13, 17, 23, 255))
        d   = ImageDraw.Draw(img)
        # Draw a simple green tree shape as placeholder
        pad = sz // 8
        mid = sz // 2
        # Trunk
        trunk_w = max(2, sz // 12)
        d.rectangle([mid - trunk_w, sz - pad - sz//4, mid + trunk_w, sz - pad], fill=(63, 185, 80, 255))
        # Triangle (tree body) — approximate with a polygon
        pts = [(mid, pad), (pad, sz - pad - sz//4), (sz - pad, sz - pad - sz//4)]
        d.polygon(pts, outline=(63, 185, 80, 255))
        out = SVG.parent / f"icon{sz}.png"
        img.save(out, "PNG")
        print(f"  generated placeholder {out.name}")


def main():
    if not SVG.exists():
        print(f"ERROR: {SVG} not found")
        sys.exit(1)

    print("Generating Chrome extension icons...")

    if try_cairosvg():
        print("Using cairosvg")
        generate_with_cairosvg()
    elif try_inkscape():
        print("Using Inkscape CLI")
        generate_with_inkscape()
    else:
        print("WARNING: cairosvg/Inkscape not found — generating Pillow placeholders")
        generate_fallback_with_pillow()

    print("Done. Icons in:", SVG.parent)


if __name__ == "__main__":
    main()
