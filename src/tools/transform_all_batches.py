import os
from pathlib import Path
from transform_data_for_dynamic_turns import transform_data

def transform_all_batches():
    """Transform all batch files in the data directory."""
    data_dir = Path("data")
    
    # Get all batch files that don't end in _transformed.json
    batch_files = [f for f in data_dir.glob("batch_*.json") if not f.name.endswith("_transformed.json")]
    
    print(f"📁 Found {len(batch_files)} batch files to transform")
    
    for batch_file in sorted(batch_files):
        output_file = batch_file.parent / f"{batch_file.stem}_transformed.json"
        print(f"\n🔄 Processing {batch_file.name}...")
        
        success = transform_data(str(batch_file), str(output_file))
        if success:
            print(f"✅ Successfully transformed {batch_file.name}")
        else:
            print(f"❌ Failed to transform {batch_file.name}")

if __name__ == "__main__":
    transform_all_batches() 