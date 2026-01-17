# ZMK Firmware Fixes & Configuration: Crosses Keyboard

This document provides a comprehensive technical record of the fixes, hardware resolutions, and feature implementations for the Crosses keyboard.

---

## 🚀 Successfully Implemented Features

### 1. Advanced Mouse layers & Trackball Logic
- **Auto-Mouse Layer**: Moving the Right trackball automatically activates the `MOUSE` layer (Layer 8) for 1000ms.
- **Snipe Mode**: Activated via `MOUSE_SNIPE` layer. Reduces cursor speed (1/4 scaling) for precision.
- **Hyper Mode**: Activated via `MOUSE_HYPR` layer. Accelerates cursor speed (2x move, 4x scroll scaling).
- **Inverted Scroll**: Vertical scrolling on the left trackball is inverted for a natural "pull to scroll" feel (pull down to scroll up).
- **Split Strategy**: 
    - **Left Half**: Dedicated scrolling via `zip_xy_to_scroll_mapper`.
    - **Right Half**: Cursor movement and remote scroll listener.
- **Stability**: SPI frequency locked at **1MHz** with internal pull-ups enabled for reliable PMW3610 sensor data.

### 2. Matrix Fix (Row Shift Resolution)
- **Issue**: Rows appeared to be shifted up by one. The default 42-key layout expected a 5-row matrix but skipped physical Row 0.
- **Fix**: Implemented `shifted_transform` in `crosses_shared.dtsi`.
- **Logic**: Maps the logical 42-key layout to physical matrix rows **1, 2, 3, and 4**. This correctly aligns the top key row (Q-P) with physical Row 1 on the Crosses hardware.

---

## 🛠️ Hardware & Build Resolutions

### 1. Pin Conflict & Peripheral Fixes
- **SPI/I2C Collision**: Explicitly disabled the `i2c0` bus and removed the `nice_view` shields to free up pins **D2 (P0.17)** and **D3 (P0.20)** for the PMW3610 trackball sensor.
- **Driver Enablement**: Created side-specific `.conf` files (`config/crosses_left.conf` and `config/crosses_right.conf`) to explicitly enable the PMW3610 driver, resolving linker errors during initialization.
- **Board Correction**: Unified the build on **`nice_nano_v2`** to ensure accurate pin mappings and clock speeds.

### 2. Technical Pin Assignments
| Pin | Function | Use Case | Status |
| :--- | :--- | :--- | :--- |
| **D2 (P0.17)** | SPI SCK | Trackball Clock | **Resolved** (Disabled I2C) |
| **D3 (P0.20)** | Reserved | Reserved | **Resolved** (Disabled I2C) |
| **D1 (P0.06)** | SPI MOSI/MISO | Trackball Data | No conflict |
| **D0 (P0.08)** | SPI CS | Trackball Select | No conflict |
| **D15 (P0.15)**| Blue LED | Matrix Col 2 | **Active** (Hardware Sharing) |

---

## ⚠️ Known Limitations

### Persistent Blue LED (Left Half)
The blue status LED on the left controller flashes during matrix scanning and cannot be silenced in software.
- **Root Cause**: The physical LED shares **P0.15** with Column 2 of the key matrix. 
- **Finding**: Electrical activity from the matrix scanner toggling the pin is what drives the LED, independent of ZMK status software.

---

## 📂 Build System & Tooling
- **Justfile**: Corrected paths for `crosses.keymap` and `crosses-info.json` (removing incorrect `-42` suffixes).
- **Verification Commands**:
    - **Build**: `just build crosses` (Success generates `zmk.uf2` in `firmware/`).
    - **Diagrams**: `just draw-crosses` (Generates SVG diagrams in `keymap-drawer/`).

### Firmware Files
- [crosses_42_left.uf2](file:///home/btilford/Projects/keyboard/zmk-config/firmware/crosses_42_left.uf2)
- [crosses_42_right.uf2](file:///home/btilford/Projects/keyboard/zmk-config/firmware/crosses_42_right.uf2)