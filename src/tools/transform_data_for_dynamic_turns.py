import json
import sys
from pathlib import Path
from typing import List, Dict, Any

def load_master_conversation_ids(master_file: str = "data/master_sample_file.json") -> Dict[str, str]:
    """
    Load conversation IDs from the master file.
    
    Returns:
        Dict mapping conversation text to conversation IDs
    """
    try:
        with open(master_file, 'r', encoding='utf-8', newline='') as f:
            master_data = json.load(f)
            
        # Create a mapping of conversation text to conversation ID
        conv_map = {}
        for conv in master_data:
            if "data" in conv and "conversation" in conv["data"]:
                # Create a key from the conversation text
                conv_key = json.dumps([msg.get("text", "") for msg in conv["data"]["conversation"]], sort_keys=True)
                conv_map[conv_key] = conv["data"].get("conversation_id")
        
        return conv_map
    except Exception as e:
        print(f"⚠️ Warning: Could not load master conversation IDs: {e}")
        return {}

def transform_data(input_file: str, output_file: str, max_turns: int = 10):
    """
    Transform conversation data to include turn-specific dialogue fields for Label Studio.
    
    Args:
        input_file: Path to the input JSON file with conversation data
        output_file: Path to save the transformed data
        max_turns: Maximum number of turns to support
    
    Returns:
        bool: True if successful, False otherwise
    """
    print(f"🔍 Reading input file: {input_file}")
    
    try:
        # Load master conversation IDs
        master_conv_ids = load_master_conversation_ids()
        
        with open(input_file, 'r', encoding='utf-8', newline='') as f:
            tasks = json.load(f)
        
        if not isinstance(tasks, list):
            print("❌ Input must be a list of tasks")
            return False
        
        transformed_tasks = []
        
        for i, task in enumerate(tasks):
            # Check for data wrapper
            if not isinstance(task, dict) or "data" not in task:
                print(f"❌ Task {i}: Missing 'data' wrapper")
                return False
            
            # Check conversation field exists and is a list
            if "conversation" not in task["data"] or not isinstance(task["data"]["conversation"], list):
                print(f"❌ Task {i}: Missing or invalid 'conversation' field")
                return False
            
            # Get the conversation
            conversation = task["data"]["conversation"]
            
            # Create a new task with turn-specific dialogue fields
            new_task = {
                "data": {
                    "conversation": [],
                }
            }
            
            # Try to find the conversation ID from the master file
            conv_key = json.dumps([msg.get("text", "") for msg in conversation], sort_keys=True)
            conversation_id = master_conv_ids.get(conv_key)
            
            if conversation_id:
                new_task["id"] = conversation_id
                new_task["data"]["conversation_id"] = conversation_id
            else:
                # Fallback to the old ID generation if no match found
                if "id" in task:
                    new_task["id"] = task["id"]
                else:
                    base_filename = Path(input_file).stem
                    new_task["id"] = f"{base_filename}_{i+1}"
            
            # Add original_task_id for reference
            new_task["data"]["original_task_id"] = new_task["id"]
            
            # Process each message in the conversation to preserve formatting and standardize roles
            for idx, msg in enumerate(conversation):
                # Create a deep copy to avoid modifying the original
                processed_msg = msg.copy()
                
                # Standardize role names
                if idx % 2 == 0:  # Even indices (0, 2, 4...) are user messages
                    processed_msg["role"] = "User"
                else:  # Odd indices (1, 3, 5...) are LLM responses
                    processed_msg["role"] = "LLM"
                
                new_task["data"]["conversation"].append(processed_msg)
            
            # Calculate the actual number of turns in this conversation
            # Each turn consists of a user message and an assistant response
            actual_turns = (len(conversation) + 1) // 2  # Round up to include partial turns
            actual_turns = min(actual_turns, max_turns)
            
            # Add turn-specific dialogue fields only for the turns that exist
            for turn_idx in range(actual_turns):
                # Each turn consists of a user message and an assistant response
                # So we need to get 2 messages for each turn
                start_idx = turn_idx * 2
                end_idx = min(start_idx + 2, len(conversation))  # Don't go beyond the conversation length
                
                # Get the messages for this turn
                turn_dialogue = []
                for idx in range(start_idx, end_idx):
                    # Create a deep copy to avoid modifying the original
                    msg = conversation[idx].copy()
                    
                    # Standardize role names
                    if (idx - start_idx) % 2 == 0:  # First message in the turn is user
                        msg["role"] = "User"
                    else:  # Second message in the turn is LLM
                        msg["role"] = "LLM"
                    
                    turn_dialogue.append(msg)
                
                # Skip this turn if both messages are empty or don't exist
                if len(turn_dialogue) == 0:
                    continue
                
                # If we only have one message for this turn (e.g., the last user message without a response)
                if len(turn_dialogue) == 1:
                    turn_dialogue.append({"role": "LLM", "text": "", "content": ""})
                
                # Ensure each turn has the right fields (text or content)
                has_content = False
                for msg in turn_dialogue:
                    # If the message has 'content' but not 'text', copy content to text
                    if "content" in msg and "text" not in msg:
                        msg["text"] = msg["content"]
                        if msg["content"]:
                            has_content = True
                    # If the message has 'text' but not 'content', copy text to content
                    elif "text" in msg and "content" not in msg:
                        msg["content"] = msg["text"]
                        if msg["text"]:
                            has_content = True
                    # If neither exists, add empty strings for both
                    elif "text" not in msg and "content" not in msg:
                        msg["text"] = ""
                        msg["content"] = ""
                    # If both exist, check if either has content
                    else:
                        if msg["text"] or msg["content"]:
                            has_content = True
                
                # Only add the turn if it has actual content
                if has_content:
                    new_task["data"][f"turn{turn_idx+1}_dialogue"] = turn_dialogue
            
            transformed_tasks.append(new_task)
        
        # Save the transformed data with proper encoding to preserve formatting
        print(f"💾 Saving transformed data to: {output_file}")
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            json.dump(transformed_tasks, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Successfully transformed {len(transformed_tasks)} tasks")
        return True
        
    except Exception as e:
        print(f"❌ Error transforming data: {e}")
        return False

def main():
    if len(sys.argv) < 3:
        print("Usage: python transform_data_for_dynamic_turns.py <input_file> <output_file> [max_turns]")
        print("Example: python transform_data_for_dynamic_turns.py data/batch_1.json data/batch_1_transformed.json 10")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    max_turns = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    
    if transform_data(input_file, output_file, max_turns):
        print("\n📋 Next steps:")
        print(f"1. Use the transformed file ({output_file}) with Label Studio")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main() 