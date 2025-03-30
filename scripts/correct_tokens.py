import re
from pathlib import Path
from collections import defaultdict
import json  # Import the json library

# Input file (TypeScript tokens)
INPUT_FILE = "tokens/btokens-new.ts"

# Output directory for SCSS files
SCSS_OUTPUT_DIR = "scssbuild"

# Step 1: Load .ts token file
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    ts_content = f.read()

# Step 2: Parse export constants
token_pattern = re.compile(r"export const (\w+)\s*=\s*(.+?);")
parsed = {}

for match in token_pattern.finditer(ts_content):
    var_name, value = match.groups()
    value = value.strip().strip("'").strip('"')
    parsed[var_name] = value

# Step 3: Group by top-level namespace (e.g., CORE, THEME, PROPERTIES) and breakpoints
grouped_literals = defaultdict(lambda: defaultdict(list))
grouped_references = defaultdict(lambda: defaultdict(list))

for var, value in parsed.items():
    css_var = "--" + var.replace("FIGMA_VARS_", "").lower().replace("_", "-")
    parts = var.split("_")
    group = parts[2].lower() if len(parts) > 2 else "misc"
    breakpoint = parts[1].lower() if len(parts) > 1 and parts[1].lower() in ("mobile", "tablet", "desktop") else "all"  # 'all' for non-breakpoint specific

    if re.match(r"^#([A-Fa-f0-9]{3,8})$", value):  # hex
        grouped_literals[group][breakpoint].append({"name": css_var, "value": value, "type": "color"})
    elif re.match(r"^-?\d+(\.\d+)?$", value):  # number
        px_val = f"{value}px"
        grouped_literals[group][breakpoint].append({"name": css_var, "value": px_val, "type": "number"})
    elif value.startswith("FIGMA_VARS_"):
        ref_var = "--" + value.replace("FIGMA_VARS_", "").lower().replace("_", "-")
        grouped_references[group][breakpoint].append({"name": css_var, "value": f"var({ref_var})", "type": "reference"})
    else:
        grouped_literals[group][breakpoint].append({"name": css_var, "value": value, "type": "string"})  # Or determine the correct type

# Step 4: Build nested SCSS map (and JSON structure)
def safe_nested_insert(d, keys, value):
    for key in keys[:-1]:
        if key not in d or not isinstance(d[key], dict):
            d[key] = {}
        d = d[key]
    d[keys[-1]] = value

def build_nested_map_from_vars(group, breakpoint, var_list):
    nested = {}
    for var_data in var_list:
        full_key = var_data["name"]
        val = var_data["value"]
        clean_key = full_key.replace(f"--{group}-{breakpoint}-", "", 1).replace(f"--{group}-", "", 1)
        key_parts = [k for k in clean_key.split("-") if k]
        safe_nested_insert(nested, key_parts, val)
    return nested

def nested_dict_to_scss(d, indent=0):
    spacing = "  " * indent
    lines = ["("]
    for k, v in d.items():
        key = f'"{k}"'
        if isinstance(v, dict):
            nested = nested_dict_to_scss(v, indent + 1)
            lines.append(f"{spacing}  {key}: {nested},")
        else:
            lines.append(f"{spacing}  {key}: {v},")
    lines.append(f"{spacing})")
    return "\n".join(lines)

# Step 5: Write SCSS maps and JSON to files
Path(SCSS_OUTPUT_DIR).mkdir(exist_ok=True)  # Create the scssbuild directory
Path("tokens").mkdir(exist_ok=True)  # Ensure tokens directory exists for JSON
output_data = {}  # For the combined JSON

for group, breakpoint_vars in grouped_literals.items():
    output_data[group] = {}
    for breakpoint, var_list in breakpoint_vars.items():
        nested = build_nested_map_from_vars(group, breakpoint, var_list)
        scss_map = f"${group}-{breakpoint}-tokens: {nested_dict_to_scss(nested)};"
        out_path = f"{SCSS_OUTPUT_DIR}/tokens-{group}-{breakpoint}-nested.scss"  # Save to scssbuild
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(scss_map)
        print(f"✅ Written: {out_path}")
        output_data[group][breakpoint] = nested

for group, breakpoint_vars in grouped_references.items():
    if group not in output_data:
        output_data[group] = {}
    for breakpoint, var_list in breakpoint_vars.items():
        nested = build_nested_map_from_vars(group, breakpoint, var_list)
        scss_map = f"${group}-{breakpoint}-refs: {nested_dict_to_scss(nested)};"
        out_path = f"{SCSS_OUTPUT_DIR}/tokens-{group}-{breakpoint}-refs.scss"  # Save to scssbuild
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(scss_map)
        print(f"✅ Written: {out_path}")
        output_data[group][breakpoint] = nested

# Write combined JSON
json_out_path = "tokens/tokens.json"
with open(json_out_path, "w", encoding="utf-8") as f:
    json.dump(output_data, f, indent=2)
print(f"✅ Written: {json_out_path}")