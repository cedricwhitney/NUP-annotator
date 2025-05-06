import json
import os
import sys
from pathlib import Path
from collections import defaultdict
import logging
from typing import Dict, List, Set, Tuple
import csv # Import csv module

# Remove BatchCreator import as we now read batches directly
# # Add project root to sys.path to allow importing BatchCreator
# project_root = Path(__file__).resolve().parent.parent.parent
# sys.path.insert(0, str(project_root))
# try:
#     from src.tools.create_batches import BatchCreator # Import from the existing script
# except ImportError:
#     logging.error("Failed to import BatchCreator from src.tools.create_batches. Make sure the file exists and is in the correct path.")
#     sys.exit(1)


# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Parameters matching create_batches.py
NUM_RATERS = 12
NUM_TASKS = 120 # Should match the number of tasks in master file
TASKS_PER_RATER = 20
RATERS_PER_TASK = 2
MAX_TURNS = 10 # From start_project.py, influences turn_dialogue creation

# File/Directory Paths
MASTER_FILE = Path("data/batches/master_sample_file.json")
ANNOTATIONS_DIR = Path("data/annotator_exports/round two annotations")
BATCH_DIR = Path("data/batches") # Corrected Path for batch files
OUTPUT_DIR = Path("data/rater_agreement") # Output directory for report
REPORT_FILE = OUTPUT_DIR / "completeness_report.csv" # CSV report file path

# Rater Name Mapping (Corrected based on user feedback)
# Indices correspond to rater_id (0-11) used in BatchCreator
# Rater ID = batch number - 1
RATER_NAME_MAP = {
    0: 'Ahmet',      # batch_1
    1: 'Anka',       # batch_2
    2: 'Cedric',     # batch_3
    3: 'Zoey',       # batch_4 (Corrected: Was Dayeon)
    4: 'Megan',      # batch_5
    5: 'Niloofar',   # batch_6
    6: 'Shayne',     # batch_7
    7: 'Victor',     # batch_8
    8: 'Wenting',    # batch_9
    9: 'Yuntian',    # batch_10
    10: 'Zhiping',   # batch_11
    11: 'ZSuperhero' # batch_12
}
# --- End Configuration ---


def get_expected_assignments_from_batches(batch_dir: Path, rater_map: Dict[int, str]) -> Dict[str, Set[str]]:
    """Generates the expected assignments by reading batch files."""
    logging.info(f"Generating expected task assignments by reading batch files from: {batch_dir}")
    task_to_expected_raters = defaultdict(set)
    processed_batches = 0

    if not batch_dir.is_dir():
        logging.error(f"Batch directory not found: {batch_dir}")
        return {}

    for filename in os.listdir(batch_dir):
        if filename.lower().startswith('batch_') and filename.lower().endswith('.json'):
            filepath = batch_dir / filename
            try:
                # Extract batch number to get rater ID
                batch_num_str = filename.lower().split('_')[-1].split('.')[0]
                batch_num = int(batch_num_str)
                rater_id = batch_num - 1 # Rater ID is 0-indexed
                annotator_name = rater_map.get(rater_id)

                if annotator_name is None:
                    logging.warning(f"Could not map batch number {batch_num} (from {filename}) to a rater name. Skipping file.")
                    continue

                with open(filepath, 'r', encoding='utf-8') as f:
                    batch_tasks = json.load(f)
                    if not isinstance(batch_tasks, list):
                        logging.warning(f"Expected a list in batch file {filename}. Skipping.")
                        continue

                    for task in batch_tasks:
                        if isinstance(task, dict):
                            task_id = task.get('id') # Assuming ID is conv_XXXX format here
                            if task_id:
                                task_to_expected_raters[task_id].add(annotator_name)
                            else:
                                logging.warning(f"Task missing 'id' in batch file {filename}.")
                    processed_batches += 1
                    logging.debug(f"Processed batch file {filename} for annotator {annotator_name}")

            except (ValueError, IndexError) as e:
                logging.warning(f"Could not parse batch number from filename {filename}: {e}")
            except json.JSONDecodeError as e:
                logging.error(f"Error decoding JSON from batch file {filepath}: {e}")
            except Exception as e:
                logging.error(f"Error processing batch file {filepath}: {e}")

    logging.info(f"Successfully generated expected assignments from {processed_batches} batch files.")
    return dict(task_to_expected_raters)


def load_master_tasks(filepath: Path) -> Dict[str, Dict]:
    """Loads master tasks and maps task ID to task data."""
    if not filepath.exists():
        logging.error(f"Master file not found: {filepath}")
        return {}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            master_data_list = json.load(f) # Assumes master file is a list
        
        master_tasks = {}
        for idx, task_data in enumerate(master_data_list):
             # Assuming the original master file doesn't have top-level 'id' yet
             # The 'id' used in batches is the 'conversation_id'
             task_id = task_data.get('data', {}).get('conversation_id')
             if task_id:
                master_tasks[task_id] = {
                    'data': task_data.get('data', {}),
                    'original_index': idx # Store original index if needed for assignment mapping
                }
             else:
                 logging.warning(f"Task at index {idx} in master file is missing 'conversation_id'.")
        logging.info(f"Loaded {len(master_tasks)} tasks from master file: {filepath}")
        return master_tasks
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON from master file {filepath}: {e}")
        return {}
    except Exception as e:
        logging.error(f"Error reading master file {filepath}: {e}")
        return {}


def get_available_annotators(annotations_dir: Path) -> Dict[str, Path]:
    """Finds available .json export files and maps annotator name to filepath."""
    available_files = {}
    if not annotations_dir.is_dir():
        logging.error(f"Annotations directory not found: {annotations_dir}")
        return {}

    for filename in os.listdir(annotations_dir):
        if filename.lower().endswith('.json'):
            annotator_name = os.path.splitext(filename)[0]
            # Normalize name for matching (e.g., handle case sensitivity if needed)
            normalized_name = annotator_name.lower()
            
            # Find if this name matches any in our RATER_NAME_MAP values
            matched = False
            for rater_id, name in RATER_NAME_MAP.items():
                if name.lower() == normalized_name:
                     available_files[name] = annotations_dir / filename
                     matched = True
                     break
            if not matched:
                 logging.warning(f"Found export file '{filename}' but annotator name '{annotator_name}' not in RATER_NAME_MAP. Skipping.")

        elif filename != '.DS_Store':
            logging.warning(f"Skipping non-JSON file in annotations dir: {filename}")

    logging.info(f"Found {len(available_files)} relevant annotator export files.")
    return available_files


def process_annotation_file(filepath: Path, annotator_name: str) -> Dict[str, Dict]:
    """Processes a single annotator's export file."""
    processed_data = {} # task_id -> {annotator, selected_turns}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                tasks = json.load(f)
            except json.JSONDecodeError:
                logging.warning(f"Standard JSON decode failed for {filepath.name}. Trying JSON Lines.")
                f.seek(0)
                tasks = [json.loads(line) for line in f if line.strip()]

        if not isinstance(tasks, list):
            logging.warning(f"Expected a list of tasks in {filepath.name}, got {type(tasks)}. Skipping file.")
            return {}

        logged_ids_count = 0 # Debug: Counter for logged IDs per file
        for task in tasks:
            if not isinstance(task, dict):
                logging.warning(f"Skipping non-dictionary item in {filepath.name}")
                continue

            # task_id_internal = task.get('id') # This is the Label Studio internal ID (integer)
            task_data = task.get('data', {})
            original_task_id = task_data.get('conversation_id') # This is the stable 'conv_XXXX' ID

            if not original_task_id:
                # Try to get internal ID for logging purposes if original is missing
                task_id_internal = task.get('id', 'UNKNOWN_INTERNAL_ID') 
                logging.warning(f"Skipping task with missing 'conversation_id' in data field (Internal ID: {task_id_internal}) in {filepath.name}")
                continue
            
            # Convert task_id to the format "conv_XXXX" (string with leading zeros)
            # try:
            #     task_id_str = f"conv_{int(task_id):04d}"
            # except (ValueError, TypeError):
            #      logging.warning(f"Could not convert task ID '{task_id}' (type: {type(task_id)}) to integer format in {filepath.name}. Skipping.")
            #      continue

            # Debug: Log first few task IDs found in the file
            if logged_ids_count < 3:
                # Use internal ID for debug log if needed, but original_task_id is the key
                task_id_internal = task.get('id', 'N/A') 
                logging.debug(f"[Debug {filepath.name}] Found Original Task ID: {original_task_id} (Internal LS ID: {task_id_internal})")
                logged_ids_count += 1

            # Extract selected turns from the *first* annotation result found
            selected_turns = set()
            annotations = task.get('annotations', [])
            if annotations and isinstance(annotations, list) and len(annotations) > 0:
                 annotation_result = annotations[0].get('result', [])
                 # Find the 'turn_selector' choices within the result list
                 for result_item in annotation_result:
                     if isinstance(result_item, dict) and result_item.get('from_name') == 'turn_selector':
                         choices = result_item.get('value', {}).get('choices', [])
                         # Extract turn number, assuming format "Turn X"
                         for choice in choices:
                             try:
                                 turn_num = int(choice.split()[-1])
                                 selected_turns.add(turn_num)
                             except (ValueError, IndexError):
                                 logging.warning(f"Could not parse turn number from choice '{choice}' in task {original_task_id}, file {filepath.name}")
                         break # Assume only one turn_selector per annotation

            processed_data[original_task_id] = { # Use the ORIGINAL string ID from data
                "annotator": annotator_name,
                "selected_turns": selected_turns
            }

    except Exception as e:
        logging.error(f"Error processing file {filepath}: {e}")

    return processed_data

def get_max_turns_for_task(task_data: Dict) -> int:
     """Calculate the maximum theoretical turns from conversation data."""
     conversation = task_data.get('conversation', [])
     if not conversation:
         return 0
     # Each pair of User/LLM is a turn. Round up for the last user message.
     return (len(conversation) + 1) // 2


def check_completeness():
    """Main function to check and report completeness."""
    logging.info("--- Starting Completeness Check ---")

    # 1. Load Master Tasks
    master_tasks = load_master_tasks(MASTER_FILE)
    if not master_tasks:
        return
    num_tasks_actual = len(master_tasks)
    # Create a mapping from original_index back to task_id for assignment lookup
    # index_to_taskid = {v['original_index']: k for k, v in master_tasks.items()}


    # 2. Get Expected Raters for each task index - NEW METHOD
    # expected_raters_by_index = get_expected_assignments(num_tasks_actual)
    # if not expected_raters_by_index:
    #      return
    # # Map expected raters to task_id
    # expected_raters_by_taskid = defaultdict(set)
    # for index, rater_ids in expected_raters_by_index.items():
    #     task_id = index_to_taskid.get(index)
    #     if task_id:
    #          expected_raters_by_taskid[task_id] = {RATER_NAME_MAP[r_id] for r_id in rater_ids}
    #     else:
    #          logging.warning(f"Could not map task index {index} back to a task ID.")
    expected_raters_by_taskid = get_expected_assignments_from_batches(BATCH_DIR, RATER_NAME_MAP)
    if not expected_raters_by_taskid:
        logging.error("Failed to determine expected assignments from batch files.")
        return

    # 3. Get Available Annotator Files
    available_annotators_files = get_available_annotators(ANNOTATIONS_DIR)
    available_annotator_names = set(available_annotators_files.keys())
    logging.info(f"Available annotators based on export files: {', '.join(sorted(available_annotator_names))}")


    # 4. Process Actual Annotations
    actual_annotations = defaultdict(dict) # task_id -> {annotator_name: {selected_turns}}
    for name, filepath in available_annotators_files.items():
        logging.info(f"Processing annotations for: {name} ({filepath.name})")
        annotator_data = process_annotation_file(filepath, name)
        for task_id, data in annotator_data.items():
            if task_id in actual_annotations:
                 actual_annotations[task_id][name] = data # Store annotator's specific data
            else:
                 actual_annotations[task_id] = {name: data}


    # 5. Compare and Report
    logging.info("--- Completeness Report ---")
    missing_annotator_count = 0
    missing_turns_count = 0
    fully_complete_count = 0
    report_data = [] # Store data for CSV
    csv_headers = [
        "Task ID", "Expected Annotators", "Actual Annotators Found", 
        "Annotator Status", "Annotator 1", "Annotator 1 Turn Status",
        "Annotator 2", "Annotator 2 Turn Status"
    ]

    # Iterate through master tasks to ensure all 120 are checked
    for task_id, master_task_info in sorted(master_tasks.items()): # Sort by task_id for report
        expected = expected_raters_by_taskid.get(task_id, set())
        actual_data = actual_annotations.get(task_id, {}) # Dict of {annotator: {selected_turns}}
        actual_annotators_found = set(actual_data.keys())

        report_line = f"Task ID: {task_id}\n"
        report_line += f"  Expected Annotators: {', '.join(sorted(expected)) if expected else 'N/A'}\n"
        report_line += f"  Actual Annotators Found: {', '.join(sorted(actual_annotators_found)) if actual_annotators_found else 'None'}\n"

        # Annotator Completeness Status
        annotator_status = "Error: No expected annotators"
        missing_annotators_for_task = expected - actual_annotators_found
        
        if not expected:
             annotator_status = "Error: No expected annotators determined"
        elif len(missing_annotators_for_task) == 0:
            annotator_status = "Annotators Complete"
        elif len(missing_annotators_for_task) == len(expected):
             annotator_status = f"Annotators Missing Both ({', '.join(sorted(missing_annotators_for_task))})"
             missing_annotator_count += 1
        else:
            annotator_status = f"Annotator Missing: {', '.join(sorted(missing_annotators_for_task))}"
            missing_annotator_count += 1
            
        report_line += f"  Annotator Status: {annotator_status}\n"

        # Turn Completeness Status (for each actual annotator)
        max_turns_in_conv = get_max_turns_for_task(master_task_info.get('data', {}))
        all_turns_expected = set(range(1, max_turns_in_conv + 1))
        task_fully_complete = (len(missing_annotators_for_task) == 0) # Start assuming complete

        if not actual_annotators_found:
             report_line += "  Turn Status: No annotations found to check turns.\n"
             if expected: # If we expected annotators but found none
                  task_fully_complete = False
             annotator1_name, annotator1_status = "", "No annotations found"
             annotator2_name, annotator2_status = "", ""
        else:
            annotator_turn_statuses = {}
            for annotator_name, annotation_data in actual_data.items():
                selected = annotation_data.get('selected_turns', set())
                missing_turns = all_turns_expected - selected
                turn_status = ""
                if not all_turns_expected:
                     turn_status = " (No turns in original data)"
                elif not selected and all_turns_expected:
                     turn_status = " - Missing ALL Turns"
                     missing_turns_count +=1
                     task_fully_complete = False
                elif missing_turns:
                    turn_status = f" - Missing Turns: {sorted(list(missing_turns))}"
                    missing_turns_count += 1
                    task_fully_complete = False
                else:
                    turn_status = "Turns Complete"
                report_line += f"    - {annotator_name}: {turn_status}\n"
                annotator_turn_statuses[annotator_name] = turn_status

            # Prepare turn status for CSV (max 2 annotators)
            actual_list = sorted(list(actual_annotators_found))
            annotator1_name = actual_list[0] if len(actual_list) > 0 else ""
            annotator1_status = annotator_turn_statuses.get(annotator1_name, "Status N/A")
            annotator2_name = actual_list[1] if len(actual_list) > 1 else ""
            annotator2_status = annotator_turn_statuses.get(annotator2_name, "") if annotator2_name else ""
        
        if task_fully_complete:
             fully_complete_count +=1

        # Store row for CSV report
        report_data.append([
            task_id,
            ", ".join(sorted(expected)) if expected else "N/A",
            ", ".join(sorted(actual_annotators_found)) if actual_annotators_found else "None",
            annotator_status,
            annotator1_name,
            annotator1_status,
            annotator2_name,
            annotator2_status
        ])

    # Write CSV Report
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True) # Ensure dir exists
    try:
        with open(REPORT_FILE, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(csv_headers)
            writer.writerows(report_data)
        logging.info(f"Successfully wrote completeness report to {REPORT_FILE}")
    except Exception as e:
        logging.error(f"Error writing CSV report to {REPORT_FILE}: {e}")

    logging.info("--- Summary ---")
    logging.info(f"Total Tasks Checked: {num_tasks_actual}")
    logging.info(f"Tasks Fully Complete (Correct Annotators + All Turns): {fully_complete_count}")
    logging.info(f"Tasks with Missing Annotators: {missing_annotator_count}")
    logging.info(f"Tasks with Missing Turns (by any present annotator): {missing_turns_count}")
    logging.info("--- Check Complete ---")


if __name__ == "__main__":
    check_completeness() 