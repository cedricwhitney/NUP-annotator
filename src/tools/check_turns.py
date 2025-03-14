import json
import sys

def check_turns(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    print(f"Number of tasks: {len(data)}")
    
    for i, task in enumerate(data[:5]):  # Check first 5 tasks
        turns = len([k for k in task['data'].keys() if k.startswith('turn')])
        msgs = len(task['data']['conversation'])
        print(f"Task {i+1}: {turns} turns, {msgs} messages")
        
        # Print the keys to see what turns exist
        turn_keys = [k for k in task['data'].keys() if k.startswith('turn')]
        print(f"  Turn keys: {turn_keys}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        check_turns(sys.argv[1])
    else:
        print("Usage: python check_turns.py <transformed_file>")
        print("Example: python check_turns.py data/batch_1_transformed.json") 