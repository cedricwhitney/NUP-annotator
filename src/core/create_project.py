import os
import sys
import requests
from label_studio_sdk import Client
import json
from pathlib import Path
from src.tools.convert_jsonl_to_json import convert_jsonl_to_json
from src.tools.validate_labelstudio_json import validate_and_fix_json

LABEL_STUDIO_URL = os.getenv("LABEL_STUDIO_URL", "http://localhost:8080")

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
TASKS_FILE = os.path.join(DATA_DIR, 'initial_tasks.json')

def get_api_key():
    api_key = os.getenv("LABEL_STUDIO_API_KEY")
    if not api_key:
        print("\n🔑 No API key found in environment.")
        print("Please get your API key from Label Studio:")
        print("1. Visit http://localhost:8080")
        print("2. Go to Account & Settings > Access Token")
        api_key = input("\nEnter your API key: ").strip()
        if not api_key:
            print("❌ Error: API key is required")
            sys.exit(1)
    return api_key

LABEL_CONFIG = """
<View>
    <Paragraphs value="$conversation" name="conversation" 
                layout="dialogue" textKey="text" nameKey="role"/>
    <Taxonomy name="taxonomy" toName="conversation">
        <Choice value="Self-Disclosure">
            <Choice value="Yes" />
            <Choice value="No" />
        </Choice>
        <Choice value="Media Format">
            <Choice value="Natural language" />
            <Choice value="Code" />
            <Choice value="Math / symbols" />
            <Choice value="Formatted enumeration/itemization (bullets/lists)" />
            <Choice value="Charts/Graphs" />
            <Choice value="Images" />
            <Choice value="Audio" />
            <Choice value="URLs" />
            <Choice value="Other" />
        </Choice>
        <Choice value="Anthropomorphization">
            <Choice value="Yes" />
            <Choice value="No" />
        </Choice>
        <Choice value="Answer Form">
            <Choice value="Refusal to answer (with explanation)" />
            <Choice value="Refusal to answer (without explanation)" />
            <Choice value="Partial refusal, expressing uncertainty, disclaiming" />
            <Choice value="Direct Answer / Open Generation" />
            <Choice value="Continuation of Input" />
        </Choice>
        <Choice value="Multi-turn Relationship">
            <Choice value="First request" />
            <Choice value="Unrelated request" />
            <Choice value="Same task, new request" />
            <Choice value="Repeat request" />
            <Choice value="Related request" />
        </Choice>
        <Choice value="Topics">
            <Choice value="Math &amp; Sciences" />
            <Choice value="History" />
            <Choice value="Geography" />
            <Choice value="Religion &amp; Spirituality" />
            <Choice value="Literature &amp; Writing" />
            <Choice value="Psychology, Philosophy &amp; Human Behavior" />
            <Choice value="Linguistics &amp; Languages" />
            <Choice value="Technology, Software &amp; Computing" />
            <Choice value="Engineering &amp; Infrastructure" />
            <Choice value="Nature &amp; Environment" />
            <Choice value="Transportation" />
            <Choice value="Travel &amp; Tourism" />
            <Choice value="Lifestyle" />
            <Choice value="Food &amp; Dining" />
            <Choice value="Art &amp; Design" />
            <Choice value="Fashion &amp; Beauty" />
            <Choice value="Culture" />
            <Choice value="Entertainment, Hobbies &amp; Leisure" />
            <Choice value="Sports" />
            <Choice value="Social Issues &amp; Movements" />
            <Choice value="Economics" />
            <Choice value="Health &amp; Medicine" />
            <Choice value="Business &amp; Finances" />
            <Choice value="Employment &amp; Hiring" />
            <Choice value="Education" />
            <Choice value="News &amp; Current Affairs" />
            <Choice value="Interpersonal Relationships &amp; Communication" />
            <Choice value="Adult &amp; Illicit Content" />
            <Choice value="Law, Criminal Justice, Law Enforcement" />
            <Choice value="Politics &amp; Elections" />
            <Choice value="Insurance &amp; Social Scoring" />
            <Choice value="Housing" />
            <Choice value="Immigration / Migration" />
            <Choice value="Other" />
        </Choice>
        <Choice value="Restricted Use Flags">
            <Choice value="Inciting violence, hateful or other harmful behavior: harassment &amp; bullying" />
            <Choice value="Inciting violence, hateful or other harmful behavior: physical harm" />
            <Choice value="Inciting violence, hateful or other harmful behavior: self-harm" />
            <Choice value="Criminal planning or other suspected illegal activity not listed elsewhere" />
            <Choice value="Cyberattacks" />
            <Choice value="Weapons &amp; drugs" />
            <Choice value="CBRN-related outputs" />
            <Choice value="Sexually explicit content: real person" />
            <Choice value="Sexually explicit content: fictitious person" />
            <Choice value="Sexually explicit content: Request/discussion of CSAM" />
            <Choice value="Sexually explicit content: Other" />
            <Choice value="Impersonation attempts" />
            <Choice value="Misinformation" />
            <Choice value="Privacy concerns: Possible identifiable information" />
            <Choice value="Privacy concerns: Possible sensitive information" />
            <Choice value="Generating spam" />
            <Choice value="Generating defamatory content" />
            <Choice value="Output misrepresentation: disclaiming AI use" />
            <Choice value="Output misrepresentation: Automated decision-making without disclosure" />
            <Choice value="Discriminatory practices" />
            <Choice value="Possible presence of copyrighted, unreferenced material" />
            <Choice value="Other" />
        </Choice>
    </Taxonomy>
</View>
"""

def get_input_file():
    """Let user choose their input file."""
    data_dir = Path("data")
    
    # List all potential input files
    data_files = list(data_dir.glob("*.json*"))  # Gets both .json and .jsonl files
    
    if not data_files:
        print("❌ Error: No JSON/JSONL files found in data directory")
        print(f"Please add your tasks file to: {data_dir}/")
        sys.exit(1)
    
    if len(data_files) == 1:
        chosen_file = data_files[0]
        print(f"📁 Found file: {chosen_file}")
    else:
        print("\n📁 Multiple files found. Please choose one:")
        for i, file in enumerate(data_files, 1):
            print(f"{i}. {file}")
        
        while True:
            try:
                choice = input("\nEnter the number of the file to use: ").strip()
                file_index = int(choice) - 1
                if 0 <= file_index < len(data_files):
                    chosen_file = data_files[file_index]
                    break
                else:
                    print("❌ Invalid choice. Please enter a number from the list.")
            except ValueError:
                print("❌ Please enter a valid number.")
    
    return chosen_file

def prepare_tasks_file():
    """Prepare the tasks file for Label Studio."""
    input_file = get_input_file()
    print(f"📁 Using file: {input_file}")
    
    # If it's JSONL, convert it
    if input_file.suffix == '.jsonl':
        print("🔄 Converting JSONL to JSON format...")
        output_file = input_file.with_suffix('.json')
        convert_jsonl_to_json(str(input_file), str(output_file))
        input_file = output_file
    
    # Validate the JSON format
    print("🔍 Validating JSON format...")
    if not validate_and_fix_json(str(input_file)):
        print("❌ Error: Invalid JSON format. Please fix the format and try again.")
        sys.exit(1)
    
    return str(input_file)

def main():
    api_key = get_api_key()
    
    # Initialize Label Studio client
    ls = Client(url=LABEL_STUDIO_URL, api_key=api_key)
    print(f"📡 Connecting to Label Studio at {LABEL_STUDIO_URL}...")

    try:
        # Create project
        project_name = "DUP Taxonomy Annotation"
        print(f"🛠 Creating new project: {project_name}")
        project = ls.start_project(
            title=project_name,
            label_config=LABEL_CONFIG,
        )
        print(f"🎉 Project created: {project.id}")
        
        # Import tasks
        print("📥 Importing initial tasks...")
        tasks = prepare_tasks_file()
        project.import_tasks(tasks)
        print(f"✅ Imported {len(tasks)} tasks")
        
        # Save the API key for future use
        print("\n💡 Tip: To skip this prompt next time, set your API key as an environment variable:")
        print(f"export LABEL_STUDIO_API_KEY={api_key}")
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print("❌ Error: Invalid API key")
            sys.exit(1)
        raise

if __name__ == "__main__":
    main()
