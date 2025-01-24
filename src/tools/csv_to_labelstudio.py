import os
import pandas as pd
import json

def main():
    """Convert conversation CSV to Label Studio JSON format.
    
    Expected CSV format:
        Turn 0, Turn 1, Turn 2, Turn 3, Turn 4
        "Hello", "Hi there", "How are you?", "I'm good", "Great!"
    
    Will be converted to Label Studio format with:
        - Even-numbered turns (0, 2, 4) marked as "human"
        - Odd-numbered turns (1, 3) marked as "llm"
        - Empty turns are skipped
    """
    # Input and output file paths
    csv_file = os.getenv("TEST_CSV_FILE", "data/test_input_cleaned.csv")
    json_file = os.getenv("TEST_JSON_FILE", "data/test_output.json")

    print(f"🔍 Checking if '{csv_file}' exists...")
    if not os.path.exists(csv_file):
        print(f"❌ File not found: {csv_file}")
        return

    print(f"✅ Found file: {csv_file}")
    print("📊 Reading CSV content...")

    try:
        # Read the CSV and fill missing values with empty strings
        # Use csv.QUOTE_MINIMAL for proper handling of quoted strings
        df = pd.read_csv(
            csv_file, 
            sep=',', 
            quoting=1,  # QUOTE_MINIMAL
            quotechar='"',
            keep_default_na=False  # Don't convert empty strings to NaN
        ).fillna('')
        print(f"✅ Successfully read CSV with {len(df)} rows.")
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return

    tasks = []

    # Process each row to generate tasks
    for _, row in df.iterrows():
        conversation = []

        # Loop through Turn 0 to Turn 4
        for i in range(5):  # Turn 0 to Turn 4
            turn_key = f"Turn {i}"
            message = row.get(turn_key, '').strip()
            if message:  # Only add if message has content after stripping
                role = "human" if i % 2 == 0 else "llm"
                conversation.append({
                    "role": role,
                    "text": message
                })

        # Only add the task if there are non-empty messages in the conversation
        if len(conversation) > 0:  # Additional check to ensure we have messages
            tasks.append({
                "data": {  # Add data wrapper for Label Studio format
                    "conversation": conversation
                }
            })

    print(f"✅ Processed {len(tasks)} tasks.")

    # Save to JSON
    print(f"💾 Saving JSON to: {json_file}")
    try:
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(tasks, f, indent=4, ensure_ascii=False)
        print(f"🎉 JSON file created successfully: {json_file}")
    except Exception as e:
        print(f"❌ Error saving JSON: {e}")


if __name__ == "__main__":
    print("🚀 Starting the script!")
    main()
    print("🎉 Script completed!")
