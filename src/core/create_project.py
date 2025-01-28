import os
import sys
import requests
from label_studio_sdk import Client
import json
from pathlib import Path
from src.tools.convert_jsonl_to_json import convert_jsonl_to_json
from src.tools.validate_labelstudio_json import validate_and_fix_json

LABEL_STUDIO_URL = os.getenv("LABEL_STUDIO_URL", "http://localhost:8080")

# Constants
DATA_DIR = Path("data")
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
<View style="display: flex;">
    <View style="width: 60%; padding-right: 1em;">
        <Paragraphs name="conversation" value="$conversation" 
                    layout="dialogue" textKey="text" nameKey="role"/>
    </View>
    
    <View style="width: 40%; padding-left: 1em; overflow-y: auto;">
        <Collapse>
            <Panel value="Conversation-Level Labels">
                <View>
                    <Collapse>
                        <Panel value="Self-disclosure">
                            <View>
                                <Choices name="self_disclosure" toName="conversation" choice="single" required="true">
                                    <Choice value="Yes" />
                                    <Choice value="No" />
                                </Choices>
                            </View>
                        </Panel>
                    </Collapse>
                    
                    <Collapse>
                        <Panel value="Topics">
                            <View>
                                <Filter name="filter_topics" toName="topics" minlength="0" placeholder="Filter topics..."/>
                                <Labels name="topics" toName="conversation" choice="multiple">
                                    <Label value="Math &amp; Sciences" />
                                    <Label value="History" />
                                    <Label value="Geography" />
                                    <Label value="Religion &amp; Spirituality" />
                                    <Label value="Literature &amp; Writing" />
                                    <Label value="Psychology, Philosophy &amp; Human Behavior" />
                                    <Label value="Linguistics &amp; Languages" />
                                    <Label value="Technology, Software &amp; Computing" />
                                    <Label value="Engineering &amp; Infrastructure" />
                                    <Label value="Nature &amp; Environment" />
                                    <Label value="Transportation" />
                                    <Label value="Travel &amp; Tourism" />
                                    <Label value="Lifestyle" />
                                    <Label value="Food &amp; Dining" />
                                    <Label value="Art &amp; Design" />
                                    <Label value="Fashion &amp; Beauty" />
                                    <Label value="Culture" />
                                    <Label value="Entertainment, Hobbies &amp; Leisure" />
                                    <Label value="Sports" />
                                    <Label value="Social Issues &amp; Movements" />
                                    <Label value="Economics" />
                                    <Label value="Health &amp; Medicine" />
                                    <Label value="Business &amp; Finances" />
                                    <Label value="Employment &amp; Hiring" />
                                    <Label value="Education" />
                                    <Label value="News &amp; Current Affairs" />
                                    <Label value="Interpersonal Relationships &amp; Communication" />
                                    <Label value="Adult &amp; Illicit Content" />
                                    <Label value="Law, Criminal Justice, Law Enforcement" />
                                    <Label value="Politics &amp; Elections" />
                                    <Label value="Insurance &amp; Social Scoring" />
                                    <Label value="Housing" />
                                    <Label value="Immigration / Migration" />
                                    <Label value="Other" />
                                </Labels>
                            </View>
                        </Panel>
                    </Collapse>
                </View>
            </Panel>
        </Collapse>

        <Collapse>
            <Panel value="Text-Level Labels">
                <View>
                    <Header value="First, highlight text, then click the correct label, then click the highlighted text and select the corresponding dropdown." size="10"/>
                    
                    <ParagraphLabels name="text_selection" toName="conversation">
                        <Label value="Prompt 1" background="#ffd700"/>
                        <Label value="Response 1" background="#4169e1"/>
                        <Label value="Prompt 2" background="#ffd700"/>
                        <Label value="Response 2" background="#4169e1"/>
                        <Label value="Prompt 3" background="#ffd700"/>
                    </ParagraphLabels>
                    
                    <Collapse>
                        <Panel value="Prompt 1">
                            <View>
                                <Collapse>
                                    <Panel value="Multi-turn Relationship">
                                        <View>
                                            <Choices name="multi_turn_prompt1" toName="conversation" perRegion="true" whenTagName="text_selection" whenLabelValue="Prompt 1" choice="single">
                                                <Choice value="First request" />
                                                <Choice value="Unrelated request" />
                                                <Choice value="Same task, new request" />
                                                <Choice value="Repeat request" />
                                                <Choice value="Related request" />
                                            </Choices>
                                        </View>
                                    </Panel>
                                </Collapse>
                                
                                <Collapse>
                                    <Panel value="Function/Purpose">
                                        <View>
                                            <Choices name="function_purpose_prompt1" toName="conversation" perRegion="true" whenTagName="text_selection" whenLabelValue="Prompt 1" choice="multiple">
                                                <Choice value="Information Seeking" />
                                                <Choice value="Task Completion" />
                                                <Choice value="Social Interaction" />
                                                <Choice value="Content Creation" />
                                                <Choice value="Problem Solving" />
                                                <Choice value="Learning/Education" />
                                                <Choice value="Entertainment" />
                                                <Choice value="Other" />
                                            </Choices>
                                        </View>
                                    </Panel>
                                </Collapse>
                                
                                <Collapse>
                                    <Panel value="Restricted Use Flags">
                                        <View>
                                            <Filter name="filter_flags_prompt1" toName="restricted_flags_prompt1" minlength="0" placeholder="Filter flags..."/>
                                            <Choices name="restricted_flags_prompt1" toName="conversation" perRegion="true" whenTagName="text_selection" whenLabelValue="Prompt 1" choice="multiple">
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
                                            </Choices>
                                        </View>
                                    </Panel>
                                </Collapse>
                            </View>
                        </Panel>
                    </Collapse>
                    
                    <Collapse>
                        <Panel value="Response 1">
                            <View>
                                <Collapse>
                                    <Panel value="Media Format">
                                        <View>
                                            <Choices name="media_format_response1" toName="conversation" perRegion="true" whenTagName="text_selection" whenLabelValue="Response 1" choice="multiple">
                                                <Choice value="Natural language" />
                                                <Choice value="Code" />
                                                <Choice value="Math / symbols" />
                                                <Choice value="Formatted enumeration/itemization" />
                                                <Choice value="Charts/Graphs" />
                                                <Choice value="Images" />
                                                <Choice value="Audio" />
                                                <Choice value="URLs" />
                                                <Choice value="Other" />
                                            </Choices>
                                        </View>
                                    </Panel>
                                </Collapse>
                                
                                <Collapse>
                                    <Panel value="Anthropomorphization">
                                        <View>
                                            <Choices name="anthropomorphization_response1" toName="conversation" perRegion="true" whenTagName="text_selection" whenLabelValue="Response 1" choice="single">
                                                <Choice value="Yes" />
                                                <Choice value="No" />
                                            </Choices>
                                        </View>
                                    </Panel>
                                </Collapse>
                                
                                <Collapse>
                                    <Panel value="Answer Form">
                                        <View>
                                            <Choices name="answer_form_response1" toName="conversation" perRegion="true" whenTagName="text_selection" whenLabelValue="Response 1" choice="single">
                                                <Choice value="Refusal to answer (with explanation)" />
                                                <Choice value="Refusal to answer (without explanation)" />
                                                <Choice value="Partial refusal, expressing uncertainty, disclaiming" />
                                                <Choice value="Direct Answer / Open Generation" />
                                                <Choice value="Continuation of Input" />
                                            </Choices>
                                        </View>
                                    </Panel>
                                </Collapse>
                            </View>
                        </Panel>
                    </Collapse>
                    
                    <Collapse>
                        <Panel value="Prompt 2">
                            <View>
                                <Collapse>
                                    <Panel value="Multi-turn Relationship">
                                        <View>
                                            <Choices name="multi_turn_prompt2" toName="conversation" perRegion="true" whenTagName="text_selection" whenLabelValue="Prompt 2" choice="single">
                                                <Choice value="First request" />
                                                <Choice value="Unrelated request" />
                                                <Choice value="Same task, new request" />
                                                <Choice value="Repeat request" />
                                                <Choice value="Related request" />
                                            </Choices>
                                        </View>
                                    </Panel>
                                </Collapse>
                                
                                <Collapse>
                                    <Panel value="Function/Purpose">
                                        <View>
                                            <Choices name="function_purpose_prompt2" toName="conversation" perRegion="true" whenTagName="text_selection" whenLabelValue="Prompt 2" choice="multiple">
                                                <Choice value="Information Seeking" />
                                                <Choice value="Task Completion" />
                                                <Choice value="Social Interaction" />
                                                <Choice value="Content Creation" />
                                                <Choice value="Problem Solving" />
                                                <Choice value="Learning/Education" />
                                                <Choice value="Entertainment" />
                                                <Choice value="Other" />
                                            </Choices>
                                        </View>
                                    </Panel>
                                </Collapse>
                                
                                <Collapse>
                                    <Panel value="Restricted Use Flags">
                                        <View>
                                            <Filter name="filter_flags_prompt2" toName="restricted_flags_prompt2" minlength="0" placeholder="Filter flags..."/>
                                            <Choices name="restricted_flags_prompt2" toName="conversation" perRegion="true" whenTagName="text_selection" whenLabelValue="Prompt 2" choice="multiple">
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
                                            </Choices>
                                        </View>
                                    </Panel>
                                </Collapse>
                            </View>
                        </Panel>
                    </Collapse>
                    
                    <Collapse>
                        <Panel value="Response 2">
                            <View>
                                <Collapse>
                                    <Panel value="Media Format">
                                        <View>
                                            <Choices name="media_format_response2" toName="conversation" perRegion="true" whenTagName="text_selection" whenLabelValue="Response 2" choice="multiple">
                                                <Choice value="Natural language" />
                                                <Choice value="Code" />
                                                <Choice value="Math / symbols" />
                                                <Choice value="Formatted enumeration/itemization" />
                                                <Choice value="Charts/Graphs" />
                                                <Choice value="Images" />
                                                <Choice value="Audio" />
                                                <Choice value="URLs" />
                                                <Choice value="Other" />
                                            </Choices>
                                        </View>
                                    </Panel>
                                </Collapse>
                                
                                <Collapse>
                                    <Panel value="Anthropomorphization">
                                        <View>
                                            <Choices name="anthropomorphization_response2" toName="conversation" perRegion="true" whenTagName="text_selection" whenLabelValue="Response 2" choice="single">
                                                <Choice value="Yes" />
                                                <Choice value="No" />
                                            </Choices>
                                        </View>
                                    </Panel>
                                </Collapse>
                                
                                <Collapse>
                                    <Panel value="Answer Form">
                                        <View>
                                            <Choices name="answer_form_response2" toName="conversation" perRegion="true" whenTagName="text_selection" whenLabelValue="Response 2" choice="single">
                                                <Choice value="Refusal to answer (with explanation)" />
                                                <Choice value="Refusal to answer (without explanation)" />
                                                <Choice value="Partial refusal, expressing uncertainty, disclaiming" />
                                                <Choice value="Direct Answer / Open Generation" />
                                                <Choice value="Continuation of Input" />
                                            </Choices>
                                        </View>
                                    </Panel>
                                </Collapse>
                            </View>
                        </Panel>
                    </Collapse>
                    
                    <Collapse>
                        <Panel value="Prompt 3">
                            <View>
                                <Collapse>
                                    <Panel value="Multi-turn Relationship">
                                        <View>
                                            <Choices name="multi_turn_prompt3" toName="conversation" perRegion="true" whenTagName="text_selection" whenLabelValue="Prompt 3" choice="single">
                                                <Choice value="First request" />
                                                <Choice value="Unrelated request" />
                                                <Choice value="Same task, new request" />
                                                <Choice value="Repeat request" />
                                                <Choice value="Related request" />
                                            </Choices>
                                        </View>
                                    </Panel>
                                </Collapse>
                                
                                <Collapse>
                                    <Panel value="Function/Purpose">
                                        <View>
                                            <Choices name="function_purpose_prompt3" toName="conversation" perRegion="true" whenTagName="text_selection" whenLabelValue="Prompt 3" choice="multiple">
                                                <Choice value="Information Seeking" />
                                                <Choice value="Task Completion" />
                                                <Choice value="Social Interaction" />
                                                <Choice value="Content Creation" />
                                                <Choice value="Problem Solving" />
                                                <Choice value="Learning/Education" />
                                                <Choice value="Entertainment" />
                                                <Choice value="Other" />
                                            </Choices>
                                        </View>
                                    </Panel>
                                </Collapse>
                                
                                <Collapse>
                                    <Panel value="Restricted Use Flags">
                                        <View>
                                            <Filter name="filter_flags_prompt3" toName="restricted_flags_prompt3" minlength="0" placeholder="Filter flags..."/>
                                            <Choices name="restricted_flags_prompt3" toName="conversation" perRegion="true" whenTagName="text_selection" whenLabelValue="Prompt 3" choice="multiple">
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
                                            </Choices>
                                        </View>
                                    </Panel>
                                </Collapse>
                            </View>
                        </Panel>
                    </Collapse>
                </View>
            </Panel>
        </Collapse>
    </View>
</View>
"""

def get_input_file():
    """Let user choose their input file."""
    # Use DATA_DIR instead of creating new Path
    data_files = list(DATA_DIR.glob("*.json*"))
    
    if not data_files:
        print("❌ Error: No JSON/JSONL files found in data directory")
        print(f"Please add your tasks file to: {DATA_DIR}/")
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
