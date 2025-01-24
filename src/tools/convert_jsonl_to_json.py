import json

def convert_jsonl_to_json(input_file, output_file):
    """Convert JSONL file to Label Studio JSON format."""
    tasks = []
    with open(input_file, 'r') as f:
        for line in f:
            task = json.loads(line)
            # Convert to Label Studio format
            label_studio_task = {
                "data": {
                    "conversation": task["conversation"]
                }
            }
            tasks.append(label_studio_task)
    
    with open(output_file, 'w') as f:
        json.dump(tasks, f, indent=2)

if __name__ == "__main__":
    convert_jsonl_to_json('data/cedric_120_sample.jsonl', 'data/your_tasks.json') 