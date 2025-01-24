import os
import json
import sys
from typing import List, Dict, Any

def validate_and_fix_json(input_file: str, output_file: str = None) -> bool:
    """Validate and optionally fix JSON format for Label Studio.
    
    Returns:
        bool: True if file is valid (or fixable), False if invalid format
    """
    print(f"🔍 Validating {input_file}")
    
    try:
        with open(input_file, 'r') as f:
            tasks = json.load(f)
        
        if not isinstance(tasks, list):
            print("❌ Root must be a list of tasks")
            return False
            
        has_issues = False
        for i, task in enumerate(tasks):
            # Check for data wrapper
            if not isinstance(task, dict) or "data" not in task:
                print(f"❌ Task {i}: Missing 'data' wrapper")
                return False
            
            # Check conversation field exists and is a list
            if "conversation" not in task["data"] or not isinstance(task["data"]["conversation"], list):
                print(f"❌ Task {i}: Missing or invalid 'conversation' field")
                return False
            
            # Check each turn in conversation
            for j, turn in enumerate(task["data"]["conversation"]):
                if not isinstance(turn, dict):
                    print(f"❌ Task {i}, Turn {j}: Must be a dictionary")
                    return False
                    
                if "role" not in turn or "text" not in turn:
                    print(f"❌ Task {i}, Turn {j}: Missing required fields 'role' and/or 'text'")
                    return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error validating JSON: {e}")
        return False

def fix_task(task: Dict[str, Any], index: int) -> tuple[Dict[str, Any], bool]:
    """Fix a single task's format if possible.
    
    Returns:
        tuple: (fixed_task, was_fixed) or (None, False) if unfixable
    """
    fixed = False
    
    # Check basic structure
    if not isinstance(task, dict):
        print(f"❌ Task {index} must be a dictionary")
        return None, False
    
    # Ensure 'data' field exists
    if 'data' not in task:
        print(f"⚠️ Task {index}: Adding missing 'data' field")
        task = {'data': task}
        fixed = True
    
    # Check conversation structure
    if 'conversation' not in task['data']:
        # Try to detect and fix conversation data
        if any(isinstance(v, list) for v in task['data'].values()):
            # Find the first list that looks like conversation data
            for key, value in task['data'].items():
                if isinstance(value, list) and all(isinstance(t, dict) for t in value):
                    print(f"⚠️ Task {index}: Moving '{key}' to 'conversation' field")
                    task['data']['conversation'] = value
                    fixed = True
                    break
        if 'conversation' not in task['data']:
            print(f"❌ Task {index}: Cannot find conversation data")
            return None, False
    
    # Validate conversation turns
    conv = task['data']['conversation']
    if not isinstance(conv, list):
        print(f"❌ Task {index}: Conversation must be a list")
        return None, False
    
    fixed_conv = []
    for j, turn in enumerate(conv):
        if not isinstance(turn, dict):
            print(f"❌ Task {index}, Turn {j}: Must be a dictionary")
            return None, False
        
        # Fix missing or renamed fields
        fixed_turn = {}
        if 'text' not in turn:
            # Try common alternatives
            for alt in ['message', 'content', 'utterance']:
                if alt in turn:
                    print(f"⚠️ Task {index}, Turn {j}: Renaming '{alt}' to 'text'")
                    fixed_turn['text'] = turn[alt]
                    fixed = True
                    break
            if 'text' not in fixed_turn:
                print(f"❌ Task {index}, Turn {j}: Missing 'text' field")
                return None, False
        else:
            fixed_turn['text'] = turn['text']
        
        if 'role' not in turn:
            # Try common alternatives
            for alt in ['speaker', 'participant', 'author']:
                if alt in turn:
                    print(f"⚠️ Task {index}, Turn {j}: Renaming '{alt}' to 'role'")
                    fixed_turn['role'] = turn[alt]
                    fixed = True
                    break
            if 'role' not in fixed_turn:
                print(f"❌ Task {index}, Turn {j}: Missing 'role' field")
                return None, False
        else:
            fixed_turn['role'] = turn['role']
        
        fixed_conv.append(fixed_turn)
    
    task['data']['conversation'] = fixed_conv
    return task, fixed

def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_labelstudio_json.py input.json [output.json]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    success = validate_and_fix_json(input_file, output_file)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 