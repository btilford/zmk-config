default:
    @just --list --unsorted

config := absolute_path('config')
build := absolute_path('.build')
out := absolute_path('firmware')
draw := absolute_path('keymap-drawer')

# parse build.yaml and filter targets by expression
_parse_targets $expr:
    #!/usr/bin/env bash
    attrs="[.board, .shield, .snippet, .\"artifact-name\"]"
    filter="(($attrs | map(. // [.]) | combinations), ((.include // {})[] | $attrs)) | join(\",\")"
    echo "$(yq -r "$filter" build.yaml | grep -v "^," | grep -i "${expr/#all/.*}")"

# build firmware for single board & shield combination
_build_single $board $shield $snippet $artifact *west_args:
    #!/usr/bin/env bash
    set -euo pipefail
    artifact="${artifact:-${shield:+${shield// /+}-}${board}}"
    build_dir="{{ build / '$artifact' }}"

    echo "Building firmware for $artifact..."
    west build -s zmk/app -d "$build_dir" -b $board {{ west_args }} ${snippet:+-S "$snippet"} -- \
        -DZMK_CONFIG="{{ config }}" ${shield:+-DSHIELD="$shield"}

    if [[ -f "$build_dir/zephyr/zmk.uf2" ]]; then
        mkdir -p "{{ out }}" && cp "$build_dir/zephyr/zmk.uf2" "{{ out }}/$artifact.uf2"
    else
        mkdir -p "{{ out }}" && cp "$build_dir/zephyr/zmk.bin" "{{ out }}/$artifact.bin"
    fi

# build firmware for matching targets
build expr *west_args:
    #!/usr/bin/env bash
    set -euo pipefail
    targets=$(just _parse_targets {{ expr }})

    [[ -z $targets ]] && echo "No matching targets found. Aborting..." >&2 && exit 1
    echo "$targets" | while IFS=, read -r board shield snippet artifact; do
        just _build_single "$board" "$shield" "$snippet" "$artifact" {{ west_args }}
    done

# clear build cache and artifacts
clean:
    rm -rf {{ build }} {{ out }}

# clear all automatically generated files
clean-all: clean clean-generated
    rm -rf .west zmk

# clear nix cache
clean-nix:
    nix-collect-garbage --delete-old

# test keymap-drawer layout compatibility
test-layouts:
    #!/usr/bin/env bash
    set -euo pipefail

    echo "Testing keymap-drawer layout compatibility..."

    # Generate temp keymaps for testing
    mkdir -p build/keymaps
    python zmk_keymap_extractor.py "{{ config }}/corne.keymap" "{{ config }}/corne.conf" build/keymaps/corne-42-full.keymap -o build/keymaps
    python zmk_keymap_extractor.py "{{ config }}/crosses.keymap" "{{ config }}/crosses.conf" build/keymaps/crosses-42-full.keymap -o build/keymaps

    # Test corne layout
    if keymap -c "{{ draw }}/corne-42.yaml" parse -z build/keymaps/corne-42-full.keymap >/dev/null 2>&1; then
        echo "✓ Corne layout: Compatible"
    else
        echo "✗ Corne layout: Failed - check configuration"
    fi

    # Test crosses layout
    if keymap -c "{{ draw }}/crosses-42.yaml" parse -z build/keymaps/crosses-42-full.keymap >/dev/null 2>&1; then
        echo "✓ Crosses layout: Compatible"
    else
        echo "✗ Crosses layout: Failed - check configuration"
    fi

# generate corne keymap diagram
draw-corne:
	#!/usr/bin/env bash
	set -euo pipefail

	echo "Generating corne keymap diagram..."
	mkdir -p build/keymaps build/diagrams build/temp
	python zmk_keymap_extractor.py "{{ config }}/corne.keymap" "{{ config }}/corne.conf" build/keymaps/corne-42-full.keymap -o build/keymaps
	keymap -c "{{ draw }}/corne-42.yaml" parse -z build/keymaps/corne-42-full.keymap > build/temp/corne-full.yaml
	sed -i 's/zmk_keyboard: corne-42-full/zmk_keyboard: corne/' build/temp/corne-full.yaml
	keymap -c "{{ draw }}/corne-42.yaml" draw build/temp/corne-full.yaml > build/diagrams/corne-42-full.svg
	cp build/diagrams/corne-42-full.svg "{{ draw }}/corne-42-full.svg"
	echo "✓ Generated build/diagrams/corne-42-full.svg"
	echo "✓ Updated keymap-drawer/corne-42-full.svg"

# generate crosses keymap diagram
draw-crosses:
	#!/usr/bin/env bash
	set -euo pipefail

	echo "Generating crosses keymap diagram..."
	mkdir -p build/keymaps build/diagrams build/temp
	python zmk_keymap_extractor.py "{{ config }}/crosses.keymap" "{{ config }}/crosses.conf" build/keymaps/crosses-42-full.keymap -o build/keymaps
	keymap -c "{{ draw }}/crosses-42.yaml" parse -z build/keymaps/crosses-42-full.keymap > build/temp/crosses-full.yaml
	keymap -c "{{ draw }}/crosses-42.yaml" draw -j "{{ config }}/crosses-info.json" -l gggw_crosses_42_layout build/temp/crosses-full.yaml > build/diagrams/crosses-42-full.svg
	cp build/diagrams/crosses-42-full.svg "{{ draw }}/crosses-42-full.svg"
	cp build/diagrams/crosses-42-full.svg "{{ draw }}/crosses-42.svg"
	echo "✓ Generated build/diagrams/crosses-42-full.svg"
	echo "✓ Updated keymap-drawer/crosses-42-full.svg"
	echo "✓ Updated keymap-drawer/crosses-42.svg"

# clean generated files
clean-generated:
    rm -rf build/

# generate both keymap diagrams
draw: test-layouts
    #!/usr/bin/env bash
    set -euo pipefail

    echo "Generating keymap diagrams..."

    if just draw-corne; then
        echo "✓ Corne diagram generated successfully"
    else
        echo "⚠ Corne diagram failed, continuing..."
    fi

    if just draw-crosses; then
        echo "✓ Crosses diagram generated successfully"
    else
        echo "⚠ Crosses diagram failed, continuing..."
    fi

    echo "Keymap generation complete. Check for any warnings above."

# initialize west
init:
    west init -l config
    west update --fetch-opt=--filter=blob:none
    west zephyr-export

# list build targets
list:
    @just _parse_targets all | sed 's/,*$//' | sort | column

# update west
update:
    west update --fetch-opt=--filter=blob:none

# upgrade zephyr-sdk and python dependencies
upgrade-sdk:
    nix flake update --flake .

[no-cd]
test $testpath *FLAGS:
    #!/usr/bin/env bash
    set -euo pipefail
    testcase=$(basename "$testpath")
    build_dir="{{ build / "tests" / '$testcase' }}"
    config_dir="{{ '$(pwd)' / '$testpath' }}"
    cd {{ justfile_directory() }}

    if [[ "{{ FLAGS }}" != *"--no-build"* ]]; then
        echo "Running $testcase..."
        rm -rf "$build_dir"
        west build -s zmk/app -d "$build_dir" -b native_posix_64 -- \
            -DCONFIG_ASSERT=y -DZMK_CONFIG="$config_dir"
    fi

    ${build_dir}/zephyr/zmk.exe | sed -e "s/.*> //" |
        tee ${build_dir}/keycode_events.full.log |
        sed -n -f ${config_dir}/events.patterns > ${build_dir}/keycode_events.log
    if [[ "{{ FLAGS }}" == *"--verbose"* ]]; then
        cat ${build_dir}/keycode_events.log
    fi

    if [[ "{{ FLAGS }}" == *"--auto-accept"* ]]; then
        cp ${build_dir}/keycode_events.log ${config_dir}/keycode_events.snapshot
    fi
    diff -auZ ${config_dir}/keycode_events.snapshot ${build_dir}/keycode_events.log
