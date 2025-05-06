import json
import os
from collections import defaultdict
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define paths
INPUT_DIR = Path('data/annotator_exports/round two annotations')
OUTPUT_DIR = Path('data/rater_agreement')
OUTPUT_FILE = OUTPUT_DIR / 'agreement_tasks.json'

# Ensure output directory exists
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def extract_annotator_name(filename):
    """Extracts the annotator name from the filename (e.g., 'megan.json' -> 'megan')."""
    return os.path.splitext(filename)[0]

def package_annotations():
    """Packages annotations from multiple files, adding annotator info and filtering."""
    aggregated_tasks = defaultdict(lambda: {'data': None, 'annotations': []})

    if not os.path.exists(INPUT_DIR):
        logging.error(f"Input directory not found: {INPUT_DIR}")
        return

    logging.info(f"Scanning directory: {INPUT_DIR}")
    found_files = False
    all_task_ids_found = set() # Set to store all unique IDs encountered

    for filename in os.listdir(INPUT_DIR):
        if filename.endswith('.json'):
            found_files = True
            annotator_name = extract_annotator_name(filename)
            filepath = os.path.join(INPUT_DIR, filename)
            logging.info(f"Processing file: {filepath} for annotator: {annotator_name}")

            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    # Handle potential multiple JSON objects or non-standard formats if necessary
                    # For now, assume it's a list of task objects
                    try:
                        tasks = json.load(f)
                    except json.JSONDecodeError as e:
                         # Attempt to load JSON Lines format if standard JSON fails
                        logging.warning(f"Standard JSON decode failed for {filename}: {e}. Trying JSON Lines.")
                        f.seek(0) # Reset file pointer
                        tasks = [json.loads(line) for line in f if line.strip()]


                if not isinstance(tasks, list):
                    logging.warning(f"Expected a list of tasks in {filename}, but got {type(tasks)}. Skipping file.")
                    continue

                for task in tasks:
                    if not isinstance(task, dict):
                        logging.warning(f"Skipping non-dictionary item in {filename}: {task}")
                        continue

                    # Use original conversation_id from data field as the key
                    task_data = task.get('data', {})
                    task_id = task_data.get('conversation_id')
                    # internal_ls_id = task.get('id') # Keep track if needed for debugging

                    if task_id is None:
                        internal_ls_id = task.get('id', 'UNKNOWN_INTERNAL_ID')
                        logging.warning(f"Skipping task with missing 'conversation_id' in data (Internal ID: {internal_ls_id}) in {filename}")
                        continue

                    all_task_ids_found.add(task_id) # Add ID to the set

                    # Store data if not already stored (assuming data is consistent for the same task id)
                    if aggregated_tasks[task_id]['data'] is None and task_data:
                        aggregated_tasks[task_id]['data'] = task_data

                    # Process annotations for this task
                    task_annotations = task.get('annotations', []) # Get annotations for the current task
                    for annotation_set in task_annotations: # Iterate over the correct variable
                         if isinstance(annotation_set, dict):
                            # Add annotator name to each result within the annotation set
                            results = annotation_set.get('result', [])
                            completed_by = annotation_set.get('completed_by') # Preserve original completed_by if needed

                            modified_annotation = {
                                'result': results,
                                'annotator': annotator_name,
                                'original_completed_by': completed_by # Optional: keep original ID
                            }
                            aggregated_tasks[task_id]['annotations'].append(modified_annotation)
                         else:
                            logging.warning(f"Unexpected annotation format in task {task_id} from {filename}. Expected dict, got {type(annotation_set)}.")


            except json.JSONDecodeError as e:
                logging.error(f"Error decoding JSON from {filepath}: {e}")
            except Exception as e:
                logging.error(f"An unexpected error occurred processing {filepath}: {e}")
        elif filename != '.DS_Store':
             logging.warning(f"Skipping non-JSON file: {filename}")


    if not found_files:
        logging.error(f"No JSON files found in {INPUT_DIR}")
        return

    logging.info(f"Verification count: Found {len(all_task_ids_found)} unique task IDs across all processed files.")

    # Filter tasks: keep only those with annotations from at least two annotators
    packaged_annotations = []
    annotator_counts = defaultdict(set)
    for task_id, task_info in aggregated_tasks.items():
        for ann in task_info['annotations']:
            annotator_counts[task_id].add(ann.get('annotator')) # Use set to count unique annotators

    logging.info(f"Found {len(aggregated_tasks)} unique task IDs.")

    for task_id, task_info in aggregated_tasks.items():
        unique_annotators_count = len(annotator_counts[task_id])
        # Filter for tasks with exactly 2 unique annotators
        if unique_annotators_count == 2: 
            final_task = {
                'id': task_id, # Use the conversation_id
                'data': task_info['data'],
                'annotations': task_info['annotations'] # Contains all annotations from all annotators for this task
            }
            packaged_annotations.append(final_task)
        # else:
            # logging.debug(f"Task {task_id} skipped, only {unique_annotators_count} unique annotator(s).")


    logging.info(f"Packaged {len(packaged_annotations)} tasks with annotations from 2 or more annotators.")

    # Write the packaged annotations to the output file
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(packaged_annotations, f, indent=4, ensure_ascii=False)
        logging.info(f"Successfully wrote packaged annotations to {OUTPUT_FILE}")
    except Exception as e:
        logging.error(f"Error writing output file {OUTPUT_FILE}: {e}")

if __name__ == "__main__":
    package_annotations() 