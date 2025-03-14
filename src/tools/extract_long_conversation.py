#!/usr/bin/env python3
import json
import os
from pathlib import Path

def extract_longest_conversation(file_path):
    """Extract and display the conversation with the most turns."""
    print(f"Analyzing file: {file_path}")
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found")
        return
    
    # Load the JSON data
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print(f"Error: {file_path} is not a valid JSON file")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    # Find the conversation with the most turns
    max_turns = 0
    max_turns_idx = -1
    
    for i, task in enumerate(data):
        turns = (len(task['data']['conversation']) + 1) // 2
        if turns > max_turns:
            max_turns = turns
            max_turns_idx = i
    
    if max_turns_idx == -1:
        print("No conversations found in the file")
        return
    
    # Get the conversation with the most turns
    longest_conversation = data[max_turns_idx]
    
    # Print conversation details
    print(f"\nFound conversation with {max_turns} turns (ID: {longest_conversation.get('id', 'N/A')})")
    
    # Print the conversation messages
    print("\n===== CONVERSATION WITH 72 TURNS =====\n")
    
    conversation = longest_conversation['data']['conversation']
    for i, message in enumerate(conversation):
        role = message.get('role', 'unknown')
        # Get text content, handling both direct text and content array formats
        if 'text' in message:
            text = message['text']
        elif 'content' in message and isinstance(message['content'], list):
            # Extract text from content array
            text_parts = []
            for content_item in message['content']:
                if isinstance(content_item, dict) and 'text' in content_item:
                    text_parts.append(content_item['text'])
                elif isinstance(content_item, str):
                    text_parts.append(content_item)
            text = "\n".join(text_parts)
        else:
            text = str(message.get('content', ''))
        
        # Truncate very long messages for display
        if len(text) > 500:
            text = text[:500] + "... [truncated]"
        
        turn_num = (i // 2) + 1
        if i % 2 == 0:
            print(f"\n----- TURN {turn_num} -----")
            print(f"USER: {text}\n")
        else:
            print(f"ASSISTANT: {text}\n")
    
    return longest_conversation

if __name__ == "__main__":
    # Extract the longest conversation from the sample file
    sample_file = Path("data/cedric_120_sample.json")
    extract_longest_conversation(sample_file) 