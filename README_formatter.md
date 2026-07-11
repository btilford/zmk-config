# Keyboard Layer Formatter

A Python script to automatically format ZMK keyboard layers with proper alignment, ASCII art diagrams, and clean code structure.

## Features

- **Column Alignment**: Option A compact alignment where each key starts at the same position within its column
- **ASCII Art Generation**: Automatically generates visual keyboard layout diagrams
- **Side Separators**: Uses `║` to separate left and right keyboard halves
- **Macro Preservation**: Never modifies ZMK behavior syntax (`&hml LGUI A`, etc.)
- **Git Integration**: Pre-commit hook for automatic formatting

## Installation

```bash
# Clone or download the keyboard_formatter.py script
# Make it executable
chmod +x keyboard_formatter.py
```

## Usage

### Format a single file
```bash
python keyboard_formatter.py config/corne.keymap
```

### Format all .keymap files in a directory
```bash
python keyboard_formatter.py config/
```

### In-place formatting (modifies files)
```bash
python keyboard_formatter.py config/corne.keymap --in-place
```

### Dry run (show changes without modifying)
```bash
python keyboard_formatter.py config/corne.keymap --dry-run
```

## Git Hook Setup

### Automatic Setup
```bash
python keyboard_formatter.py --install-hooks
```

### Manual Setup
```bash
# Create pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
set -e

# Get only staged .keymap files that have changes
STAGED_KEYMAPS=$(git diff --cached --name-only --diff-filter=ACM | grep '\.keymap$' || true)

if [ -n "$STAGED_KEYMAPS" ]; then
    echo "Formatting staged keymap files..."
    
    for keymap_file in $STAGED_KEYMAPS; do
        if [ -f "$keymap_file" ]; then
            echo "Formatting $keymap_file..."
            python keyboard_formatter.py "$keymap_file" --in-place --quiet
            
            # Re-stage the formatted file
            git add "$keymap_file"
        fi
    done
fi
EOF

chmod +x .git/hooks/pre-commit
```

## Example Output

**Before:**
```c
ZMK_BASE_LAYER(Base,
&kp TAB    &kp Q       &kp W        &kp E          &kp R          &kp T,            /*|*/    &kp Y         &kp U         &kp I        &kp O          &kp P          &lt BTOOTH BSPC,
&kp LCTRL  &kp A       &kp S        &kp D          &kp F          &kp G,            /*|*/    &kp H         &kp J         &kp K        &kp L          &kp SEMI       &kp SQT,
&kp LSHFT  &kp Z       &kp X        &kp C          &kp V          &kp B,            /*|*/    &kp N         &kp M         &kp COMMA    &kp DOT        &kp FSLH       &kp ESC,
                                     &kp LGUI    &mo 1     &kp SPACE,          /*|*/      &kp RET     &mo 2     &kp RALT
)
```

**After:**
```c
// -----------------------------------------------------------------------------------------
// | TAB  |  Q  |  W  |  E  |  R  |  T  | ║ |  Y  |  U   |  I  |  O  |  P  | BKSP |
// | CTRL |  A  |  S  |  D  |  F  |  G  | ║ |  H  |  J   |  K  |  L  |  ;  |  '   |
// | SHFT |  Z  |  X  |  C  |  V  |  B  | ║ |  N  |  M   |  ,  |  .  |  /  | ESC  |
//                    | GUI | LWR | SPC | ║ | ENT | RSE  | ALT |

ZMK_BASE_LAYER(Base,
    &kp TAB &kp Q &kp W &kp E &kp R &kp T ║ &kp Y &kp U &kp I &kp O &kp P &lt BTOOTH BSPC,
    &kp LCTRL &kp A &kp S &kp D &kp F &kp G ║ &kp H &kp J &kp K &kp L &kp SEMI &kp SQT,
    &kp LSHFT &kp Z &kp X &kp C &kp V &kp B ║ &kp N &kp M &kp COMMA &kp DOT &kp FSLH &kp ESC,
    &kp LGUI &mo 1 &kp SPACE ║ &kp RET &mo 2 &kp RALT
)
```

## Requirements

- Python 3.6+
- ZMK keyboard configuration files

## License

MIT License - feel free to use and modify for your keyboard projects!