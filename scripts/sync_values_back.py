import json
from pathlib import Path

ORIGINAL_FILE = Path("tokens/btokens.json")
FIXED_FILE = Path("tokens/btokens.fixed.json")

def sync_values(fixed, original):
    if isinstance(fixed, dict) and isinstance(original, dict):
        for key, value in fixed.items():
            if key in original:
                if isinstance(value, dict) and 'value' in value:
                    original_value = original.get(key, {})
                    if isinstance(original_value, dict) and 'value' in original_value:
                        original[key]['value'] = value['value']
                    else:
                        original[key] = value
                else:
                    sync_values(value, original[key])
    elif isinstance(fixed, list) and isinstance(original, list):
        for f_item, o_item in zip(fixed, original):
            sync_values(f_item, o_item)

# Load files
with ORIGINAL_FILE.open("r", encoding="utf-8") as f:
    original_data = json.load(f)

with FIXED_FILE.open("r", encoding="utf-8") as f:
    fixed_data = json.load(f)

# Sync values only
sync_values(fixed_data, original_data)

# Save updated original
with ORIGINAL_FILE.open("w", encoding="utf-8") as f:
    json.dump(original_data, f, indent=2)

print("✅ Synced updated token values back to btokens.json")