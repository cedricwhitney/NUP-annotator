import os
import sys
import requests
from label_studio_sdk import Client
import json
from pathlib import Path
from src.tools.convert_jsonl_to_json import convert_jsonl_to_json
from src.tools.validate_labelstudio_json import validate_and_fix_json
from src.tools.transform_data_for_dynamic_turns import transform_data

LABEL_STUDIO_URL = os.getenv("LABEL_STUDIO_URL", "http://localhost:8080")

# Constants
DATA_DIR = Path("data")
TASKS_FILE = os.path.join(DATA_DIR, 'initial_tasks.json')
MAX_CHAT_TURNS = 10  # Maximum number of turns to support in the UI

def get_api_key():
    api_key = os.getenv("LABEL_STUDIO_API_KEY")
    if not api_key:
        print("\n🔑 No API key found in environment.")
        print("Please get your API key from Label Studio:")
        print("1. Visit http://localhost:8080")
        print("2. Go to Account & Settings > Access Token")
        print("\nNote: The terminal will keep scrolling with Label Studio logs.")
        print("Don't worry - just paste your API key and press Enter!\n")
        api_key = input("Enter your API key: ").strip()
        if not api_key:
            print("❌ Error: API key is required")
            sys.exit(1)
    return api_key

def generate_dynamic_label_config(max_turns=None):
    """Generate a dynamic Label Studio configuration based on the maximum number of turns."""
    
    # If max_turns is not provided, use the default
    if max_turns is None:
        max_turns = MAX_CHAT_TURNS
    
    # Base view with conversation display
    base_view = """
<View style="display: flex;">
    <Style>.htx-text{ white-space: pre-wrap; }</Style>
    <View style="width: 60%; padding-right: 1em; white-space: pre-wrap;">
        <Paragraphs name="conversation" value="$conversation" 
        layout="dialogue" textKey="text" nameKey="role"/>
        <Header value="Original ID: $original_task_id" style="margin-top: 1em; font-size: 0.9em; color: #555;"/>
    </View>
    
    <View style="width: 40%; padding-left: 1em; overflow-y: auto;">
        <View style="margin-bottom: 1em; padding: 1em; background: #f0f0f0; border-radius: 5px;">
            <Header value="Select turns to display:" />
            <Choices name="turn_selector" toName="conversation" choice="multiple" showInline="true">
"""
    
    # Add checkbox for each possible turn
    for turn_num in range(1, max_turns + 1):
        base_view += f'                <Choice value="Turn {turn_num}">Turn {turn_num}</Choice>\n'
    
    base_view += """
                            </Choices>
                </View>
"""

    # Generate panels for each turn
    turn_panels = ""
    for turn_num in range(1, max_turns + 1):
        # Create panel for the prompt (user message)
        prompt_panel = f"""
        <View whenTagName="turn_selector" whenChoiceValue="Turn {turn_num}" visibleWhen="choice-selected">
            <Collapse visibleWhen="$turn{turn_num}_dialogue[0].text">
                <Panel value="Turn {turn_num} - Prompt">
                    <View>
                        <Collapse>
                            <Panel value="Media Format">
                                <Filter name="filter_media_{turn_num}" toName="media_format_{turn_num}" minlength="0" placeholder="Filter media formats..."/>
                                <Choices name="media_format_{turn_num}" toName="conversation" choice="multiple">
                                    <Choice value="Audio" />
                                    <Choice value="Charts/Graphs" />
                                    <Choice value="Code" />
                                    <Choice value="Formatted enumeration/itemization" />
                                    <Choice value="HTML" />
                                    <Choice value="Images" />
                                    <Choice value="Likely retrieved/pasted content" />
                                    <Choice value="Math / symbols" />
                                    <Choice value="Natural language" />
                                    <Choice value="URLs" />
                                    <Choice value="Other" />
                                </Choices>
                            </Panel>
                        </Collapse>
                        
                        <Collapse>
                            <Panel value="Function/Purpose">
                                <Filter name="filter_function_{turn_num}" toName="function_purpose_{turn_num}" minlength="0" placeholder="Filter functions..."/>
                                <Choices name="function_purpose_{turn_num}" toName="conversation" choice="multiple">
                                    <Choice value="No Clear Ask" />
                                    <Choice value="Advice, Guidance, &amp; Recommendations: Instructions / How-to" />
                                    <Choice value="Advice, Guidance, &amp; Recommendations: Social and personal advice" />
                                    <Choice value="Advice, Guidance, &amp; Recommendations: Professional advice" />
                                    <Choice value="Advice, Guidance, &amp; Recommendations: Activity / product recommendations" />
                                    <Choice value="Advice, Guidance, &amp; Recommendations: Action planning (scheduling, robotics)" />
                                    <Choice value="Content generation: brainstorming / ideation" />
                                    <Choice value="Content generation: creative / fiction writing" />
                                    <Choice value="Content generation: academic / essay" />
                                    <Choice value="Content generation: administrative writing" />
                                    <Choice value="Content generation: code" />
                                    <Choice value="Content generation: code documentation" />
                                    <Choice value="Content generation: general prose, discussion or explanation" />
                                    <Choice value="Content generation: prompts for another AI system" />
                                    <Choice value="Content generation: other" />
                                    <Choice value="Editorial &amp; formatting: Natural language content editing" />
                                    <Choice value="Editorial &amp; formatting: Natural language style or re-formatting" />
                                    <Choice value="Editorial &amp; formatting: Code content editing" />
                                    <Choice value="Editorial &amp; formatting: Code style and re-formatting" />
                                    <Choice value="Editorial &amp; formatting: Content summarization" />
                                    <Choice value="Editorial &amp; formatting: Content expansion" />
                                    <Choice value="Editorial &amp; formatting: Information processing &amp; re-formatting" />
                                    <Choice value="Information analysis: Content explanation / interpretation" />
                                    <Choice value="Information analysis: Content quality review or assessment" />
                                    <Choice value="Information analysis: Content Classification" />
                                    <Choice value="Information analysis: Ranking or Scoring" />
                                    <Choice value="Information analysis: Other content analysis / description" />
                                    <Choice value="Information retrieval: general info from web" />
                                    <Choice value="Information retrieval: general info from prompt content" />
                                    <Choice value="Advice, Guidance, &amp; Recommendations: Instructions / How-to" />
                                    <Choice value="Advice, Guidance, &amp; Recommendations: Social and personal advice" />
                                    <Choice value="Advice, Guidance, &amp; Recommendations: Professional advice" />
                                    <Choice value="Advice, Guidance, &amp; Recommendations: Activity / product recommendations" />
                                    <Choice value="Advice, Guidance, &amp; Recommendations: Action planning (scheduling, robotics)" />
                                    <Choice value="Reasoning: Mathematical or numerical problem solving" />
                                    <Choice value="Reasoning: Verbal problems, logic games, puzzles or riddles" />
                                    <Choice value="Reasoning: Other general problem solving" />
                                    <Choice value="Role-play / social simulation: platonic companion / friend" />
                                    <Choice value="Role-play / social simulation: romantic companion" />
                                    <Choice value="Role-play / social simulation: simulation of real person / celebrity" />
                                    <Choice value="Role-play / social simulation: user study persona simulations or polling" />
                                    <Choice value="Role-play / social simulation: therapist / coach" />
                                    <Choice value="Translation (language to language)" />
                                    <Choice value="Other" />
                                </Choices>
                            </Panel>
                        </Collapse>

                        <Collapse>
                            <Panel value="Multi-turn Relationship">
                                <Choices name="multi_turn_relationship_{turn_num}" toName="conversation" choice="single">
                                    <Choice value="First request" />
                                    <Choice value="Unrelated request" />
                                    <Choice value="Same/similar task, new request" />
                                    <Choice value="Repeated/follow-up request" />
                                    <Choice value="New task, related request" />
                                </Choices>
                            </Panel>
                        </Collapse>

                        <Collapse>
                            <Panel value="Interaction Features">
                                <Choices name="interaction_features_{turn_num}" toName="conversation" choice="multiple">
                                    <Choice value="Role-assignment" />
                                    <Choice value="Jailbreak attempt" />
                                    <Choice value="Courtesy / politeness" />
                                    <Choice value="Reinforcement/Praise" />
                                    <Choice value="Companionship" />
                                    <Choice value="None" />
                                </Choices>
                            </Panel>
                        </Collapse>

                        <Collapse>
                            <Panel value="Prompt Quality">
                                <Choices name="prompt_quality_{turn_num}" toName="conversation" choice="single">
                                    <Choice value="Prompt is grammatical, well-formed, and formal" />
                                    <Choice value="Prompt is grammatical, well-formed and casual" />
                                    <Choice value="Prompt is mostly grammatical, well-formed, and formal" />
                                    <Choice value="Prompt is mostly grammatical, well-formed, and casual" />
                                    <Choice value="Prompt is not grammatical, difficult to interpret, or is extremely casual" />
                                </Choices>
                            </Panel>
                        </Collapse>

                        <Collapse>
                            <Panel value="Restricted Flags">
                                <Filter name="filter_flags_{turn_num}" toName="restricted_flags_{turn_num}" minlength="0" placeholder="Filter flags..."/>
                                <Choices name="restricted_flags_{turn_num}" toName="conversation" choice="multiple">
                                    <Choice value="None" />
                                    <Choice value="CBRN-related outputs" />
                                    <Choice value="Criminal planning or other suspected illegal activity not listed elsewhere" />
                                    <Choice value="Cyberattacks" />
                                    <Choice value="Discriminatory practices" />
                                    <Choice value="Generating defamatory content" />
                                    <Choice value="Generating spam" />
                                    <Choice value="Impersonation attempts" />
                                    <Choice value="Inciting violence, hateful or other harmful behavior: harassment &amp; bullying" />
                                    <Choice value="Inciting violence, hateful or other harmful behavior: physical harm" />
                                    <Choice value="Inciting violence, hateful or other harmful behavior: self-harm" />
                                    <Choice value="Misinformation" />
                                    <Choice value="Output misrepresentation: Automated decision-making without disclosure" />
                                    <Choice value="Output misrepresentation: disclaiming AI use" />
                                    <Choice value="Possible presence of copyrighted, unreferenced material" />
                                    <Choice value="Potential violation of external policy / ethics" />
                                    <Choice value="Privacy concerns: Possible identifiable information" />
                                    <Choice value="Privacy concerns: Possible sensitive information" />
                                    <Choice value="Sexually explicit content: fictitious person" />
                                    <Choice value="Sexually explicit content: Other" />
                                    <Choice value="Sexually explicit content: real person" />
                                    <Choice value="Sexually explicit content: Request/discussion of CSAM" />
                                    <Choice value="Weapons &amp; drugs" />
                                    <Choice value="Other" />
                                </Choices>
                            </Panel>
                        </Collapse>
                    </View>
                </Panel>
            </Collapse>

            <Collapse visibleWhen="$turn{turn_num}_dialogue[1].text">
                <Panel value="Turn {turn_num} - Response">
                    <View>
                        <Collapse>
                            <Panel value="Media Format">
                                <Filter name="filter_media_response_{turn_num}" toName="media_format_response_{turn_num}" minlength="0" placeholder="Filter media formats..."/>
                                <Choices name="media_format_response_{turn_num}" toName="conversation" choice="multiple">
                                    <Choice value="Audio" />
                                    <Choice value="Charts/Graphs" />
                                    <Choice value="Code" />
                                    <Choice value="Formatted enumeration/itemization" />
                                    <Choice value="HTML" />
                                    <Choice value="Images" />
                                    <Choice value="Likely retrieved/pasted content" />
                                    <Choice value="Math / symbols" />
                                    <Choice value="Natural language" />
                                    <Choice value="Other" />
                                    <Choice value="URLs" />
                                </Choices>
                            </Panel>
                        </Collapse>

                        <Collapse>
                            <Panel value="Answer Form">
                                <Choices name="answer_form_{turn_num}" toName="conversation" choice="single">
                                    <Choice value="Refusal to answer (with explanation)" />
                                    <Choice value="Refusal to answer (without explanation)" />
                                    <Choice value="Partial refusal, expressing uncertainty, disclaiming" />
                                    <Choice value="Direct Answer / Open Generation" />
                                    <Choice value="Continuation of Input" />
                                </Choices>
                            </Panel>
                        </Collapse>

                        <Collapse>
                            <Panel value="Self Disclosure">
                            <Choices name="self_disclosure_{turn_num}" toName="conversation" choice="single">
                                    <Choice value="Yes" />
                                    <Choice value="No" />
                                </Choices>
                            </Panel>
                        </Collapse>

                        <Collapse>
                            <Panel value="Interaction Features">
                                <Choices name="interaction_features_response_{turn_num}" toName="conversation" choice="multiple">
                                    <Choice value="Self-Disclosure" />
                                    <Choice value="Content-Direct Response" />
                                    <Choice value="Content-Preferences/Feelings/Opinions/Religious beliefs" />
                                    <Choice value="Apology" />
                                    <Choice value="Content-Empathy" />
                                    <Choice value="Register and Style- Phatic Expressions" />
                                    <Choice value="Register and Style- Expressions of Confidence and Doubt" />
                                    <Choice value="Non-Personalization" />
                                    <Choice value="None" />
                                </Choices>
                            </Panel>
                        </Collapse>

                        <Collapse>
                            <Panel value="Restricted Flags">
                                <Filter name="filter_flags_response_{turn_num}" toName="restricted_flags_response_{turn_num}" minlength="0" placeholder="Filter flags..."/>
                            <Choices name="restricted_flags_response_{turn_num}" toName="conversation" choice="multiple">
                                <Choice value="None" />
                                <Choice value="CBRN-related outputs" />
                                <Choice value="Criminal planning or other suspected illegal activity not listed elsewhere" />
                                <Choice value="Cyberattacks" />
                                <Choice value="Discriminatory practices" />
                                <Choice value="Generating defamatory content" />
                                <Choice value="Generating spam" />
                                <Choice value="Impersonation attempts" />
                                <Choice value="Inciting violence, hateful or other harmful behavior: harassment &amp; bullying" />
                                <Choice value="Inciting violence, hateful or other harmful behavior: physical harm" />
                                <Choice value="Inciting violence, hateful or other harmful behavior: self-harm" />
                                <Choice value="Misinformation" />
                                <Choice value="Other" />
                                <Choice value="Output misrepresentation: Automated decision-making without disclosure" />
                                <Choice value="Output misrepresentation: disclaiming AI use" />
                                <Choice value="Possible presence of copyrighted, unreferenced material" />
                                <Choice value="Potential violation of external policy / ethics" />
                                <Choice value="Privacy concerns: Possible identifiable information" />
                                <Choice value="Privacy concerns: Possible sensitive information" />
                                <Choice value="Sexually explicit content: fictitious person" />
                                <Choice value="Sexually explicit content: Other" />
                                <Choice value="Sexually explicit content: real person" />
                                <Choice value="Sexually explicit content: Request/discussion of CSAM" />
                                <Choice value="Weapons &amp; drugs" />
                                </Choices>
                            </Panel>
                        </Collapse>
                    </View>
                </Panel>
            </Collapse>
        </View>
"""

        # Create panel for the whole turn (containing both user and assistant messages)
        whole_turn_panel = f"""
        <View whenTagName="turn_selector" whenChoiceValue="Turn {turn_num}" visibleWhen="choice-selected">
            <Collapse visibleWhen="$turn{turn_num}_dialogue[0].text">
                <Panel value="Turn {turn_num} - Whole Turn">
                    <View>
                        <Collapse>
                            <Panel value="Topic">
                                <Filter name="filter_topic_whole_{turn_num}" toName="topic_whole_{turn_num}" minlength="0" placeholder="Filter topics..."/>
                                <Choices name="topic_whole_{turn_num}" toName="conversation" choice="multiple">
                                    <Choice value="None" />
                                    <Choice value="Same Topics as prior conversation turn" />
                                    <Choice value="Adult &amp; Illicit Content" />
                                    <Choice value="Art &amp; Design" />
                                    <Choice value="Business &amp; Finances" />
                                    <Choice value="Culture" />
                                    <Choice value="Economics" />
                                    <Choice value="Education" />
                                    <Choice value="Employment &amp; Hiring" />
                                    <Choice value="Engineering &amp; Infrastructure" />
                                    <Choice value="Entertainment, Hobbies &amp; Leisure" />
                                    <Choice value="Fantasy / Fiction / Fanfiction" />
                                    <Choice value="Fashion &amp; Beauty" />
                                    <Choice value="Food &amp; Dining" />
                                    <Choice value="Geography" />
                                    <Choice value="Health &amp; Medicine" />
                                    <Choice value="History" />
                                    <Choice value="Housing" />
                                    <Choice value="Immigration / migration" />
                                    <Choice value="Insurance &amp; social scoring" />
                                    <Choice value="Interpersonal Relationships &amp; Communication" />
                                    <Choice value="Law, Criminal Justice, Law Enforcement" />
                                    <Choice value="Lifestyle" />
                                    <Choice value="Linguistics &amp; Languages" />
                                    <Choice value="Literature &amp; Writing" />
                                    <Choice value="Math &amp; Sciences" />
                                    <Choice value="Nature &amp; Environment" />
                                    <Choice value="News &amp; Current Affairs" />
                                    <Choice value="Politics &amp; Elections" />
                                    <Choice value="Psychology, Philosophy &amp; Human Behavior" />
                                    <Choice value="Religion &amp; Spirituality" />
                                    <Choice value="Social Issues &amp; Movements" />
                                    <Choice value="Sports" />
                                    <Choice value="Technology, Software &amp; Computing" />
                                    <Choice value="Transportation" />
                                    <Choice value="Travel &amp; Tourism" />
                                    <Choice value="Video Games" />
                                    <Choice value="Other" />
                                </Choices>
                            </Panel>
                        </Collapse>

                        <Collapse>
                            <Panel value="Other Feedback">
                                <TextArea name="other_feedback_{turn_num}" toName="conversation" 
                                          placeholder="Enter any additional feedback, observations, or notes about this turn..." 
                                          rows="4" maxSubmissions="1" editable="true" />
                            </Panel>
                        </Collapse>
                    </View>
                </Panel>
            </Collapse>
        </View>
"""
        turn_panels += prompt_panel + whole_turn_panel

    # Close the views
    closing_tags = """
    </View>
</View>
"""

    # Combine everything
    return base_view + turn_panels + closing_tags

# Generate the dynamic label configuration
LABEL_CONFIG = generate_dynamic_label_config()

def get_input_file():
    """Let user choose their input file."""
    # Define batch assignments
    BATCH_ASSIGNMENTS = {
        'batch_1.json': 'Ahmet',
        'batch_2.json': 'Anka',
        'batch_3.json': 'Cedric',
        'batch_4.json': 'Dayeon',
        'batch_5.json': 'Megan',
        'batch_6.json': 'Niloofar',
        'batch_7.json': 'Shayne',
        'batch_8.json': 'Victor',
        'batch_9.json': 'Wenting',
        'batch_10.json': 'Yuntian',
        'batch_11.json': 'Zhiping',
        'batch_12.json': 'Updated'
    }

    while True:
        data_files = list(DATA_DIR.glob("*.json*"))
        
        if not data_files:
            print("\n❌ No JSON/JSONL files found in data directory")
            print(f"Please add your tasks file to: {DATA_DIR}/")
            choice = input("\nPress 'r' to refresh after adding your file, or 'q' to quit: ").strip().lower()
            if choice == 'q':
                sys.exit(1)
            elif choice == 'r':
                continue
            else:
                print("Invalid choice. Please press 'r' to refresh or 'q' to quit.")
                continue
        
        print("\n📁 Available files:")
        for i, file in enumerate(data_files, 1):
            filename = file.name
            assignee = BATCH_ASSIGNMENTS.get(filename, '')
            # Add the assignee in parentheses if it exists
            display_name = f"{filename} ({assignee})" if assignee else filename
            print(f"{i}. {display_name}")
        
        print("\nOptions:")
        print("- Enter a number to select a file")
        print("- Press 'r' to refresh the list")
        print("- Press 'q' to quit")
        
        choice = input("\nYour choice: ").strip().lower()
        if choice == 'q':
            sys.exit(1)
        elif choice == 'r':
            continue
        
        try:
            file_index = int(choice) - 1
            if 0 <= file_index < len(data_files):
                chosen_file = data_files[file_index]
                break
            else:
                print("❌ Invalid choice. Please enter a number from the list.")
                continue
        except ValueError:
            print("❌ Invalid input. Please enter a number, 'r' to refresh, or 'q' to quit.")
            continue
    
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
    
    # Transform the data for dynamic turns
    print("🔄 Transforming data for dynamic turns...")
    transformed_file = input_file.with_name(f"{input_file.stem}_transformed.json")
    
    # Read the input file to get the actual number of turns
    with open(input_file, 'r') as f:
        tasks = json.load(f)
        # Calculate a reasonable maximum number of turns
        turn_counts = [(len(task["data"]["conversation"]) + 1) // 2 for task in tasks]
        turn_counts.sort()
        # Use the 95th percentile, capped at MAX_CHAT_TURNS
        percentile_95 = turn_counts[int(len(turn_counts) * 0.95)]
        reasonable_max = min(MAX_CHAT_TURNS, percentile_95)
        print(f"📊 Using a reasonable maximum of {reasonable_max} turns for transformation")
    
    if not transform_data(str(input_file), str(transformed_file), reasonable_max):
        print("❌ Error: Failed to transform data for dynamic turns.")
        sys.exit(1)
    
    return str(transformed_file)

def start_project():
    """Start a new Label Studio project with pre-configured settings."""
    api_key = get_api_key()
    
    # Initialize Label Studio client
    ls = Client(url=LABEL_STUDIO_URL, api_key=api_key)
    print(f"📡 Connecting to Label Studio at {LABEL_STUDIO_URL}...")

    try:
        # Prepare tasks file and get the actual number of turns
        tasks_file = prepare_tasks_file()
        
        # Read the transformed file to get the actual number of turns
        with open(tasks_file, 'r') as f:
            tasks = json.load(f)
            # Calculate a reasonable maximum number of turns
            turn_counts = [(len(task["data"]["conversation"]) + 1) // 2 for task in tasks]
            turn_counts.sort()
            
            # Use the 95th percentile, capped at MAX_CHAT_TURNS
            percentile_95 = turn_counts[int(len(turn_counts) * 0.95)]
            actual_max_turns = min(MAX_CHAT_TURNS, percentile_95)
            print(f"📊 Using {actual_max_turns} turns for the interface (95th percentile: {percentile_95}, MAX_CHAT_TURNS: {MAX_CHAT_TURNS})")
        
        # Create project with dynamic label config based on actual turns
        project_name = "DUP Taxonomy Annotation"
        print(f"🛠 Creating new project: {project_name}")
        label_config = generate_dynamic_label_config(actual_max_turns)
        project = ls.start_project(
            title=project_name,
            label_config=label_config,
        )
        print(f"🎉 Project created: {project.id}")
        
        # Import tasks
        print("📥 Importing initial tasks...")
        project.import_tasks(tasks_file)
        print(f"✅ Imported tasks from {tasks_file}")
        
        # Save the API key for future use
        print("\n💡 Tip: To skip this prompt next time, set your API key as an environment variable:")
        print(f"export LABEL_STUDIO_API_KEY={api_key}")
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print("❌ Error: Invalid API key")
            sys.exit(1)
        raise

if __name__ == "__main__":
    start_project()
