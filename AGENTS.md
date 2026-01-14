# AGENTS.md - Development Guidelines for ZMK Keyboard Configuration

This document provides comprehensive guidelines for software engineering agents working on this ZMK (Zephyr Mechanical Keyboard) firmware configuration repository.

## Table of Contents
1. [Build/Lint/Test Commands](#buildlinttest-commands)
2. [Code Style Guidelines](#code-style-guidelines)
3. [Development Workflow](#development-workflow)
4. [Project Structure](#project-structure)
5. [Testing](#testing)
6. [Continuous Integration](#continuous-integration)
7. [Advanced Features](#advanced-features)
8. [GitHub Actions Customization](#github-actions-customization)
9. [Troubleshooting](#troubleshooting)

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
just clean-generated              # Remove generated keymaps and diagrams

# Initialize west workspace (first-time setup)
just init

# Update west modules
just update
```

### Keymap-Drawer Commands
```bash
# Generate keymap diagrams
just test-layouts                 # Validate keymap parsing compatibility
just draw-corne                   # Generate corne keyboard diagram
just draw-crosses                 # Generate crosses keyboard diagram
just draw                         # Generate both diagrams with error handling
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

## Essential Requirements

### Bluetooth Configuration
**Bluetooth must remain enabled for keyboard functionality.** These keyboards are designed as wireless devices and require Bluetooth connectivity to function properly.

**⚠️ IMPORTANT: Do not disable `CONFIG_BT`** - This will render the keyboards inoperable as they cannot connect to devices without wireless capability.

**Current Configuration:**
```conf
# Bluetooth is required for keyboard functionality - do not disable
# Note: If build fails due to PSA crypto issues, ensure Zephyr SDK version is compatible with ZMK version
CONFIG_BT_ECC=n
CONFIG_BT_CRYPTO=n
```

**SDK Compatibility Notes:**
- **ZMK v0.3.0** requires **Zephyr SDK v0.16.x** for proper Bluetooth crypto support
- **ZMK main branch** requires **Zephyr SDK v0.17.0+** for Zephyr 4.1 compatibility
- If encountering PSA crypto header errors (`psa/crypto.h` not found), verify SDK version matches ZMK version requirements

**Dependencies:**
- Zephyr SDK must include Bluetooth stack components
- Ensure `west` workspace is properly initialized with Bluetooth-enabled modules
- Check `west.yml` for correct ZMK and Zephyr version coordination

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

### Version Compatibility
- **ZMK v0.3.0** uses **Zephyr v3.5.0+zmk-fixes**
- **ZMK main** uses **Zephyr v4.1** (latest features)
- **PMW3610 Driver:** Match branch to Zephyr version
  - `main` branch → Zephyr 3.5
  - `zephyr-4.1` branch → Zephyr 4.1

**Bluetooth Requirements:**
- **Bluetooth must remain enabled** (`CONFIG_BT=y`) for keyboard functionality
- Do not disable `CONFIG_BT_ECC` or `CONFIG_BT_CRYPTO` unless compatibility issues arise
- Use appropriate Zephyr SDK version to avoid PSA crypto header issues

**When to Upgrade:**
- Need latest ZMK features → Use main branch
- Hardware requires Zephyr 4.1 → Use main branch
- Stable production → Stick with v0.3.0

**Upgrade Process:**
1. Update `west.yml` ZMK revision to `main`
2. Run `west update --fetch-opt=--filter=blob:none`
3. **Install Zephyr SDK v0.17.0** (remove v0.16.5 if present)
4. Update PMW3610 driver to `zephyr-4.1` branch if using trackball
5. Re-enable Bluetooth crypto if previously disabled (`CONFIG_BT_ECC=y`, `CONFIG_BT_CRYPTO=y`)
6. Test builds with new versions
7. Validate all hardware compatibility

**Rollback Process:**
- Change ZMK revision back to `v0.3.0` in `west.yml`
- Run `west update` to revert dependencies
- **Install Zephyr SDK v0.16.5** (remove v0.17.0 if present)
- Update PMW3610 driver back to `main` branch if using trackball
- Ensure Bluetooth crypto is enabled (`CONFIG_BT_ECC=y`, `CONFIG_BT_CRYPTO=y`)
- Test builds to ensure stability

### Version Control
- Commit logical units of functionality
- Use conventional commit messages
- Test builds before pushing
- Keep visualization files up to date

## Tooling

### Required Tools
- **Python Virtual Environment** (recommended for dependency isolation):
  ```bash
  python -m venv zmk-env
  source zmk-env/bin/activate  # Linux/macOS
  # zmk-env\Scripts\activate   # Windows
  pip install west keymap-drawer pyelftools
  ```
- `west`: Zephyr build system (install via pip in venv)
- `just`: Task runner (system package: `sudo pacman -S just` on Arch)
- Python 3.10+ with required packages (west, keymap-drawer, pyelftools)
- **Zephyr SDK** (version depends on ZMK branch):
  ```bash
  # For ZMK v0.3.0 (Zephyr 3.5.0+zmk-fixes) - CURRENT RECOMMENDATION:
  wget https://github.com/zephyrproject-rtos/sdk-ng/releases/download/v0.16.5/zephyr-sdk-0.16.5_linux-x86_64.tar.xz
  tar xf zephyr-sdk-0.16.5_linux-x86_64.tar.xz
  cd zephyr-sdk-0.16.5 && ./setup.sh
  # Environment setup (v0.16.5 doesn't have zephyr-env.sh):
  export ZEPHYR_SDK_INSTALL_DIR=/home/btilford/zephyr-sdk-0.16.5
  source /home/btilford/zephyr-sdk-0.16.5/environment-setup-x86_64-pokysdk-linux

  # For ZMK main branch (Zephyr 4.1.0) - FUTURE UPGRADE:
  wget https://github.com/zephyrproject-rtos/sdk-ng/releases/download/v0.17.0/zephyr-sdk-0.17.0_linux-x86_64.tar.xz
  tar xf zephyr-sdk-0.17.0_linux-x86_64.tar.xz
  cd zephyr-sdk-0.17.0 && ./setup.sh
  source ~/zephyr-sdk-0.17.0/zephyr-env.sh
  ```

  **⚠️ CRITICAL SDK Version Compatibility:**
  - **ZMK v0.3.0** → **Zephyr SDK v0.16.x** (Bluetooth crypto support, current setup)
  - **ZMK main** → **Zephyr SDK v0.17.0+** (Zephyr 4.1 compatibility, future upgrade)

  **SDK Version Differences:**
  - **v0.16.5**: Manual environment setup, full Bluetooth ECC support with ZMK v0.3.0
  - **v0.17.0**: Single `zephyr-env.sh` script, but has PSA crypto header issues with ZMK v0.3.0

### Optional Tools
- `keymap-drawer`: Keymap visualization
- `zmk_keymap_extractor.py`: Custom script for processing complex ZMK keymaps
- VS Code with DTS language support
- ZMK Studio for testing (when available)

## Advanced Features

### Keymap Visualization
Repository includes automated keymap diagram generation via keymap-drawer.

**Local Commands:**
- `just test-layouts` - Validate keymap parsing compatibility
- `just draw-corne` - Generate corne keyboard diagram
- `just draw-crosses` - Generate crosses keyboard diagram
- `just draw` - Generate both diagrams with error handling
- `just clean-generated` - Remove all generated files

**Configuration Files:**
- `keymap-drawer/corne-42.yaml` - Corne layout and styling
- `keymap-drawer/crosses-42.yaml` - Crosses layout and styling

**Generated Files (in build/ directory):**
- `build/keymaps/` - Processed keymap files with all layers
- `build/diagrams/` - Final SVG diagram outputs
- `build/temp/` - Intermediate parsing files

**Features:**
- Full 11-layer visualization (Base, Symbol, Numpad, Motion, Text, Media, Desktop, Function, Mouse, MouseSnipe, System)
- Complex behavior preservation (home row mods, layer taps, combos)
- Conditional compilation handling (REAL_POINTING_DEVICE, CONFIG_WIRELESS)
- Automated intermediate file processing via `zmk_keymap_extractor.py`

### Trackball Configuration
Custom trackball support for PMW3610 hardware with separate left/right functionality.

**File Structure:**
- `config/trackball_base.dtsi` - Shared mouse behaviors and scalers
- `config/trackball_movement.dtsi` - Right-side movement configuration
- `config/trackball_scroll.dtsi` - Left-side scrolling configuration
- `config/trackball.dtsi` - Fallback dual-functionality

**Mouse Behaviors:**
- `&mmv` - Mouse movement with acceleration
- `&msc` - Mouse scrolling with timing
- `&mkp` - Mouse button clicks
- `zip_xy_scaler` - XY coordinate scaling
- `zip_scroll_scaler` - Scroll wheel scaling

**Conditional Loading Pattern:**
```c
#ifdef REAL_POINTING_DEVICE
  #if defined(CROSSES_LEFT) || defined(SHIELD_crosses_left)
    #include "trackball_scroll.dtsi"
  #elif defined(CROSSES_RIGHT) || defined(SHIELD_crosses_right)
    #include "trackball_movement.dtsi"
  #else
    #include "trackball.dtsi"
  #endif
#endif
```

**Hardware Compatibility:**
- PMW3610 driver main branch (Zephyr 3.5)
- PMW3610 driver zephyr-4.1 branch (Zephyr 4.1)
- Compatible strings: `pixart,pmw3610` vs `pixart,pmw3610-efogtech`

## GitHub Actions Customization

### Dynamic Artifact Naming
Build artifacts include GitHub ref names for easy identification across branches/tags.

**Implementation:**
- `build.yaml` uses `REF_NAME` placeholders
- Preprocessing job replaces placeholders with actual branch/tag names
- Handles special characters (slashes, etc.) in ref names

**Workflow Features:**
- `preprocess` job validates YAML before building
- Artifact names: `board-shield-ref-name`
- Archive names: `zmk-firmware-ref-name`

**Example Artifact Names:**
- Branch `feature/keyboard-layout`: `corne-42-left-feature-keyboard-layout`
- Tag `v1.2.3`: `settings-reset-v1.2.3`
- Main branch: `crosses-42-right-main`

**Benefits:**
- Easy identification of builds from different branches
- Clean CI/CD artifact management
- Automatic handling of all ref types

## Keymap Inclusion Issues

### Crosses Keyboard Using Wrong Keymaps
**Problem**: Crosses keyboard flashes with original gggw-zmk-keebs mappings instead of custom keymaps.

**Root Cause**: Shield keymaps take precedence over config directory keymaps in ZMK's build system.

**Solution**: The crosses board definitions have been integrated into this repository. Custom keymaps are now properly included in the shield definition.

**Verification**: Check firmware binary contains custom behaviors:
```bash
strings .build/crosses_42_right/zephyr/zmk.elf | grep -E "(hml|hmr|magic_shift|smart_num)"
```

## Troubleshooting

### DTS Compilation Issues

**"Could not find any keymap nodes" (keymap-drawer)**
- **Cause:** DTS compilation fails due to undefined references
- **Check:** Ensure all mouse behaviors are defined (`&mmv`, `&msc`, `&mkp`)
- **Fix:** Verify trackball files include complete behavior definitions

**Undefined Reference Errors**
- **Common Issues:** Missing scalers, incomplete behaviors
- **Mouse Behaviors:** Must define compatible strings and properties
- **Input Scalers:** `zip_xy_scaler`, `zip_scroll_scaler` must be defined

**Version Compatibility**
- **ZMK/Zephyr Mismatch:** Ensure driver versions match Zephyr version
- **PMW3610 Driver:** main branch (Zephyr 3.5), zephyr-4.1 branch (Zephyr 4.1)
- **Compatible Strings:** Must match hardware definitions

### Build Issues

**GitHub Actions YAML Processing**
- **Backtick Errors:** Remove backticks from file redirections
- **Special Characters:** Escape slashes in branch names
- **Validation:** Always validate processed YAML syntax

**West Update Required**
- Run `west update` after version changes
- Clears old dependencies and pulls correct versions
- Required when switching ZMK/Zephyr versions

### Version Management Issues

**SDK Version Conflicts**
- **PSA Crypto Headers Missing:** `psa/crypto.h` not found - indicates wrong SDK version for ZMK branch
- **Libc Mutex Conflicts:** Conflicting `__lock___libc_recursive_mutex` types - Zephyr/SDK version mismatch
- **Build Assertion Failures:** Device name too long - may indicate version compatibility issues

**Version Switching Process:**
1. Update `west.yml` ZMK revision to desired version
2. Run `west update --fetch-opt=--filter=blob:none`
3. Switch Zephyr SDK version to match ZMK requirements
4. Clean build artifacts: `just clean`
5. Test build: `just build corne`

**When to Upgrade:**
- Need latest ZMK features → Use main branch
- Hardware requires Zephyr 4.1 → Use main branch
- Stable production → Stick with v0.3.0

**Rollback Process:**
- Change ZMK revision back to `v0.3.0` in `west.yml`
- Run `west update` to revert dependencies
- Switch to Zephyr SDK v0.16.x
- Test builds to ensure stability

### Environment Setup Issues

**Virtual Environment Problems**
- **Not Activated:** Run `source zmk-env/bin/activate` before using Python tools
- **Wrong Python Version:** Ensure venv uses Python 3.10+
- **Missing Dependencies:** Install all packages: `pip install west keymap-drawer pyelftools`

**Zephyr SDK Issues**
- **Version Mismatch:** Must use SDK v0.17.0 for Zephyr v4.1.0 compatibility
- **Environment Not Sourced:** Run `source ~/zephyr-sdk-0.17.0/zephyr-env.sh`
- **Installation Failed:** Check available disk space and permissions
- **CMake Not Found:** Install system packages: `sudo apt-get install cmake ninja-build` (Ubuntu/Debian)

**West Issues**
- **Command Not Found:** Install via pip: `pip install west`
- **Workspace Not Initialized:** Run `just init` first
- **Module Updates:** Run `west update` after changing ZMK versions

### Keymap-Drawer Issues

**Layout Compatibility**
- **Missing Layouts:** Ensure keyboard layouts are defined
- **gggw_crosses_42_layout:** Required for crosses keyboard
- **foostan_corne_6col_layout:** Required for corne keyboard

**Configuration Errors**
- **Invalid YAML:** Check syntax in `.yaml` config files
- **Missing Behaviors:** Ensure all referenced behaviors exist
- **Path Issues:** Verify correct file paths in commands

### Keymap Inclusion Issues

**Crosses Keyboard Using Wrong Keymaps**
- **Problem**: Crosses keyboard flashes with original gggw-zmk-keebs mappings instead of custom keymaps
- **Root Cause**: Shield keymaps take precedence over config directory keymaps in ZMK's build system
- **Solution**: Extract board definitions from external repository and integrate locally
  1. Copy board definitions to `boards/shields/crosses/` and `zmk/app/boards/shields/crosses/`
  2. Add required ZMK modules directly to `config/west.yml`
  3. Create shield-specific keymap override (`config/crosses_right.keymap`)
  4. Remove external gggw-zmk-keebs dependency
- **Verification**: Check firmware binary contains custom behaviors:
  ```bash
  strings .build/crosses_42_right/zephyr/zmk.elf | grep -E "(hml|hmr|magic_shift|smart_num)"
  ```

---

*This document should be updated when new patterns or conventions are established. Last updated: $(date)*

*This document should be updated when new patterns or conventions are established. Last updated: $(date)*