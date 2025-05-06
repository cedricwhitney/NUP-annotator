import json
import os
from collections import defaultdict

def load_json_file(filepath):
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {filepath}: {str(e)}")
        return None

def count_turns_in_conversation(conversation):
    if not conversation:
        return 0
    # Each turn consists of a user message followed by an assistant message
    # So the number of turns is the total messages divided by 2 (rounded up)
    return (len(conversation) + 1) // 2

def analyze_annotations(annotator_name, data):
    if not data:
        print(f"No data found for {annotator_name}")
        return
    
    print(f"\nAnalyzing annotations for {annotator_name}...")
    
    # Track annotations per task
    task_turns = defaultdict(set)
    task_total_turns = {}
    
    # First pass: collect all annotations and count actual turns
    for item in data:
        task_id = item.get('id')
        if not task_id:
            print(f"Warning: Found item without task ID in {annotator_name}'s data")
            continue
            
        print(f"\nProcessing task {task_id}:")
        
        # Get conversation data to count actual turns
        conversation = item.get('data', {}).get('conversation', [])
        actual_turns = count_turns_in_conversation(conversation)
        task_total_turns[task_id] = actual_turns
        print(f"Task {task_id} has {actual_turns} actual turns")
        
        annotations = item.get('annotations', [])
        if not annotations:
            print(f"Warning: Task {task_id} has no annotations")
            continue
        
        print(f"Found {len(annotations)} annotation(s)")
        for annotation_idx, annotation in enumerate(annotations):
            results = annotation.get('result', [])
            
            for result in results:
                value = result.get('value', {})
                from_name = result.get('from_name', '')
                
                if 'choices' in value:
                    choices = value['choices']
                    if any(choice.startswith('Turn ') for choice in choices):
                        try:
                            turn_num = int(next(choice.split(' ')[1] for choice in choices if choice.startswith('Turn ')))
                            if turn_num <= actual_turns:  # Only count turns that actually exist
                                task_turns[task_id].add(turn_num)
                                print(f"Found valid turn {turn_num}")
                            else:
                                print(f"Warning: Turn {turn_num} marked but conversation only has {actual_turns} turns")
                        except (ValueError, IndexError) as e:
                            print(f"Warning: Invalid turn number format in task {task_id}: {choices}")
    
    # Analyze completeness
    incomplete_tasks = []
    for task_id, turns in task_turns.items():
        actual_turns = task_total_turns[task_id]
        # Only include turns that exist and are less than 10
        expected_turns = set(range(1, min(10, actual_turns + 1)))  # Changed from 11 to 10 to not include turn 10
        missing_turns = expected_turns - turns
        if missing_turns:
            incomplete_tasks.append((task_id, missing_turns, actual_turns))
            print(f"\nTask {task_id} ({actual_turns} total turns):")
            print(f"Missing turns: {sorted(missing_turns)}")
            print(f"Annotated turns: {sorted(turns)}")
    
    if incomplete_tasks:
        print(f"\n{annotator_name} has {len(incomplete_tasks)} incomplete tasks:")
        total_missing = sum(len(missing) for _, missing, _ in incomplete_tasks)
        print(f"Total missing turns: {total_missing}")
        for task_id, missing, actual_turns in incomplete_tasks:
            print(f"Task {task_id} ({actual_turns} total turns): Missing {len(missing)} turns - {sorted(missing)}")
    else:
        print(f"\n{annotator_name} has completed all tasks!")

def main():
    annotations_dir = "annotator_exports/round two annotations"
    annotator = "zhiping"  # Check Zhiping's annotations
    
    json_file = os.path.join(annotations_dir, f"{annotator}.json")
    if not os.path.exists(json_file):
        print(f"Error: File not found - {json_file}")
        return
        
    print(f"Loading annotations from {json_file}...")
    data = load_json_file(json_file)
    analyze_annotations(annotator, data)

if __name__ == "__main__":
    main() 