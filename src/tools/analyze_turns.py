#!/usr/bin/env python3
import json
import os
from collections import Counter
from pathlib import Path

def analyze_turns(file_path):
    """Analyze the number of turns in conversations from a JSON file."""
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
    
    # Calculate turns for each conversation
    # A turn consists of a user message and an assistant response
    # So we divide the total messages by 2 (rounding up for odd numbers)
    turns = [(len(task['data']['conversation']) + 1) // 2 for task in data]
    
    if not turns:
        print("No conversations found in the file")
        return
    
    # Sort turns for percentile calculations
    turns.sort()
    
    # Calculate statistics
    min_turns = min(turns)
    max_turns = max(turns)
    median_turns = turns[len(turns)//2]
    percentile_90 = turns[int(len(turns)*0.90)]
    percentile_95 = turns[int(len(turns)*0.95)]
    percentile_99 = turns[int(len(turns)*0.99)]
    
    # Print statistics
    print(f"\nTurn Statistics:")
    print(f"Total conversations: {len(turns)}")
    print(f"Min turns: {min_turns}")
    print(f"Median turns: {median_turns}")
    print(f"90th percentile: {percentile_90}")
    print(f"95th percentile: {percentile_95}")
    print(f"99th percentile: {percentile_99}")
    print(f"Max turns: {max_turns}")
    
    # Calculate distribution
    counter = Counter(turns)
    
    print("\nDistribution:")
    for count, freq in sorted(counter.items()):
        print(f"{count} turns: {freq} conversations ({freq/len(turns)*100:.1f}%)")
    
    # Recommendation
    print("\nRecommendation:")
    if percentile_95 <= 10:
        recommended = 10
    elif percentile_95 <= 15:
        recommended = 15
    elif percentile_95 <= 20:
        recommended = 20
    else:
        recommended = 25
    
    print(f"Based on the 95th percentile ({percentile_95}), a reasonable MAX_CHAT_TURNS value would be {recommended}.")
    print(f"This would cover {sum(1 for t in turns if t <= recommended)/len(turns)*100:.1f}% of all conversations.")
    
    return recommended

if __name__ == "__main__":
    # Analyze the sample file
    sample_file = Path("data/cedric_120_sample.json")
    analyze_turns(sample_file) 