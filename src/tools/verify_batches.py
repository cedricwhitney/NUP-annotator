import json
from collections import defaultdict

def verify_batches():
    # Track which conversations appear in which batches
    conversation_batches = defaultdict(list)
    batch_sizes = {}
    
    # Read each batch file
    for i in range(1, 13):
        filename = f"data/batch_{i}.json"
        with open(filename) as f:
            data = json.load(f)
            batch_sizes[i] = len(data)
            
            # Track each conversation
            for task in data:
                # Create a unique identifier for the conversation
                # Using the first message as an identifier
                conv = task['data']['conversation'][0]['text']
                conversation_batches[conv].append(i)
    
    # Print batch sizes
    print("\nBatch sizes:")
    for batch, size in batch_sizes.items():
        print(f"Batch {batch}: {size} conversations")
    
    # Verify each conversation appears exactly twice
    print("\nCoverage verification:")
    total_conversations = len(conversation_batches)
    correct_coverage = sum(1 for conv, batches in conversation_batches.items() if len(batches) == 2)
    
    print(f"\nTotal unique conversations: {total_conversations}")
    print(f"Conversations appearing exactly twice: {correct_coverage}")
    
    # Print any irregularities
    if total_conversations != 60 or correct_coverage != 60:
        print("\nIrregularities found:")
        for conv, batches in conversation_batches.items():
            if len(batches) != 2:
                print(f"Conversation appears in {len(batches)} batches: {batches}")

if __name__ == "__main__":
    verify_batches() 