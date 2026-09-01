#!/usr/bin/env python3
"""Post-process a keymap-drawer SVG and refuse to emit a broken one.

Two defects that keymap-drawer produces silently -- the draw command reports
success either way, and both files look perfect in a browser, which is how they
reached the repo unnoticed.

1. Glyph refs use a colon fragment. keymap-drawer embeds each glyph with BOTH
   id="mdi:arrow-up" and id="mdi-arrow-up" but points every use at the colon
   form. librsvg does not resolve a colon in a URL fragment, so every glyph key
   renders BLANK in thumbnailers, ImageMagick, GTK previews and pandoc. Browsers
   do resolve it. Retarget the refs at the hyphen ids, which both parsers handle.

2. Well-formedness. svg_extra_style is written verbatim into a style element
   with no CDATA wrapper, so a bare left-angle-bracket anywhere in it -- a CSS
   comment included -- is parsed as an opening tag and the file stops being
   valid XML. Nothing outside a browser can then open it.

Validation is fatal: a malformed SVG fails the build rather than being
committed. Kept in sync with the reference implementation at
~/dotfiles/kmonad/.config/kmonad/tools/kmonad-draw.py
"""
import sys
import xml.etree.ElementTree as ET


def process(path: str) -> int:
    with open(path, encoding="utf-8") as fh:
        svg = fh.read()

    n = svg.count('href="#mdi:')
    if n:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(svg.replace('href="#mdi:', 'href="#mdi-'))

    try:
        ET.parse(path)
    except ET.ParseError as exc:
        print(f"FAIL {path}: not well-formed XML -- {exc}", file=sys.stderr)
        print("     A bare left-angle-bracket in svg_extra_style or svg_style_dark",
              file=sys.stderr)
        print("     is the usual cause; keymap-drawer emits that block with no CDATA.",
              file=sys.stderr)
        return 1

    print(f"ok   {path} (retargeted {n} glyph refs, valid XML)")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: svg-postprocess.py FILE.svg [FILE.svg ...]", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(max(process(p) for p in sys.argv[1:]))
