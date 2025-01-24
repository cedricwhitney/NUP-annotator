import os
from label_studio_sdk import Client
import json

LABEL_STUDIO_URL = os.getenv("LABEL_STUDIO_URL", "http://localhost:8080")
LABEL_STUDIO_API_KEY = os.getenv("LABEL_STUDIO_API_KEY", "712b782e7e9f192994ceec6044bc6c24bd953dda")
PROJECT_NAME = "DUP Taxonomy Annotation"  # Replace with your shared project name

def main():
    # Initialize Label Studio client
    ls = Client(url=LABEL_STUDIO_URL, api_key=LABEL_STUDIO_API_KEY)
    print(f"📡 Connecting to Label Studio at {LABEL_STUDIO_URL}...")

    # Find the existing project by name
    projects = ls.get_projects()
    project = next((p for p in projects if p.title == PROJECT_NAME), None)

    if not project:
        print(f"❌ Project '{PROJECT_NAME}' not found. Please ensure it exists.")
        return

    print(f"✅ Found project: {PROJECT_NAME} (ID: {project.id})")

    # Fetch the project object
    project_obj = ls.get_project(project.id)

    # Upload tasks
    json_file = "data/test_output.json"
    if os.path.exists(json_file):
        print(f"📤 Uploading tasks from: {json_file}")
        with open(json_file, "r", encoding="utf-8") as f:
            tasks = json.load(f)
            project_obj.import_tasks(tasks)  # Correct way to import tasks
        print(f"🎉 Tasks uploaded successfully!")
    else:
        print(f"❌ JSON file not found: {json_file}")


if __name__ == "__main__":
    main()
