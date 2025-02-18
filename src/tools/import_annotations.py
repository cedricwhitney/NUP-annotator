import json
from pathlib import Path
from datetime import datetime
import sys

EXPORT_DIR = Path(__file__).parent.parent.parent / "annotator_exports"

def import_annotations(input_file: str, annotator_name: str):
    """Import annotations from a JSON file into an annotator's history."""
    
    EXPORT_DIR.mkdir(exist_ok=True)
    input_path = Path(input_file)
    
    # Validate input file exists
    if not input_path.exists():
        print(f"❌ Input file not found: {input_file}")
        return False
        
    # Load the input JSON
    try:
        with open(input_path) as f:
            raw_data = json.load(f)
            
        # Handle both raw export format (list) and metadata format (dict)
        if isinstance(raw_data, list):
            new_data = {
                "projects": [],
                "annotations": raw_data
            }
        else:
            new_data = raw_data
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON file: {input_file}")
        return False
        
    # Prepare the export file path
    export_filename = EXPORT_DIR / f"{annotator_name}_annotations.json"
    
    # Create new export structure
    all_exports = {
        "metadata": {
            "annotator": annotator_name,
            "last_export": datetime.now().isoformat(),
            "projects": new_data.get("projects", [])
        },
        "annotations": new_data.get("annotations", [])
    }
    
    # Save updated file
    with open(export_filename, 'w') as f:
        json.dump(all_exports, f, indent=2)
    
    print(f"✅ Successfully imported annotations for {annotator_name}")
    print(f"📊 Total annotations: {len(all_exports['annotations'])}")
    return True

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python import_annotations.py <input_json_file> <annotator_name>")
        print("Example: python import_annotations.py new_annotations.json john")
        sys.exit(1)
    
    input_file = sys.argv[1]
    annotator_name = sys.argv[2]
    
    if import_annotations(input_file, annotator_name):
        print("\n📋 Next steps:")
        print("1. git add annotator_exports/")
        print("2. git commit -m 'Import annotations for " + annotator_name + "'")
        print("3. git pull origin main  # Get any updates from other annotators")
        print("4. git push origin main  # Share the imported annotations")
    else:
        sys.exit(1) 