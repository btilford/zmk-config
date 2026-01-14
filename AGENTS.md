# AGENTS.md - Development Guidelines for ZMK Keyboard Configuration

This document provides comprehensive guidelines for software engineering agents working on this ZMK (Zephyr Mechanical Keyboard) firmware configuration repository.

## Table of Contents
1. [Build/Lint/Test Commands](#buildlinttest-commands)
2. [Code Style Guidelines](#code-style-guidelines)
3. [Development Workflow](#development-workflow)
4. [Project Structure](#project-structure)
5. [Testing](#testing)
6. [Continuous Integration](#continuous-integration)

## Build/Lint/Test Commands

### Building Firmware
```bash
# Build all targets matching a pattern
just build <pattern>

# Common build commands:
just build all                    # Build all targets
just build corne                  # Build Corne keyboard variants
just build crosses                # Build Crosses keyboard variants
just build settings-reset         # Build settings reset firmware

# Build specific target
just build corne-42-left
just build crosses-42-right

# Clean build artifacts
just clean                        # Remove build and firmware directories
just clean-all                    # Remove all generated files (west, zmk, etc.)

# Initialize west workspace (first-time setup)
just init

# Update west modules
just update
```

### Testing
```bash
# Run tests for a specific configuration
just test <test-directory> [FLAGS]

# Test flags:
--no-build        # Skip building, use existing binary
--verbose         # Show full test output
--auto-accept     # Accept test results as new snapshot

# Example:
just test config/tests/corne-tap-dance
```

### Keymap Visualization
```bash
# Parse and visualize keymap
just draw

# This generates keymap-drawer/base.svg from the base.keymap configuration
```

### Other Commands
```bash
# List all available build targets
just list

# Upgrade Zephyr SDK and dependencies
just upgrade-sdk

# Clear Nix cache (if using Nix)
just clean-nix
```

## Code Style Guidelines

### File Organization
- **`config/`**: Core configuration files
  - `*.keymap`: Main keymap definitions
  - `*.conf`: Kconfig configuration overrides
  - `*.dtsi`: Device Tree Source includes (combos, leader keys, mouse, etc.)
- **`keymap-drawer/`**: Visualization configuration and output
- **`build.yaml`**: CI build matrix definition
- **`Justfile`**: Task runner definitions

### Device Tree Source (DTS) Style

#### Includes and Preprocessing
```c
// Group includes by type, standard ZMK includes first
#include <behaviors.dtsi>
#include <behaviors/num_word.dtsi>
#include <dt-bindings/zmk/keys.h>

// Local includes
#include "combos.dtsi"
#include "leader.dtsi"
```

#### Conditional Compilation
```c
#ifdef CONFIG_WIRELESS
  #include <dt-bindings/zmk/bt.h>
  // Wireless-specific code
#else
  // USB-only fallbacks
#endif
```

#### Macro Definitions
```c
// Use ALL_CAPS for constants
#define BASE 0
#define SYM 1
#define TAPPING_TERM_MS 200
#define QUICK_TAP_MS 193

// Use descriptive macro names with MAKE_ prefix for complex macros
#define MAKE_HRM(NAME, HOLD, TAP, TRIGGER_POS) \
  ZMK_HOLD_TAP(NAME, bindings = <HOLD>, <TAP>; \
               flavor = "balanced"; \
               tapping-term-ms = <TAPPING_TERM_MS>; \
               quick-tap-ms = <QUICK_TAP_MS>; \
               require-prior-idle-ms = <150>; \
               hold-trigger-on-release;)
```

#### Behavior Definitions
```c
// ZMK behavior definitions - one per line, aligned parameters
ZMK_HOLD_TAP(magic_shift,
    bindings = <&kp>, <&magic_shift_tap>;
    flavor = "balanced";
    tapping-term-ms = <200>;
    quick-tap-ms = <QUICK_TAP_MS>;)

ZMK_MOD_MORPH(magic_shift_tap,
    bindings = <&shift_repeat>, <&caps_word>;
    mods = <(MOD_LSFT)>;)
```

#### Keymap Layout
```c
// Use consistent spacing and alignment
// Comment headers showing physical layout
/* vim: set ft=c tw=146: */

// -------------------------------------------------------------------------
// | TAB  |  Q  |  W  |  E  |  R  |  T  |   |  Y  |  U   |  I  |  O  |  P  | BKSP |
// | CTRL |  A  |  S  |  D  |  F  |  G  |   |  H  |  J   |  K  |  L  |  ;  |  '   |
// | SHFT |  Z  |  X  |  C  |  V  |  B  |   |  N  |  M   |  ,  |  .  |  /  | ESC  |
//                     | GUI | LWR | SPC |   | ENT | RSE  | ALT |

ZMK_BASE_LAYER(Base,
    &kp TAB    &kp Q       &kp W        &kp E          &kp R          &kp T,            /*|*/    &kp Y         &kp U         &kp I        &kp O          &kp P          &lt BTOOTH BSPC,
    &gresc     &hml LGUI A  &hml LCTRL S  &hml LSHIFT D   &lt MOTION F   &hml LALT G,       /*|*/    &hmr RALT H    &lt TEXT J &hmr RSHIFT K  &hmr RCTRL L    &hmr RGUI SEMI  &kp SQT,
    MAGIC_SHIFT &kp Z      &kp X        &kp C          &kp V          &kp B,            /*|*/    &lt NUMPD N    &lt MEDIA M &kp COMMA     &kp DOT      &kp FSLH       &mt RSHFT RPAR,
                                     SMART_NUM    &lt MOUSE SPACE &ldr,          /*|*/      &mo TEXT &lt SYM RET  &kp RALT
)
```

### Naming Conventions

#### Layers
```c
#define BASE 0
#define SYM 1
#define NUMPD 2
#define MOTION 3
#define TEXT 4
#define MEDIA 5
#define DM 6          // Desktop Management
#define FKEYS 7       // Function Keys
#define MOUSE 8
#define BTOOTH 9      // Bluetooth
```

#### Behaviors
- Use `hm` prefix for home row mods: `hml`, `hmr`
- Use `mt` prefix for mod-taps: `mt_home`, `mt_end`
- Use `smart_` prefix for intelligent behaviors: `smart_mouse`, `smart_num`
- Use `magic_` prefix for context-aware behaviors: `magic_shift`

#### Constants
- `*_TERM_MS`: Timing constants (tapping term, combo term)
- `*_MS`: General timing values
- `COMBO_*`: Combo-related constants

### Combo Definitions
```c
// Clear combo matrix visualization at top of file
/*
                                      42 KEY MATRIX / LAYOUT MAPPING
   ╭────────────────────────┬────────────────────────╮ ╭─────────────────────────┬─────────────────────────╮
   │  0   1   2   3   4   5 │  6   7   8   9  10  11 │ │ LT5 LT4 LT3 LT2 LT1 LT0 │ RT0 RT1 RT2 RT3 RT4 RT5 │
   │ 12  13  14  15  16  17 │ 18  19  20  21  22  23 │ │ LM5 LM4 LM3 LM2 LM1 LM0 │ RM0 RM1 RM2 RM3 RM4 RM5 │
   │ 24  25  26  27  28  29 │ 30  31  32  33  34  35 │ │ LB5 LB4 LB3 LB2 LB1 LB0 │ RB0 RB1 RB2 RB3 RB4 RB5 │
   ╰───────────╮ 36  37  38 │ 39  40  41 ╭───────────╯ ╰───────────╮ LH2 LH1 LH0 │ RH0 RH1 RH2 ╭───────────╯
               ╰────────────┴────────────╯                         ╰─────────────┴─────────────╯             */

// Use descriptive combo names
ZMK_COMBO(capsword, &caps_word, LM2 RM2, BASE, COMBO_TERM_SLOW, COMBO_IDLE_SLOW)
ZMK_COMBO(smart_mouse, &smart_mouse, LM1 RM1, BASE, COMBO_TERM_FAST, COMBO_IDLE_FAST)
```

### YAML Configuration (keymap-drawer)
```yaml
# Use consistent indentation (2 spaces)
# Group related settings
draw_config:
  append_colon_to_layer_header: false
  draw_key_sides: true

  svg_extra_style: |
    # CSS styling for visualization

parse_config:
  preprocess: true
  skip_binding_parsing: false

  # Raw binding mappings for custom behaviors
  raw_binding_map:
    "&none":
      tap: $$mdi:minus-circle-outline$$
      type: none

  # Keycode mappings - use full names, add abbreviations as aliases
  zmk_keycode_map:
    EXCLAMATION: '!'
    EXCL: '!'          # Alias
    AT_SIGN: '@'
    AT: '@'            # Alias
```

### Comments and Documentation

#### File Headers
```c
/*                                      42 KEY MATRIX / LAYOUT MAPPING
...
*/
```

#### Behavior Documentation
```c
// Tap: repeat after alpha, else sticky-shift |
// Shift + tap/ double-tap: caps-word | Hold: shift.
#define MAGIC_SHIFT &magic_shift LSHFT 0
```

#### TODO Comments
```c
// TODO: implement snipe layers for trackball driver
// TODO: rebase caps_word PR #1451
```

### Error Handling
- ZMK handles most errors at compile-time through DTS validation
- Use conditional compilation for optional features
- Test configurations thoroughly before committing

## Development Workflow

### 1. Setup
```bash
# Clone and initialize
git clone <repository>
cd <repository>
just init
just update
```

### 2. Development Cycle
```bash
# Make changes to config files
# Test changes
just test <relevant-test>

# Build and verify
just build <target>

# Visualize changes
just draw

# Commit when ready
git add .
git commit -m "feat: <description>"
```

### 3. Testing Strategy
- Write tests for new behaviors in `config/tests/`
- Use snapshot testing for keycode sequences
- Test on actual hardware when possible
- Verify combo timing and behavior interactions

## Project Structure

```
├── config/                    # Core configuration
│   ├── *.keymap              # Main keymap definitions
│   ├── *.conf                # Kconfig overrides
│   ├── *.dtsi                # Device Tree includes
│   └── tests/                # Test configurations
├── keymap-drawer/            # Visualization
│   ├── *.yaml               # Draw configurations
│   └── *.svg                # Generated diagrams
├── build.yaml               # CI build matrix
├── Justfile                 # Task definitions
├── requirements.txt         # Python dependencies
└── .github/workflows/       # CI/CD pipelines
```

## Testing

### Test Structure
Tests are located in `config/tests/` and consist of:
- `<test-name>.keymap`: Test keymap configuration
- `<test-name>.dtsi`: Supporting behaviors (optional)
- `events.patterns`: Regex patterns for expected key events
- `keycode_events.snapshot`: Expected test output

### Running Tests
```bash
# Run specific test
just test config/tests/corne-tap-dance

# Run test without rebuilding
just test config/tests/corne-tap-dance --no-build

# Accept new test results
just test config/tests/corne-tap-dance --auto-accept
```

### Writing Tests
1. Create test configuration files
2. Define expected key event patterns
3. Run test to generate initial snapshot
4. Verify behavior matches expectations

## Continuous Integration

### GitHub Actions
- Uses ZMK's standard build workflow
- Builds all targets defined in `build.yaml`
- Triggers on push, pull requests, and manual dispatch

### Build Matrix
Defined in `build.yaml` with format:
```yaml
include:
  - board: nice_nano_v2
    shield: corne_left nice_view_adapter nice_view
    artifact-name: corne-42-left
```

### Pre-commit Checks
- Build verification for all targets
- No linting (ZMK handles validation through DTS compilation)
- Artifact generation and upload

## Best Practices

### Code Organization
- Keep related behaviors together
- Use consistent macro naming patterns
- Document complex behaviors with comments
- Group similar keycodes and behaviors

### Performance Considerations
- Minimize combo timeout values for responsiveness
- Use appropriate tapping terms for different use cases
- Balance between feature complexity and maintainability

### Maintainability
- Use descriptive names for custom behaviors
- Document behavior interactions and edge cases
- Keep keymap layout comments synchronized with actual layout
- Test behavior combinations thoroughly

### Version Control
- Commit logical units of functionality
- Use conventional commit messages
- Test builds before pushing
- Keep visualization files up to date

## Tooling

### Required Tools
- `west`: Zephyr build system
- `just`: Task runner
- Python 3.x with dependencies from `requirements.txt`
- Zephyr SDK (managed by `west`)

### Optional Tools
- `keymap-drawer`: Keymap visualization
- VS Code with DTS language support
- ZMK Studio for testing (when available)

---

*This document should be updated when new patterns or conventions are established. Last updated: $(date)*