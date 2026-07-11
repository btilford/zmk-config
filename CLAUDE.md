# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

ZMK firmware configuration for two wireless split keyboards:
- **Corne** (nice_nano board, 42-key, no trackball)
- **Crosses** (nice_nano_v2 board, 42-key, PMW3610 trackball — left half scrolls, right half moves cursor)

Both share `config/base.keymap` and `config/combos.dtsi` / `config/leader.dtsi` / `config/mouse.dtsi`.

## Build commands

```bash
just build all              # build all targets
just build corne            # corne left + right
just build crosses          # crosses left + right
just build crosses-42-left  # single target
just clean                  # remove .build/ and firmware/
just init                   # west init + update (first-time setup)
just update                 # west update after version changes
just list                   # list all build targets
```

Firmware output lands in `firmware/` as `.uf2` or `.bin` files.

## Keymap diagram commands

```bash
just draw                   # generate both SVG diagrams (runs test-layouts first)
just draw-corne             # corne only
just draw-crosses           # crosses only
just test-layouts           # validate keymap-drawer parse compatibility
just clean-generated        # remove build/ (diagrams, temp files)
```

Diagrams are committed to `keymap-drawer/` after generation. The `zmk_keymap_extractor.py` script preprocesses keymaps (resolves `#define`, conditional blocks, complex behaviors) before passing to `keymap-drawer`.

## Testing

```bash
just test config/tests/<test-name>              # build and run test
just test config/tests/<test-name> --no-build   # re-run without rebuild
just test config/tests/<test-name> --auto-accept # accept output as new snapshot
```

Tests compile for `native_posix_64` and diff against `keycode_events.snapshot`.

## Environment

The `.envrc` (direnv) sets `ZEPHYR_SDK_INSTALL_DIR` and adds the ARM toolchain to `PATH`. The Python venv at `keymap-drawer-env/` provides `keymap-drawer`; activate it when running draw commands if not already active.

**SDK version**: currently SDK v0.17.0 (`/home/btilford/zephyr-sdk-0.17.0`). ZMK is pinned to `v0.3.0` (see `config/west.yml`).

## Architecture

### Config file roles

| File | Purpose |
|------|---------|
| `config/base.keymap` | All layer definitions, behaviors, combos — shared by both keyboards. **Do not modify.** |
| `config/corne.keymap` | Corne entry point: sets `CONFIG_WIRELESS`, defines `ZMK_BASE_LAYER`, includes `base.keymap` |
| `config/crosses_shared.dtsi` | Crosses entry point: additionally sets `REAL_POINTING_DEVICE`, sets physical layout to `gggw_crosses_42_layout` |
| `config/crosses_left.keymap` / `config/crosses_right.keymap` | Per-half includes of `crosses_shared.dtsi` |
| `config/combos.dtsi`, `config/leader.dtsi`, `config/mouse.dtsi` | Feature includes pulled in by `base.keymap`. **Do not modify.** |
| `config/trackball_base.dtsi` | Shared mouse behaviors and input scalers |
| `config/trackball_scroll.dtsi` | Left-half: trackball → scroll |
| `config/trackball_movement.dtsi` | Right-half: trackball → cursor movement |
| `config/corne.conf` / `config/crosses.conf` | Kconfig overrides (Bluetooth, display, etc.) |
| `config/west.yml` | West manifest: ZMK + all modules (urob helpers, PMW3610 driver, gggw-zmk-keebs, etc.) |
| `build.yaml` | GitHub Actions build matrix |

### Layer order (defined in `base.keymap`)

`BASE(0)` → `SYM(1)` → `NUMPD(2)` → `MOTION(3)` → `TEXT(4)` → `MEDIA(5)` → `DM(6)` → `FKEYS(7)` → `MOUSE(8)` → `MOUSE_SNIPE(9)` → `MOUSE_HYPR(10)` → `BTOOTH(11)`

### Trackball conditional compilation

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

`REAL_POINTING_DEVICE` is only defined in `crosses_shared.dtsi`, not in the Corne keymap.

### Key ZMK modules (from `config/west.yml`)

- `urob/zmk-helpers` — `ZMK_HOLD_TAP`, `ZMK_COMBO`, `ZMK_LAYER`, etc.
- `urob/zmk-auto-layer` — `num_word` behavior
- `urob/zmk-leader-key` — leader key support
- `urob/zmk-tri-state` — tri-state (swapper) behavior
- `efogdev/zmk-pmw3610-driver` — PMW3610 trackball driver (pinned to `zephyr-4.1` branch)
- `Good-Great-Grand-Wonderful/gggw-zmk-keebs` — Crosses board/shield definitions

## Critical constraints

- **Do not disable `CONFIG_BT`** — these are wireless-only keyboards.
- **Do not modify `config/base.keymap`, `config/combos.dtsi`, `config/leader.dtsi`, or `config/mouse.dtsi`** — treat as immutable.
- After modifying shared files, always run `just build all` to confirm nothing breaks across both boards.
- When switching ZMK versions, the PMW3610 driver branch must match the Zephyr version (`main` = Zephyr 3.5, `zephyr-4.1` = Zephyr 4.1).
- Verify custom firmware is in the binary after flashing: `strings .build/crosses_42_right/zephyr/zmk.elf | grep -E "(hml|hmr|magic_shift)"` — if missing, the shield keymap is overriding the config directory.
