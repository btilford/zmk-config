#!/usr/bin/env python3
import re
import sys


def parse_conf_defines(conf_file):
    """Extract CONFIG_ defines from .conf files"""
    defines = []
    try:
        with open(conf_file, "r") as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if line.startswith("#") or not line:
                    continue
                if line.startswith("CONFIG_") and "=" in line:
                    key, value = line.split("=", 1)
                    # Convert CONFIG_BT=n to -DCONFIG_BT=n
                    defines.append(f"-D{key.strip()}={value.strip()}")
    except FileNotFoundError:
        pass  # Conf file might not exist
    return defines


def parse_keymap_defines(keymap_file):
    """Extract additional defines from .keymap files"""
    defines = []
    with open(keymap_file, "r") as f:
        content = f.read()
        # Find simple #define statements (not macro definitions)
        define_pattern = r"#define\s+(\w+)(?:\s+([^\\\n]+))?"
        matches = re.findall(define_pattern, content, re.MULTILINE)
        for match in matches:
            name, value = match
            if value and value.strip() and not value.strip().startswith("#"):
                defines.append(f"-D{name}={value.strip()}")
            elif not value.strip():
                defines.append(f"-D{name}")
    return defines


def extract_layers_from_base(base_file, defines):
    """Extract layer definitions from base.keymap with define handling"""
    with open(base_file, "r") as f:
        lines = f.readlines()

    # Process conditional compilation
    processed_lines = []
    skipping = False
    for line in lines:
        if line.startswith("#ifdef REAL_POINTING_DEVICE"):
            skipping = "REAL_POINTING_DEVICE" not in defines
            continue
        elif line.startswith("#ifdef CONFIG_WIRELESS"):
            skipping = "CONFIG_WIRELESS" not in defines
            continue
        elif line.startswith("#else"):
            skipping = not skipping  # Flip the skipping state
            continue
        elif line.startswith("#endif"):
            skipping = False
            continue

        if not skipping:
            processed_lines.append(line)

    content = "".join(processed_lines)

    # Keep defines as is for keymap-drawer compatibility

    # Debug
    print(f"Processed content length: {len(content)}")
    if "ZMK_BASE_LAYER(Base," in content:
        print("Found Base layer in content")
    else:
        print("Base layer NOT found in content")

    layers = {}
    # Match ZMK_BASE_LAYER(name, bindings...)
    layer_pattern = r"ZMK_BASE_LAYER\s*\(\s*(\w+)\s*,(.*?)\)"

    for match in re.finditer(layer_pattern, content, re.DOTALL):
        layer_name = match.group(1)
        layer_bindings = match.group(2)
        # Clean up the bindings - remove trailing comma and whitespace
        bindings = layer_bindings.strip()
        if bindings.endswith(","):
            bindings = bindings[:-1].strip()
        # Remove comments and newlines
        bindings = re.sub(r"/\*.*?\*/", "", bindings)
        bindings = re.sub(r"\s+", " ", bindings).strip()

        # Replace unknown behaviors with &trans for Base layer to ensure parsing
        if layer_name == "Base":
            bindings = re.sub(r"&gresc", "&trans", bindings)
            bindings = re.sub(r"MAGIC_SHIFT", "&trans", bindings)
            bindings = re.sub(r"SMART_NUM", "&trans", bindings)
            bindings = re.sub(r"&ldr", "&trans", bindings)

        layers[layer_name] = bindings

    return layers


def generate_dts_structure(layers):
    """Generate keymap-drawer compatible DTS structure"""
    dts_lines = [
        "// Layer defines",
        "#define BASE 0",
        "#define SYM 1",
        "#define NUMPD 2",
        "#define MOTION 3",
        "#define TEXT 4",
        "#define MEDIA 5",
        "#define DM 6",
        "#define FKEYS 7",
        "#define MOUSE 8",
        "#define BTOOTH 9",
        "",
        "/ {",
        "    keymap: keymap {",
        '        compatible = "zmk,keymap";',
        "",
    ]

    # Sort layers by definition order
    layer_order = [
        "Base",
        "Symbol",
        "Numpad",
        "Motion",
        "Text",
        "Media",
        "Desktop",
        "Function",
        "Mouse",
        "MouseSnipe",
        "System",
    ]

    for layer_name in layer_order:
        if layer_name in layers:
            # Format bindings multiline
            binding_str = layers[layer_name]
            binding_parts = [
                part.strip() for part in binding_str.split(",") if part.strip()
            ]
            if binding_parts:
                dts_lines.append(f"        {layer_name} {{")
                dts_lines.append("            bindings = <")
                for part in binding_parts[:-1]:
                    dts_lines.append(f"                {part},")
                if binding_parts:
                    dts_lines.append(f"                {binding_parts[-1]}")
                dts_lines.append("            >;")
                dts_lines.append("        };")
                dts_lines.append("")

    dts_lines.extend(["    };", "};"])
    return "\n".join(dts_lines)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate full keymap files for keymap-drawer"
    )
    parser.add_argument("keymap_file", help="Input keymap file")
    parser.add_argument("conf_file", help="Input configuration file")
    parser.add_argument("output_file", help="Output keymap file")
    parser.add_argument(
        "-o", "--output-dir", help="Output directory for generated files"
    )

    args = parser.parse_args()

    keymap_file = args.keymap_file
    conf_file = args.conf_file
    output_file = args.output_file

    if args.output_dir:
        import os

        output_file = os.path.join(args.output_dir, os.path.basename(output_file))

    # Extract defines
    config_defines = parse_conf_defines(conf_file)
    keymap_defines = parse_keymap_defines(keymap_file)
    all_defines = config_defines + keymap_defines

    print(f"Defines found: {all_defines}")

    # Extract layers from base.keymap
    layers = extract_layers_from_base("config/base.keymap", all_defines)

    print(f"Layers extracted: {list(layers.keys())}")

    # Generate DTS
    dts_output = generate_dts_structure(layers)

    # Write output
    with open(output_file, "w") as f:
        f.write(dts_output)

    print(f"Generated {output_file} with {len(layers)} layers")


if __name__ == "__main__":
    main()
