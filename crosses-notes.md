# ZMK Firmware Configuration: Final Result

We have successfully implemented advanced mouse layers and resolved the hardware conflicts preventing the trackballs from functioning correctly.

## 🚀 Successfully Implemented Features

### 1. Advanced Mouse Layers
- **Auto-Mouse Layer**: Moving the Right trackball automatically activates the `MOUSE` layer (Layer 8) for 1000ms.
- **Snipe Mode**: Activated via `MOUSE_SNIPE` layer. Cursor speed is slowed (1/4 scaling) for precision.
- **Hyper Mode**: Activated via `MOUSE_HYPR` layer. Cursor speed is accelerated (2x scaling) for fast movement.
- **Scroll Scaling**: Snipe and Hyper modes also apply scaling to scrolling on the left trackball (1/2x and 4x respectively).
- **Inverted Scroll**: Vertical scrolling on the left trackball has been inverted for a "natural" feel (pull down to scroll up).

### 2. Resolved Hardware Conflicts
- **SPI/I2C Collision**: Explicitly disabled I2C and removed the OLED display node. This cleared pins **D2** and **D3** on the `nice!nano_v2`, allowing the trackball's SPI bus to operate without interference.
- **Board Correction**: Unified the build on **`nice_nano_v2`** to ensure correct pin mappings for the actual hardware.

---

## ⚠️ Unresolved Hardware Indicator Case (Blue LED)
Despite multiple attempts to disable the blue status LED on the **Left Half** via devicetree (deleting nodes, redirecting aliases), the LED continues to flash moderately rapidly.

**Technical Findings:**
- The LED is likely being driven by the **Matrix Scanner** because it shares a physical pin (**P0.15**) with Column 2 of the keys.
- If the LED persists even when no Bluetooth connection is being sought, it is a hardware-level reaction to the pin being toggled during the matrix scan and cannot be fully silenced in software without disabling the keys in that column.

---

## Final Solution Status
- **Movement**: Working (Right side, auto-layering enabled).
- **Scrolling**: Working (Left side).
- **Advanced Modes**: Snipe (slow) and Hyper (fast) are fully functional.
- **Power Optimization**: Logging and Display are disabled for maximum battery life.

## Firmware Files
- [crosses_42_left.uf2](file:///home/btilford/Projects/keyboard/zmk-config/firmware/crosses_42_left.uf2)
- [crosses_42_right.uf2](file:///home/btilford/Projects/keyboard/zmk-config/firmware/crosses_42_right.uf2)
