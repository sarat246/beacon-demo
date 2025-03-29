import json
import re
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def resolve_reference(data, ref_path):
    # ... (same resolve_reference function as before)

def correct_token_reference(data, value, current_path=""):
    # ... (same correct_token_reference function as before, but use logging)
    if resolved_value is None:
        logging.warning(f"Could not correct reference: {value} at {current_path}")

def correct_references_in_data(data, current_path=""):
    # ... (same correct_references_in_data function as before)

# --- Main Execution ---
file_path = 'tokens/btokens.json'

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        token_data = json.load(f)
except FileNotFoundError:
    logging.error(f"File '{file_path}' not found.")
    sys.exit(1)  # Exit with an error code
except json.JSONDecodeError:
    logging.error(f"Invalid JSON in file '{file_path}'.")
    sys.exit(1)

correct_references_in_data(token_data)

try:
    with open('tokens/btokens.json', 'w', encoding='utf-8') as f: # Overwrite original
        json.dump(token_data, f, indent=2)
    logging.info("Token references corrected and saved to '%s'", file_path)
except IOError as e:
    logging.error(f"Error writing to file '{file_path}': {e}")
    sys.exit(1)