# Trackball Configuration Fix: Final Result

We have successfully resolved the build errors and hardware conflicts preventing the trackballs from functioning.

## Key Changes
1. **Resolved Pin Conflict**: Removed the `nice_view_adapter` and `nice_view` shields from `build.yaml`. These were claiming pins **D2** and **D3**, which are required for the trackball's SPI clock and interrupt.
2. **Corrected Board Target**: Switched the build target from `nice_nano` (v1) to **`nice_nano_v2`**. This ensures the correct pin definitions and clock speeds are used for your actual hardware.
3. **Robust Side-Specific Configuration**: Implemented a **Split Keymap Strategy**:
   - `config/crosses_left.keymap`: Configures the left trackball for **scrolling**.
   - `config/crosses_right.keymap`: Configures the right trackball for **cursor movement** and receiving scroll events.
   - **SPI Frequency**: Both sides are locked to **1MHz** for stable communication with the PMW3610 sensor.
   - **Pull-ups**: Internal pull-ups are enabled on the SPI bus to ensure clean signals.
4. **Resolved I2C Conflict**: Explicitly disabled the I2C bus and the OLED display driver. On the `nice!nano v2`, the default I2C pins occupy **D2** and **D3**, which physically collided with the trackball's SPI signals. Disabling I2C has fully cleared these pins for the trackball.
5. **Keymap Matrix Correction**: Fixed a row offset issue in the 42-key layout transform where the top row was incorrectly mapped to `RC(0,x)` instead of `RC(1,x)`.
6. **Unified Base Configuration**: Reorganized the keymaps to use `crosses_shared.dtsi`, ensuring that layout changes made to the base map are automatically applied to both the left and right firmware builds.

## Hardware Constraints: Nice!View vs. Trackball
Due to the physical wiring of the Crosses PCB, there is a fundamental pin conflict between the Nice!View display and the PMW3610 trackball sensor. Both devices share the following pins for incompatible hardware functions:

| Pin | Trackball Function | Nice!View Function | Conflict Type |
| :--- | :--- | :--- | :--- |
| **D2 (P0.17)** | **SPI Clock** (SCK) | SPI Data (MOSI) | Electrical Collision |
| **D3 (P0.20)** | **Interrupt** (IRQ) | SPI Clock (SCK) | Signal Collision |
| **D1 (P0.06)** | **SPI Data** (MOSI) | Chip Select (CS) | Bus Collision |

> [!WARNING]
> Because these pins are hard-wired on the PCB, you cannot use the Nice!View displays and the trackballs simultaneously without physical hardware modifications (jumper wires). For this reason, the displays must remain disabled in the firmware to ensure trackball stability.

## Final Solution Status
- **Movement**: The Right trackball controls the cursor with 2:1 scaling.
- **Scrolling**: The Left trackball controls vertical/horizontal scrolling.
- **Sniper Mode**: Hold the `A` key in the Mouse layer to slow down movement and scrolling by 4x.
- **Hyper Mode**: Hold the `Z` key in the Mouse layer to speed up movement by 2x and scrolling by 4x.
- **Auto-Mouse**: Moving the Right trackball automatically activates the `MOUSE` layer.
- **Battery Life**: USB Serial Logging has been **disabled** in this final version to ensure maximum battery efficiency.

## Firmware Files
- [crosses_42_left.uf2](file:///home/btilford/Projects/keyboard/zmk-config/firmware/crosses_42_left.uf2)
- [crosses_42_right.uf2](file:///home/btilford/Projects/keyboard/zmk-config/firmware/crosses_42_right.uf2)
