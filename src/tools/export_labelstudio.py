import os
from label_studio_sdk import Client
from datetime import datetime
import json
from pathlib import Path

LABEL_STUDIO_URL = os.getenv("LABEL_STUDIO_URL", "http://localhost:8080")
LABEL_STUDIO_API_KEY = os.getenv("LABEL_STUDIO_API_KEY")
# Store exports in a git-tracked directory within data/
EXPORT_DIR = Path("data/annotator_exports")

def get_api_key():
    if not LABEL_STUDIO_API_KEY:
        raise ValueError("LABEL_STUDIO_API_KEY environment variable is required")
    return LABEL_STUDIO_API_KEY

def get_annotator_name():
    """Get annotator name from git config"""
    import subprocess
    try:
        result = subprocess.run(
            ["git", "config", "user.name"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        print("⚠️  Could not get git username, using 'unknown'")
        return "unknown"

def export_data():
    # Create export directory if it doesn't exist
    EXPORT_DIR.mkdir(exist_ok=True)
    
    # Initialize Label Studio client
    ls = Client(url=LABEL_STUDIO_URL, api_key=get_api_key())
    
    # Get all projects
    projects = ls.get_projects()
    
    # Get annotator name from git
    annotator = get_annotator_name()
    
    # Create annotator-specific file that will be updated with each export
    export_filename = EXPORT_DIR / f"{annotator}_annotations.json"
    
    all_exports = {
        "metadata": {
            "annotator": annotator,
            "last_export": datetime.now().isoformat(),
            "projects": []
        },
        "annotations": []
    }
    
    for project in projects:
        print(f"📤 Exporting data from project: {project.title}")
        exported_data = project.export_tasks()
        
        # Add project metadata
        all_exports["metadata"]["projects"].append({
            "project_id": project.id,
            "project_title": project.title
        })
        
        # Add annotations
        all_exports["annotations"].extend(exported_data)
    
    # Save to file
    with open(export_filename, 'w') as f:
        json.dump(all_exports, f, indent=2)
    
    print(f"✅ Successfully exported {len(all_exports['annotations'])} annotations")

if __name__ == "__main__":
    try:
        export_data()
    except Exception as e:
        print(f"❌ Export failed: {e}")
        exit(1) 