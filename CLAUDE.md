# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Branch scope — read this first

**This branch (`add-crosses-v2`) builds Crosses v2 and nothing else.** It sits on
ZMK `main` (Zephyr 4.x); `master` stays on ZMK `v0.3.0` for corne, Crosses v1 and
Toucan2. That split is forced, not stylistic — see "Why v1 and v2 cannot share a
manifest" below. Most of the notes further down describe `master`'s targets and
do not apply here.

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

## Why v1 and v2 cannot share a manifest

A west workspace resolves exactly one `zmk` revision, and Crosses v2's boards and
PAW3222 stack only exist on ZMK `main`. That alone would force a split. But even
setting ZMK aside, the two keyboards pull incompatible forks of the *same*
devicetree binding:

| | module | `#input-processor-cells` | used as |
|---|---|---|---|
| v2 | `badjeff/zmk-input-processor-report-rate-limit` | `1` | `<&zip_report_rate_limit 2>` in `crosses_v2.dts` |
| v1 | `efogdev/zmk-report-rate-limit` (via gggw) | `0` | `CONFIG_ZMK_INPUT_PROCESSOR_REPORT_RATE_LIMIT_DEFAULT=2`, a Kconfig the other fork lacks |

Both declare `compatible: zmk,input-processor-report-rate-limit`. West happily
clones both (the project names differ), then the devicetree build fails:

    devicetree error: both .../zmk-input-processor-report-rate-limit/... and
    .../zmk-report-rate-limit/... have 'compatible: zmk,input-processor-report-rate-limit'

Neither fork can substitute for the other — the cell counts differ. Blocking one
via `import: name-blocklist` therefore breaks whichever board needed it. Revisit
only if gggw converges the two upstreams.

Related trap, same family: on ZMK `main` the Zephyr hardware-model-v2 rework
renamed the boards. `nice_nano_v2` is no longer a valid board name; it is
`nice_nano@2.0.0/nrf52840/zmk`. A plain "Invalid BOARD" error is usually this,
not a missing module.

## Local build prerequisites on this branch

ZMK Studio is enabled for `crosses_v2_right`, and its nanopb codegen needs the
`protobuf` and `grpcio-tools` Python packages in the repo venv. Without them the
build dies with `ModuleNotFoundError: No module named 'google'` partway through —
a toolchain gap, not a config error.

```bash
python3 -m venv .venv
./.venv/bin/pip install 'cmake>=3.20,<4' protobuf grpcio-tools
```

Note the venv must be created in the worktree, not copied into it: a copied venv
still points at the path it was created under, so `pip install` silently lands in
the original.

## Critical constraints

- **Do not disable `CONFIG_BT`** — these are wireless-only keyboards.
- **Do not modify `config/base.keymap`, `config/combos.dtsi`, `config/leader.dtsi`, or `config/mouse.dtsi`** — treat as immutable.
- After modifying shared files, always run `just build all` to confirm nothing breaks across both boards.
- When switching ZMK versions, the PMW3610 driver branch must match the Zephyr version (`main` = Zephyr 3.5, `zephyr-4.1` = Zephyr 4.1).
- Verify custom firmware is in the binary after flashing: `strings .build/crosses_42_right/zephyr/zmk.elf | grep -E "(hml|hmr|magic_shift)"` — if missing, the shield keymap is overriding the config directory.
