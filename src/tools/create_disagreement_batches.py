import json
import math
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define paths
INPUT_FILE = Path('data/batches/master_sample_file.json')
OUTPUT_DIR = Path('data/batches/')
OUTPUT_FILE_SHAYNE = OUTPUT_DIR / 'shayne_rater_disagreement.json'
OUTPUT_FILE_ANKA = OUTPUT_DIR / 'anka_rater_disagreement.json'

# Define the split point
SPLIT_POINT = 60

def get_conv_id_num(task):
    """Extracts the integer part of conversation_id for sorting."""
    conv_id = task.get('data', {}).get('conversation_id', 'conv_9999')
    try:
        return int(conv_id.split('_')[-1])
    except (ValueError, IndexError):
        logging.warning(f"Could not parse conversation_id '{conv_id}' for sorting, placing last.")
        return float('inf') # Place unparseable IDs at the end

def create_batches():
    """Reads tasks from the master file and splits them into two specific batch files (1-60, 61-120)."""
    if not INPUT_FILE.exists():
        logging.error(f"Input file not found: {INPUT_FILE}")
        return

    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            master_tasks = json.load(f)
        logging.info(f"Read {len(master_tasks)} tasks from {INPUT_FILE}")
    except json.JSONDecodeError as e:
        logging.error(f"Error reading or decoding JSON from {INPUT_FILE}: {e}")
        return
    except Exception as e:
        logging.error(f"An unexpected error occurred while reading {INPUT_FILE}: {e}")
        return

    # Sort tasks by conversation_id number
    try:
        sorted_tasks = sorted(master_tasks, key=get_conv_id_num)
    except Exception as e:
        logging.error(f"Error sorting tasks: {e}. Cannot create batches.")
        return

    total_tasks = len(sorted_tasks)
    logging.info(f"Sorted {total_tasks} tasks by conversation_id.")

    if total_tasks < SPLIT_POINT:
        logging.warning(f"Total tasks ({total_tasks}) is less than the split point ({SPLIT_POINT}). Adjusting split.")
        shayne_tasks = sorted_tasks
        anka_tasks = []
    elif total_tasks < 120:
         logging.warning(f"Total tasks ({total_tasks}) is less than the expected 120. Batches may not be as expected.")
         shayne_tasks = sorted_tasks[:SPLIT_POINT]
         anka_tasks = sorted_tasks[SPLIT_POINT:]
    else:
         # Split the tasks exactly at the defined point
         shayne_tasks = sorted_tasks[:SPLIT_POINT]
         anka_tasks = sorted_tasks[SPLIT_POINT:120] # Ensure we only take up to 120 if more exist
         if total_tasks > 120:
              logging.warning(f"Found {total_tasks} tasks, but only using the first 120 for the split.")

    logging.info(f"Assigning {len(shayne_tasks)} tasks (1-{SPLIT_POINT}) to Shayne.")
    logging.info(f"Assigning {len(anka_tasks)} tasks ({SPLIT_POINT + 1}-120) to Anka.")

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Write Shayne's batch file
    try:
        with open(OUTPUT_FILE_SHAYNE, 'w', encoding='utf-8') as f:
            json.dump(shayne_tasks, f, indent=4, ensure_ascii=False)
        logging.info(f"Successfully wrote Shayne disagreement batch to {OUTPUT_FILE_SHAYNE}")
    except Exception as e:
        logging.error(f"Error writing Shayne batch file {OUTPUT_FILE_SHAYNE}: {e}")

    # Write Anka's batch file
    try:
        with open(OUTPUT_FILE_ANKA, 'w', encoding='utf-8') as f:
            json.dump(anka_tasks, f, indent=4, ensure_ascii=False)
        logging.info(f"Successfully wrote Anka disagreement batch to {OUTPUT_FILE_ANKA}")
    except Exception as e:
        logging.error(f"Error writing Anka batch file {OUTPUT_FILE_ANKA}: {e}")


if __name__ == "__main__":
    create_batches() 