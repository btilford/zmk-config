#!/usr/bin/env python3
"""
Dynamic Keyboard Layer Formatter for ZMK

Automatically formats ZMK keyboard layers with dynamic spacing calculation:
- Column widths based on longest keys in each column
- ║ separator positioned dynamically
- Thumb row indentation calculated from finger rows
- Perfect vertical alignment of & symbols
"""

import re
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# Keycode to display mapping for ASCII art
KEY_DISPLAY_MAP = {
    # Standard keys
    "&kp GRAVE": "`",
    "&kp N1": "1",
    "&kp N2": "2",
    "&kp N3": "3",
    "&kp N4": "4",
    "&kp N5": "5",
    "&kp N6": "6",
    "&kp N7": "7",
    "&kp N8": "8",
    "&kp N9": "9",
    "&kp N0": "0",
    "&kp EXCL": "!",
    "&kp AT": "@",
    "&kp HASH": "#",
    "&kp DLLR": "$",
    "&kp PRCNT": "%",
    "&kp CARET": "^",
    "&kp AMPS": "&",
    "&kp KP_MULTIPLY": "*",
    "&kp LPAR": "(",
    "&kp RPAR": ")",
    "&kp MINUS": "-",
    "&kp EQUAL": "=",
    "&kp LBKT": "[",
    "&kp RBKT": "]",
    "&kp BSLH": "\\",
    "&kp LBRC": "{",
    "&kp RBRC": "}",
    "&kp PIPE": "|",
    "&kp TILDE": "~",
    "&kp QMARK": "?",
    "&kp PLUS": "+",
    "&kp UNDERSCORE": "_",
    "&kp COMMA": ",",
    "&kp DOT": ".",
    "&kp FSLH": "/",
    "&kp SEMICOLON": ";",
    "&kp SQT": "'",
    "&kp COLON": ":",
    "&kp LT": "<",
    "&kp GT": ">",
    "&kp KP_DIVIDE": "/",
    "&kp TAB": "TAB",
    "&kp SPACE": "SPC",
    "&kp RET": "ENT",
    "&kp BSPC": "BKSP",
    "&kp DEL": "DEL",
    "&kp INS": "INS",
    "&kp HOME": "HOME",
    "&kp END": "END",
    "&kp PG_UP": "PGUP",
    "&kp PG_DN": "PGDN",
    "&kp LEFT": "LEFT",
    "&kp DOWN": "DOWN",
    "&kp UP": "UP",
    "&kp RIGHT": "RIGHT",
    "&kp K_APP": "APP",
    "&kp K_CANCEL": "CANC",
    "&kp C_AC_CUT": "CUT",
    "&kp C_AC_COPY": "COPY",
    "&kp C_AC_PASTE": "PASTE",
    # Special keys and macros
    "&bootloader": "BOOT",
    "&sys_reset": "RST",
    "&out OUT_USB": "USB",
    "&out OUT_BLE": "BLE",
    "&out OUT_TOG": "TOG",
    "&bt BT_CLR_ALL": "CLR",
    "&bt BT_SEL 0": "BT0",
    "&bt BT_DISC 0": "DSC0",
    "&mmv MOVE_UP": "↑",
    "&mmv MOVE_DOWN": "↓",
    "&mmv MOVE_LEFT": "←",
    "&mmv MOVE_RIGHT": "→",
    "&msc SCRL_UP": "S↑",
    "&msc SCRL_DOWN": "S↓",
    "&mkp LCLK": "LCLK",
    "&mkp RCLK": "RCLK",
    # Modifiers and special behaviors
    "&sk LSHFT": "SHFT",
    "&sk LCTRL": "CTRL",
    "&sk LALT": "ALT",
    "&sk LGUI": "GUI",
    "&kp LGUI": "GUI",
    "&kp LALT": "ALT",
    "&kp LCTRL": "CTRL",
    "&kp LSHFT": "SHFT",
    "&kp RGUI": "GUI",
    "&kp RALT": "ALT",
    "&kp RCTRL": "CTRL",
    "&kp RSHFT": "SHFT",
    "&trans": "",
    "&none": "NONE",
    # Complex macros - compact format
    "&hml LGUI A": "🏠GUI|A",
    "&hml LCTRL S": "🏠CTL|S",
    "&hml LSHIFT D": "🏠SFT|D",
    "&hml LALT F": "🏠ALT|F",
    "&hml LALT G": "🏠ALT|G",
    "&hml LCTRL H": "🏠CTL|H",
    "&hmr RALT J": "🏠ALT|J",
    "&hmr RSHIFT K": "🏠SFT|K",
    "&hmr RCTRL L": "🏠CTL|L",
    "&hmr RGUI SEMI": "🏠GUI|;",
    "&hmr RGUI SQT": "🏠GUI|'",
    # Layer taps
    "&lt MOUSE SPACE": "MOUSE|SPC",
    "&lt TEXT J": "TEXT|J",
    "&lt NUMPD N": "NUMPD|N",
    "&lt MEDIA M": "MEDIA|M",
    "&lt SYM RET": "SYM|ENT",
    # Special behaviors
    "&magic_shift LSHFT 0": "MAGIC",
    "&smart_num NUMPD 0": "SMART#",
    "&swapper": "SWAP",
    "&leader": "LEAD",
    "&num_word NUMPD": "NUMWD",
    "&caps_word": "CAPS",
}


def parse_complex_macro(zmk_code: str) -> str:
    """Fallback parser for unmapped complex macros - keep under 8 chars"""

    # HRM patterns
    if zmk_code.startswith("&hm"):
        parts = zmk_code.split()
        if len(parts) >= 4:
            mod = parts[2][:3].upper()  # First 3 chars of modifier
            key = parts[3][:1]  # First char of tap key
            return f"🏠{mod}|{key}"

    # Unknown patterns - truncate aggressively
    clean = zmk_code.replace("&", "").replace("_", "").upper()
    return clean[:6]  # Max 6 chars for unknown keys


# The half-splitting marker inside a `bindings = < ... >` array must be a C
# comment: devicetree has no notion of ║ and dtc rejects it with
# "parse error: expected number or parenthesized expression". Only the `//`
# layout diagrams above each layer may use the box-drawing character.
CODE_SEPARATOR = "/*|*/"


class DynamicKeyboardFormatter:
    """Dynamic formatter that calculates spacing based on content"""

    def __init__(self):
        self.min_column_spacing = 1  # Minimum spaces between columns

    def format_file(
        self, filepath: Path, in_place: bool = False, dry_run: bool = False
    ) -> str:
        """Format a single .keymap file"""
        logger.info(f"Processing {filepath}")

        content = filepath.read_text(encoding="utf-8")
        formatted_content = self._format_content(content)

        if dry_run:
            print(f"=== {filepath} ===")
            print(formatted_content)
            return formatted_content

        if in_place:
            filepath.write_text(formatted_content, encoding="utf-8")
            logger.info(f"Formatted {filepath}")
        else:
            print(formatted_content)

        return formatted_content

    def _format_content(self, content: str) -> str:
        """Format the entire file content"""
        lines = content.split("\n")
        formatted_lines = []

        i = 0
        while i < len(lines):
            line = lines[i]

            # Check if this is the start of a ZMK_BASE_LAYER *invocation* — not the
            # macro's own "#define ZMK_BASE_LAYER(...)" declaration, which also
            # contains this substring but must never be reformatted.
            is_define_line = re.match(r"\s*#\s*define\s+ZMK_BASE_LAYER\b", line)
            if "ZMK_BASE_LAYER(" in line and not is_define_line:
                # Find the start of this layer block (including any preceding ASCII art).
                # Must scan formatted_lines (the output built so far), not the original
                # `lines`, since earlier reformatted layers may have a different line
                # count than their source — an index from `lines` would misalign here.
                block_start = self._find_layer_block_start(
                    formatted_lines, len(formatted_lines)
                )

                # Parse the complete layer
                layer_content, layer_end = self._extract_layer(lines, i)

                if layer_content:
                    # Format the layer with dynamic spacing
                    formatted_layer = self._format_layer_dynamic(layer_content)

                    # Remove the existing ASCII art lines (from block_start to i-1)
                    while len(formatted_lines) > block_start:
                        formatted_lines.pop()

                    # Add the new formatted layer
                    layer_lines = formatted_layer.split("\n")
                    formatted_lines.extend(layer_lines)
                    i = layer_end
                else:
                    formatted_lines.append(line)
                    i += 1
            else:
                formatted_lines.append(line)
                i += 1

        return "\n".join(formatted_lines)

    def _find_layer_block_start(self, lines: List[str], layer_start_idx: int) -> int:
        """Find the start of the layer block, including any preceding ASCII art comments"""
        # Look backward from the ZMK_BASE_LAYER line to find ASCII art comments.
        # Blank lines between stacked/stale art blocks must not stop the scan early,
        # otherwise old headers are left behind instead of being replaced.
        i = layer_start_idx - 1
        block_start = layer_start_idx
        while i >= 0:
            line = lines[i].strip()
            if not line:
                i -= 1
                continue
            is_comment = (
                line.startswith("//") or line.startswith("/*") or line.startswith(" *")
            )
            stripped_marker = re.sub(r"^(//|/\*|\*)", "", line).strip()
            is_dash_divider = bool(stripped_marker) and set(stripped_marker) <= {
                "-",
                "─",
                "═",
            }
            is_art_comment = is_comment and (
                "|" in line or "─" in line or "═" in line or is_dash_divider
            )
            if is_art_comment:
                block_start = i
                i -= 1
            else:
                break

        return block_start

    def _extract_layer(
        self, lines: List[str], start_idx: int
    ) -> Tuple[Optional[str], int]:
        """Extract a complete ZMK_BASE_LAYER definition"""
        content_lines = []
        paren_count = 0
        in_layer = False

        for i in range(start_idx, len(lines)):
            line = lines[i]
            content_lines.append(line)

            paren_count += line.count("(") - line.count(")")

            if "ZMK_BASE_LAYER(" in line:
                in_layer = True

            if in_layer and paren_count <= 0 and (";" in line or ")" in line):
                return "\n".join(content_lines), i + 1

        logger.warning(f"Could not parse layer starting at line {start_idx + 1}")
        return None, start_idx + 1

    def _format_layer_dynamic(self, layer_content: str) -> str:
        """Format a layer with dynamic spacing calculation"""
        try:
            # Extract layer name and bindings
            match = re.search(
                r"ZMK_BASE_LAYER\s*\(\s*([^,]+)\s*,(.*)\)", layer_content, re.DOTALL
            )
            if not match:
                logger.warning("Could not parse layer structure")
                return layer_content

            layer_name = match.group(1).strip()
            bindings_content = match.group(2).strip()
            bindings_content = re.sub(r"\s*\)\s*$", "", bindings_content)

            # Parse key bindings
            key_rows = self._parse_bindings(bindings_content)
            if not key_rows:
                return layer_content

            # Analyze layer content for dynamic spacing
            analysis = self._analyze_layer_content(key_rows)
            analysis["key_rows"] = key_rows  # Add key_rows to analysis for ASCII art

            # Generate ASCII art
            ascii_art = self._generate_ascii_art(analysis)

            # Format bindings with dynamic spacing
            formatted_bindings = self._format_bindings_dynamic(key_rows, analysis)

            return f"{ascii_art}\nZMK_BASE_LAYER({layer_name},\n{formatted_bindings}\n)"

        except Exception as e:
            logger.warning(f"Error formatting layer: {e}")
            return layer_content

    def _analyze_layer_content(self, key_rows: List[List[str]]) -> Dict[str, Any]:
        """Analyze layer content to determine spacing requirements"""
        finger_rows = [row for row in key_rows if not self._is_thumb_row(row)]
        thumb_row = next((row for row in key_rows if self._is_thumb_row(row)), None)

        # Calculate column max lengths across all rows
        column_max_lengths = self._calculate_column_max_lengths(key_rows)

        # Calculate dynamic column widths
        column_widths = [
            max_len + self.min_column_spacing for max_len in column_max_lengths
        ]

        # Calculate separator position
        separator_pos = self._calculate_separator_position(column_widths)

        # Calculate thumb indentation (align with column 3)
        thumb_indent = self._calculate_thumb_indentation(finger_rows, column_widths, 3)

        return {
            "finger_rows": finger_rows,
            "thumb_row": thumb_row,
            "column_max_lengths": column_max_lengths,
            "column_widths": column_widths,
            "separator_pos": separator_pos,
            "thumb_indent": thumb_indent,
        }

    def _calculate_column_max_lengths(self, key_rows: List[List[str]]) -> List[int]:
        """Calculate maximum key length in each column"""
        if not key_rows:
            return []

        max_cols = max(len(row) for row in key_rows)
        column_maxes = [0] * max_cols

        for row in key_rows:
            for col_idx, key in enumerate(row):
                if col_idx < max_cols and key:
                    column_maxes[col_idx] = max(column_maxes[col_idx], len(key))

        return column_maxes

    def _calculate_separator_position(self, column_widths: List[int]) -> int:
        """Calculate separator position based on left column widths"""
        left_width = sum(column_widths[:6])  # First 6 columns
        return 4 + left_width + 1  # "    " + left content + " "

    def _calculate_thumb_indentation(
        self,
        finger_rows: List[List[str]],
        column_widths: List[int],
        target_column: int = 3,
    ) -> int:
        """Calculate thumb indentation to align with target finger column"""
        if not finger_rows or target_column >= len(column_widths):
            return 0

        # Calculate position of target column
        indent = 4  # "    " prefix
        for i in range(target_column):
            indent += column_widths[i]

        return indent

    def _parse_bindings(self, bindings_content: str) -> List[List[str]]:
        """Parse key bindings into rows"""
        bindings = re.sub(r"/\*.*?\*/", "", bindings_content)
        bindings = re.sub(r"//.*", "", bindings)

        lines = [line.strip() for line in bindings.split("\n") if line.strip()]
        rows = []

        for line in lines:
            line = re.sub(r"/\*\|?\*/", "", line)
            line = re.sub(r",\s*(?:║|/\*\|?\*/)\s*", ",", line)

            # Each comma-separated half (left/right) is a whitespace-separated
            # run of bindings, where a binding is one "&behavior" token plus any
            # following non-"&" param tokens (e.g. "&hml LGUI A", "&bt BT_SEL 0"),
            # or a single bare macro token (e.g. "MAGIC_SHIFT").
            halves = [half.strip() for half in line.split(",") if half.strip()]
            keys = []
            for half in halves:
                keys.extend(self._split_binding_tokens(half))
            if keys:
                rows.append(keys)

        return rows

    def _split_binding_tokens(self, text: str) -> List[str]:
        """Split a run of bindings into individual '&behavior [params...]' groups"""
        tokens = text.split()
        groups: List[List[str]] = []
        for token in tokens:
            if token.startswith("&") or not groups:
                groups.append([token])
            else:
                groups[-1].append(token)
        return [" ".join(group) for group in groups]

    def _is_thumb_row(self, row: List[str]) -> bool:
        """Detect thumb rows (typically 6 or fewer keys)"""
        return len(row) <= 6

    def _generate_ascii_art(self, analysis: Dict[str, Any]) -> str:
        """Generate dynamic ASCII art diagram based on layer content"""
        key_rows = analysis.get("key_rows", [])

        if not key_rows:
            # Fallback to generic ASCII art if no key rows
            return self._get_fallback_ascii_art()

        return self._generate_dynamic_ascii_art(key_rows)

    def _get_fallback_ascii_art(self) -> str:
        """Get fallback generic ASCII art"""
        lines = [
            "// -----------------------------------------------------------------------------------------",
            "// | TAB  |  Q  |  W  |  E  |  R  |  T  | ║ |  Y  |  U   |  I  |  O  |  P  | BKSP |",
            "// | CTRL |  A  |  S  |  D  |  F  |  G  | ║ |  H  |  J   |  K  |  L  |  ;  |  '   |",
            "// | SHFT |  Z  |  X  |  C  |  V  |  B  | ║ |  N  |  M   |  ,  |  .  |  /  | ESC  |",
            "//                    | GUI | LWR | SPC | ║ | ENT | RSE  | ALT |",
            "// -----------------------------------------------------------------------------------------",
        ]
        return "\n".join(lines)

    def _generate_dynamic_ascii_art(self, key_rows: List[List[str]]) -> str:
        """Generate layer-specific ASCII art with perfect column alignment"""

        # Convert ZMK bindings to display text
        display_rows = self._convert_to_display_text(key_rows)

        # Calculate global column widths across all rows
        column_widths = self._calculate_global_column_widths(display_rows)

        # Separate finger and thumb rows
        finger_rows = [row for row in display_rows if len(row) >= 10]  # Finger rows
        thumb_row = next((row for row in display_rows if 0 < len(row) < 10), None)

        lines = []
        lines.append(
            "// -----------------------------------------------------------------------------------------"
        )

        # Format exactly 3 finger rows
        for i in range(3):
            if i < len(finger_rows):
                row = finger_rows[i]
            else:
                row = [""] * 12  # Empty row

            line = self._format_ascii_row(row, column_widths, is_thumb_row=False)
            lines.append(line)

        # Format thumb row if present
        if thumb_row:
            line = self._format_ascii_row(thumb_row, column_widths, is_thumb_row=True)
            lines.append(line)

        lines.append(
            "// -----------------------------------------------------------------------------------------"
        )

        return "\n".join(lines)

    def _convert_to_display_text(self, key_rows: List[List[str]]) -> List[List[str]]:
        """Convert ZMK key bindings to display text"""
        display_rows = []
        for row in key_rows:
            display_row = []
            for zmk_key in row:
                display_key = KEY_DISPLAY_MAP.get(zmk_key, parse_complex_macro(zmk_key))
                display_row.append(display_key)
            display_rows.append(display_row)
        return display_rows

    def _calculate_global_column_widths(
        self, display_rows: List[List[str]]
    ) -> Dict[int, int]:
        """Calculate consistent column widths across ALL rows"""

        # Collect maximum widths for each column
        column_maxes = {}
        for row in display_rows:
            for col_idx, display_key in enumerate(row):
                if col_idx < 13:  # 12 keys + 1 separator
                    key_len = len(display_key) if display_key else 0
                    column_maxes[col_idx] = max(column_maxes.get(col_idx, 0), key_len)

        # Apply consistent minimum widths
        final_widths = {}
        for col_idx in range(13):
            base_width = column_maxes.get(col_idx, 0)
            if col_idx == 6:  # ║ separator column
                final_widths[col_idx] = 1
            else:  # Key columns - minimum 6 chars for readability
                final_widths[col_idx] = max(base_width + 1, 6)

        return final_widths

    def _format_ascii_row(
        self, row: List[str], column_widths: Dict[int, int], is_thumb_row: bool = False
    ) -> str:
        """Format a row with perfect column alignment"""

        if is_thumb_row:
            # Thumb row: center the keys
            thumb_keys = row[:6]  # Support up to 6 thumb keys
            formatted_thumbs = []

            # Map thumb positions to global column indices
            thumb_positions = [7, 8, 9, 10, 11, 12]  # Thumb key positions

            for i, key in enumerate(thumb_keys):
                if i < len(thumb_positions):
                    col_idx = thumb_positions[i]
                    width = column_widths.get(col_idx, 6)
                    formatted_key = self._format_ascii_cell(key, width)
                    formatted_thumbs.append(formatted_key)

            thumb_str = " | ".join(formatted_thumbs)
            # Fixed indent for thumb alignment
            indent = " " * 21
            return f"//{indent}| {thumb_str} |"

        else:
            # Finger row: format exactly 12 key positions
            full_row = row + [""] * (12 - len(row))  # Pad to 12 keys

            # Left side (columns 0-5)
            left_cells = []
            for i in range(6):
                key = full_row[i] if i < len(full_row) else ""
                width = column_widths.get(i, 6)
                left_cells.append(self._format_ascii_cell(key, width))

            # Right side (columns 7-12)
            right_cells = []
            for i in range(6):
                col_idx = 7 + i
                key = full_row[col_idx - 1] if col_idx - 1 < len(full_row) else ""
                width = column_widths.get(col_idx, 6)
                right_cells.append(self._format_ascii_cell(key, width))

            left_str = " | ".join(left_cells)
            right_str = " | ".join(right_cells)

            return f"// | {left_str} | ║ | {right_str} |"

    def _format_ascii_cell(self, display_key: str, width: int) -> str:
        """Format a single cell with consistent left-padding"""
        if not display_key:
            return " " * width
        return f"{display_key:<{width}}"

    def _format_bindings_dynamic(
        self, key_rows: List[List[str]], analysis: Dict[str, Any]
    ) -> str:
        """Format bindings with dynamic spacing.

        The mid-row comma (before ║) and the end-of-row comma are ZMK_BASE_LAYER
        macro argument separators (name, LT, RT, LM, RM, LB, RB, LH, RH) — not
        decoration. Dropping the mid-row comma, or adding one after the last row,
        changes the macro's argument count and breaks the build.
        """
        formatted_lines = []
        column_widths = analysis["column_widths"]
        separator_pos = analysis["separator_pos"]
        thumb_indent = analysis["thumb_indent"]

        for idx, row in enumerate(key_rows):
            is_last_row = idx == len(key_rows) - 1
            if self._is_thumb_row(row):
                formatted = self._format_thumb_row_dynamic(
                    row, column_widths, thumb_indent, separator_pos, is_last_row
                )
            else:
                formatted = self._format_finger_row_dynamic(
                    row, column_widths, separator_pos, is_last_row
                )

            formatted_lines.append(formatted)

        return "\n".join(formatted_lines)

    def _format_finger_row_dynamic(
        self,
        keys: List[str],
        column_widths: List[int],
        separator_pos: int,
        is_last_row: bool,
    ) -> str:
        """Format finger row with dynamic spacing, separator pinned to separator_pos"""
        # Ensure 12 keys
        full_keys = (keys + [""] * 12)[:12]

        # Format each key with calculated column width
        formatted_parts = []
        for col_idx, key in enumerate(full_keys):
            width = column_widths[col_idx] if col_idx < len(column_widths) else 8
            if key:
                formatted_parts.append(f"{key:<{width}}")
            else:
                formatted_parts.append(" " * width)

        left_core = "".join(formatted_parts[:6]).rstrip()
        left_side = ("    " + left_core + ",").ljust(separator_pos)
        right_side = "".join(formatted_parts[6:]).rstrip()
        trailing_comma = "" if is_last_row else ","

        return f"{left_side}{CODE_SEPARATOR} {right_side}{trailing_comma}"

    def _format_thumb_row_dynamic(
        self,
        keys: List[str],
        column_widths: List[int],
        indent: int,
        separator_pos: int,
        is_last_row: bool,
    ) -> str:
        """Format thumb row with dynamic indentation, separator pinned to separator_pos"""
        # Ensure 6 thumb keys
        full_keys = (keys + [""] * 6)[:6]

        # Format thumb keys
        formatted_thumbs = []
        for i, key in enumerate(full_keys):
            width = column_widths[min(i, len(column_widths) - 1)]
            if key:
                formatted_thumbs.append(f"{key:<{width}}")
            else:
                formatted_thumbs.append(" " * width)

        indent_spaces = " " * indent
        left_core = "".join(formatted_thumbs[:3]).rstrip()
        left_thumbs = (indent_spaces + left_core + ",").ljust(separator_pos)
        right_thumbs = "".join(formatted_thumbs[3:]).rstrip()
        trailing_comma = "" if is_last_row else ","

        return f"{left_thumbs}{CODE_SEPARATOR} {right_thumbs}{trailing_comma}"


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Dynamically format ZMK keyboard layers"
    )
    parser.add_argument(
        "files", nargs="+", help="Keymap files or directories to format"
    )
    parser.add_argument(
        "--in-place", "-i", action="store_true", help="Modify files in place"
    )
    parser.add_argument(
        "--dry-run",
        "-d",
        action="store_true",
        help="Show changes without modifying files",
    )
    parser.add_argument(
        "--quiet", "-q", action="store_true", help="Suppress non-error output"
    )

    args = parser.parse_args()

    if args.quiet:
        logger.setLevel(logging.WARNING)

    formatter = DynamicKeyboardFormatter()

    for file_path in args.files:
        path = Path(file_path)

        if path.is_dir():
            keymap_files = list(path.glob("**/*.keymap"))
            for keymap_file in keymap_files:
                formatter.format_file(keymap_file, args.in_place, args.dry_run)

        elif path.is_file() and path.suffix == ".keymap":
            formatter.format_file(path, args.in_place, args.dry_run)

        else:
            logger.error(f"Invalid path: {path}")


if __name__ == "__main__":
    main()
