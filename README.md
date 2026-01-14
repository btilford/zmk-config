# ZMK Keyboard Configuration

This repository contains ZMK firmware configuration for custom mechanical keyboards, specifically supporting Corne and Crosses layouts with advanced features like trackball integration and comprehensive layer management.

## Features

- **Multi-Keyboard Support**: Corne and Crosses keyboard configurations
- **Trackball Integration**: PMW3610 sensor support with separate left/right functionality
- **Advanced Layers**: 11 layers with complex behaviors and combos
- **Automated Documentation**: Keymap visualization via keymap-drawer
- **Comprehensive Testing**: Keymap parsing and build verification

## Prerequisites

### System Requirements
- Linux (recommended) or macOS
- Python 3.10+
- Git

### Zephyr SDK Installation

**Important:** This project currently uses ZMK v0.3.0, which requires Zephyr SDK v0.16.5 for proper Bluetooth ECC support. Using v0.17.0 causes crypto compatibility issues.

#### For Current Setup (ZMK v0.3.0 + Bluetooth ECC Support)

1. **Download Zephyr SDK v0.16.5:**
   ```bash
   # For Linux x86_64
   wget https://github.com/zephyrproject-rtos/sdk-ng/releases/download/v0.16.5/zephyr-sdk-0.16.5_linux-x86_64.tar.xz
   tar xf zephyr-sdk-0.16.5_linux-x86_64.tar.xz
   ```

2. **Install SDK:**
   ```bash
   cd zephyr-sdk-0.16.5
   ./setup.sh
   ```

3. **Source environment (add to your shell profile):**
   ```bash
   export ZEPHYR_SDK_INSTALL_DIR=/home/btilford/zephyr-sdk-0.16.5
   source /home/btilford/zephyr-sdk-0.16.5/environment-setup-x86_64-pokysdk-linux
   ```

#### Alternative: ZMK Main Branch (Future Upgrade)

For ZMK main branch with latest features, use Zephyr SDK v0.17.0:

```bash
# Download and install v0.17.0
wget https://github.com/zephyrproject-rtos/sdk-ng/releases/download/v0.17.0/zephyr-sdk-0.17.0_linux-x86_64.tar.xz
tar xf zephyr-sdk-0.17.0_linux-x86_64.tar.xz
cd zephyr-sdk-0.17.0
./setup.sh

# Source environment (v0.17.0 has zephyr-env.sh)
source ~/zephyr-sdk-0.17.0/zephyr-env.sh
```

#### Key Differences Between SDK Versions

| Feature | v0.16.5 (Current) | v0.17.0 (Future) |
|---------|-------------------|------------------|
| **ZMK Compatibility** | v0.3.0 (stable) | main branch (latest) |
| **Bluetooth ECC** | ✅ Full support | ⚠️ Crypto header issues |
| **Environment Script** | `environment-setup-x86_64-pokysdk-linux` | `zephyr-env.sh` |
| **Zephyr Version** | 3.5.0+zmk-fixes | 4.1.0 |
| **Setup Method** | Manual env vars + source script | Single source script |

**Recommendation:** Stick with v0.16.5 for current production use. Upgrade to v0.17.0 + ZMK main when ready for latest features.

### Development Tools

**Recommendation:** Use a Python virtual environment (venv) for better dependency isolation. This prevents conflicts with system packages and makes it easier to manage different project requirements.

#### Option 1: Virtual Environment (Recommended)

```bash
# Create and activate virtual environment
python -m venv zmk-env
source zmk-env/bin/activate  # On Windows: zmk-env\Scripts\activate

# Install Python tools
pip install west keymap-drawer pyelftools
```

#### Option 2: User Installation

```bash
# Install to user directory (avoids system pollution)
pip install --user west keymap-drawer pyelftools
```

2. **Install just (command runner):**
   ```bash
   # On Arch Linux
   sudo pacman -S just

   # Or download from GitHub releases
   # https://github.com/casey/just/releases
   ```

**Note:** If using a virtual environment, remember to activate it (`source zmk-env/bin/activate`) before running commands that depend on these Python packages.

## Quick Start

1. **Install Prerequisites:**
   Follow the [Prerequisites](#prerequisites) section above to install Zephyr SDK, west, just, and keymap-drawer.

2. **Clone and Setup:**
   ```bash
   git clone <repository-url>
   cd zmk-config

   # If using virtual environment, activate it first
   # source zmk-env/bin/activate

   just init
   ```

3. **Build All Keyboards:**
   ```bash
   just build all
   ```

4. **Test Keymap Compatibility:**
   ```bash
   just test-layouts
   ```

5. **Generate Keymap Diagrams:**
   ```bash
   just draw
   ```

6. **Clean Generated Files:**
   ```bash
   just clean-generated
   ```

## Build Commands

### Core Build Commands

| Command | Description |
|---------|-------------|
| `just init` | Initialize west workspace and clone ZMK dependencies |
| `just update` | Update west modules |
| `just build all` | Build firmware for all configured keyboards |
| `just build corne` | Build firmware for Corne keyboards only |
| `just build crosses` | Build firmware for Crosses keyboards only |
| `just clean` | Remove build artifacts |
| `just clean-all` | Remove all generated files (west, zmk, etc.) |

### Specific Target Builds

Build individual keyboard variants:

```bash
# Corne variants
just build corne-left
just build corne-right

# Crosses variants
just build crosses-left
just build crosses-right
```

### Keymap-Drawer Commands

Generate visual keymap diagrams:

| Command | Description |
|---------|-------------|
| `just test-layouts` | Validate keymap parsing compatibility |
| `just draw-corne` | Generate Corne keyboard diagram |
| `just draw-crosses` | Generate Crosses keyboard diagram |
| `just draw` | Generate diagrams for both keyboards |
| `just clean-generated` | Remove all generated files |

Generated files are placed in the `build/` directory:
- `build/keymaps/` - Generated keymap files
- `build/diagrams/` - Generated SVG diagrams
- `build/temp/` - Intermediate parsing files

### Why Intermediate Files?

The keymap generation process uses intermediate files for several important reasons:

1. **Complex Keymap Processing:** Your ZMK keymaps contain advanced features like home row mods (`&hml`), layer taps (`&lt`), and conditional compilation (`#ifdef`). The `zmk_keymap_extractor.py` script processes these complex constructs and generates simplified DTS files that keymap-drawer can understand.

2. **Define Resolution:** The script resolves `#define` statements and conditional compilation based on your `.conf` files, ensuring the generated keymaps accurately reflect your actual keyboard configuration.

3. **Layout Compatibility:** Keymap-drawer requires specific keyboard layout identifiers. The intermediate YAML files allow us to specify the correct layout (e.g., `zmk_keyboard: corne`) for proper rendering.

4. **Layer Preservation:** All 11 layers (Base, Symbol, Numpad, Motion, Text, Media, Desktop, Function, Mouse, MouseSnipe, System) are extracted and organized in the correct order.

5. **Reproducibility:** The intermediate files make the generation process transparent and allow for debugging if issues arise.

The workflow ensures that your visual keyboard diagrams stay synchronized with your actual keymap code while handling ZMK's complexity behind the scenes.

Manual keymap processing:

```bash
# Generate full keymaps with all layers
python zmk_keymap_extractor.py config/corne.keymap config/corne.conf build/keymaps/corne-full.keymap -o build/keymaps
python zmk_keymap_extractor.py config/crosses.keymap config/crosses.conf build/keymaps/crosses-full.keymap -o build/keymaps

# Parse and draw
keymap -c keymap-drawer/corne.yaml parse -z build/keymaps/corne-full.keymap > build/temp/corne-full.yaml
sed -i 's/zmk_keyboard: corne-full/zmk_keyboard: corne/' build/temp/corne-full.yaml
keymap -c keymap-drawer/corne.yaml draw build/temp/corne-full.yaml > build/diagrams/corne-full.svg
```

### Testing Commands

| Command | Description |
|---------|-------------|
| `just test <test-config>` | Run specific test configuration |
| `just test config/tests/corne-tap-dance` | Example test run |

### Maintenance Commands

| Command | Description |
|---------|-------------|
| `just upgrade-sdk` | Upgrade Zephyr SDK and dependencies |
| `just clean-nix` | Clear Nix cache (if using Nix) |
| `just list` | List all available build targets |

## Configuration Files

### Keyboard Configurations
- `config/corne.keymap` - Corne keyboard layout
- `config/crosses.keymap` - Crosses keyboard layout
- `config/base.keymap` - Shared layer definitions
- `config/corne.conf` - Corne-specific configuration
- `config/crosses.conf` - Crosses-specific configuration

### Trackball Support
- `config/trackball_base.dtsi` - Shared trackball behaviors
- `config/trackball_movement.dtsi` - Right-side movement
- `config/trackball_scroll.dtsi` - Left-side scrolling
- `REAL_POINTING_DEVICE` define affects mouse layer differences

### Keymap Visualization
- `keymap-drawer/corne.yaml` - Corne diagram configuration
- `keymap-drawer/crosses.yaml` - Crosses diagram configuration
- `zmk_keymap_extractor.py` - Automation script for full keymap generation

## Layer Structure

Both keyboards support 11 layers in this order:

1. **Base** - QWERTY layout with home row mods
2. **Symbol** - Numbers and symbols
3. **Numpad** - Numeric keypad
4. **Motion** - Mouse movement controls
5. **Text** - Text navigation and editing
6. **Media** - Media controls
7. **Desktop** - Desktop management (Linux/Mac)
8. **Function** - Function keys (F1-F12)
9. **Mouse** - Mouse buttons and controls
10. **MouseSnipe** - Precision mouse adjustments
11. **System** - System controls and macros

## Advanced Features

### Trackball Integration
- Separate left/right functionality
- Configurable scaling and acceleration
- Hardware-specific behavior based on `REAL_POINTING_DEVICE`

### Complex Behaviors
- Home row mods (`&hml`, `&hmr`)
- Layer taps (`&lt`)
- Mod taps (`&mt`)
- Combos and custom macros
- Sticky keys and caps word

### Conditional Compilation
- `CONFIG_WIRELESS` - Bluetooth settings
- `REAL_POINTING_DEVICE` - Trackball hardware presence
- `CONFIG_ZMK_DISPLAY` - OLED display support

## Troubleshooting

### Build Issues
- Ensure Zephyr SDK is properly installed and sourced
- Check that `west` workspace is initialized
- Verify all dependencies are installed

### Keymap-Drawer Issues
- Ensure Python dependencies are installed (`pyelftools`)
- If using venv, make sure it's activated: `source zmk-env/bin/activate`
- Check that config files have correct layout specifications
- Verify layer definitions match expected format

### Zephyr SDK Issues
- **Version Mismatch:** Use SDK v0.16.5 for ZMK v0.3.0 (current), v0.17.0 for ZMK main
- **Environment Setup:**
  - v0.16.5: `export ZEPHYR_SDK_INSTALL_DIR=~/zephyr-sdk-0.16.5 && source ~/zephyr-sdk-0.16.5/environment-setup-x86_64-pokysdk-linux`
  - v0.17.0: `source ~/zephyr-sdk-0.17.0/zephyr-env.sh`
- **Bluetooth Crypto Issues:** If PSA crypto header errors occur, ensure SDK version matches ZMK version
- **Permission Issues:** If using system installation, ensure `/opt/zephyr-sdk` is accessible
- **Missing Dependencies:** Install required packages: `sudo apt-get install cmake ninja-build` (Ubuntu/Debian)

### Trackball Problems
- Confirm `REAL_POINTING_DEVICE` is defined for Crosses
- Check PMW3610 driver compatibility
- Verify hardware connections

## Contributing

1. Test builds with `just build all`
2. Verify keymap parsing with `just test-layouts`
3. Update diagrams with `just draw`
4. Commit changes following conventional format

## License

This configuration is provided as-is for educational and personal use.