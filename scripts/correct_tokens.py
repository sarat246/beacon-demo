import json
import re
from pathlib import Path

# Input/output paths
INPUT_FILE = "tokens/btokens.json"
OUTPUT_FILE = "tokens/btokens.fixed.json"

# Define known top-level mappings
top_level_keys = {
    "core": ["colorNeutral", "colorAlerts", "colorBrand", "numbers", "fontFamily"],
    "properties": [
        "fontWeight", "lineHeight", "fontSize", "letterSpacing",
        "paragraphSpacing", "spacing", "borderRadius", "borderWidth",
        "opacity", "boxShadow", "padding","radius"
    ],
    "breakpoints": ["breakpoint", "device", "columns", "margin", "gutter"]
}

# Reverse mapping for easy reference fixing
reference_map = {}
for group, keys in top_level_keys.items():
    for key in keys:
        reference_map[key] = group

def fix_references(value: str, path: list) -> str:
    matches = re.findall(r"\{([^}]+)\}", value)

    for ref in matches:
        parts = ref.split(".")
        if len(parts) > 1:
            base = parts[0]

            # Inject "Theme/Brand" for colorStyles if found inside a theme section
            if base == "colorStyles" and path and "Theme/" in path[0]:
                brand = path[0]
                fixed = f"{brand}.{ref}"
                value = value.replace(f"{{{ref}}}", f"{{{fixed}}}")
            elif base in reference_map:
                fixed = f"{reference_map[base]}.{ref}"
                value = value.replace(f"{{{ref}}}", f"{{{fixed}}}")

    return value


# Recursive token cleaner
# Updated to handle contextual theme-based prefixing
def fix_token_dict(obj, path=None):
    if path is None:
        path = []

    if isinstance(obj, dict):
        new_dict = {}
        for k, v in obj.items():
            new_path = path + [k]
            new_dict[k] = fix_token_dict(v, new_path)
        return new_dict

    elif isinstance(obj, list):
        return [fix_token_dict(item, path) for item in obj]

    elif isinstance(obj, str):
        return fix_references(obj, path)

    return obj

# Normalize top-level keys ONLY for known groups
def normalize_top_level_keys(data: dict) -> dict:
    known = {"core", "properties", "breakpoints"}
    normalized = {}

    for key, value in data.items():
        parts = key.lower().split("/")
        if parts[-1] in known:
            normalized[parts[-1]] = value
        else:
            normalized[key] = value  # preserve Theme/Brand, etc.
    return normalized

# Load, fix, normalize and save
def process_token_file():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Fix references and values
    cleaned = fix_token_dict(data)

    # Normalize top-level keys like "Core/core" → "core"
    cleaned = normalize_top_level_keys(cleaned)

    Path(OUTPUT_FILE).parent.mkdir(exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, indent=2)

    print(f"✅ Token file cleaned and saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    process_token_file()