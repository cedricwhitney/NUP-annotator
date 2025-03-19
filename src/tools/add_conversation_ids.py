import json
from pathlib import Path

def add_conversation_ids(master_file: str):
    """
    Add unique conversation IDs to the master sample file.
    
    Args:
        master_file: Path to the master sample file
    """
    print(f"🔍 Reading master file: {master_file}")
    
    try:
        with open(master_file, 'r', encoding='utf-8', newline='') as f:
            conversations = json.load(f)
        
        if not isinstance(conversations, list):
            print("❌ Input must be a list of conversations")
            return False
        
        # Add unique IDs to each conversation
        for i, conv in enumerate(conversations):
            if not isinstance(conv, dict) or "data" not in conv:
                print(f"❌ Conversation {i}: Missing 'data' wrapper")
                return False
            
            # Create a unique conversation ID
            conv_id = f"conv_{i+1:04d}"  # This will create IDs like conv_0001, conv_0002, etc.
            
            # Add the conversation ID only to the data section
            conv["data"]["conversation_id"] = conv_id
            
            # Remove any root-level conversation_id if it exists
            if "conversation_id" in conv:
                del conv["conversation_id"]
        
        # Save back to the same file
        print(f"💾 Saving updated master file")
        with open(master_file, 'w', encoding='utf-8', newline='') as f:
            json.dump(conversations, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Successfully added IDs to {len(conversations)} conversations")
        return True
        
    except Exception as e:
        print(f"❌ Error adding conversation IDs: {e}")
        return False

def main():
    master_file = "data/master_sample_file.json"
    
    if add_conversation_ids(master_file):
        print("\n📋 Next steps:")
        print("1. Run create_batches.py to create new batch files with the updated IDs")
    else:
        print("❌ Failed to add conversation IDs")

if __name__ == "__main__":
    main() 