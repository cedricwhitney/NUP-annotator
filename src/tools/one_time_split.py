import json
import os
import sys
from pathlib import Path

def distribute_rows(num_annotators=12, rows_per_annotator=20):
    """
    Returns a dictionary mapping row IDs to annotator pairs.
    Each annotator gets exactly rows_per_annotator rows.
    Each row is assigned to exactly 2 annotators.
    """
    total_rows = (num_annotators * rows_per_annotator) // 2
    assignment = {}

    for i in range(total_rows):
        a = i % num_annotators
        b = (a + (i // num_annotators) + 1) % num_annotators
        assignment[i] = [a, b]

    return assignment

def split_data(input_file, output_dir="data"):
    """
    Splits input JSON file into individual files for each annotator.
    """
    if not os.path.exists(input_file):
        print(f"❌ Error: Input file '{input_file}' not found")
        sys.exit(1)

    # Read input file
    print(f"📖 Reading from {input_file}")
    with open(input_file) as f:
        data = json.load(f)
    
    # Get assignments
    assignments = distribute_rows()
    
    # Create annotator-specific files
    annotator_tasks = {i: [] for i in range(12)}
    
    # Distribute tasks according to assignments
    for row_id, annotators in assignments.items():
        if row_id >= len(data):
            break
        task = data[row_id]
        for annotator in annotators:
            annotator_tasks[annotator].append(task)
    
    # Write files
    for annotator, tasks in annotator_tasks.items():
        output_file = os.path.join(output_dir, f"batch_{annotator+1}.json")
        with open(output_file, 'w') as f:
            json.dump(tasks, f, indent=2)
        print(f"✅ Created {output_file} with {len(tasks)} tasks")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python one_time_split.py <input_json_file>")
        print("Example: python one_time_split.py data/cedric_120_sample.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    split_data(input_file) 