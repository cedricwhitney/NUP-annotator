import os
import sys
import requests
from label_studio_sdk import Client
import json
from pathlib import Path
from src.tools.validate_labelstudio_json import validate_and_fix_json

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
        <Header value="Conversation ID: $conversation_id" style="margin-top: 1em; font-size: 0.9em; color: #555;"/>
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
        <View>
            <View whenTagName="turn_selector" whenChoiceValue="Turn {turn_num}" visibleWhen="choice-selected">
                <Collapse visibleWhen="$turn{turn_num}_dialogue[0].text">
                    <Panel value="Turn {turn_num} - Prompt">
                        <View>
                            <View style="margin-bottom: 1em;">
                                <Text name="turn_{turn_num}_prompt_warning" value="⚠️ Please complete all required fields for Turn {turn_num} - Prompt:" style="color: #ff6b6b; font-weight: bold;" />
                            </View>
                            <Collapse>
                                <Panel value="Media Format">
                                    <Filter name="filter_media_{turn_num}" toName="media_format_{turn_num}" minlength="0" placeholder="Filter media formats..."/>
                                    <Choices name="media_format_{turn_num}" toName="conversation" choice="multiple" required="true">
                                        <Choice value="Audio" />
                                        <Choice value="Charts / graphs" />
                                        <Choice value="Formatted enumeration / itemization" />
                                        <Choice value="HTML" />
                                        <Choice value="Images" />
                                        <Choice value="Likely retrieved / pasted content" />
                                        <Choice value="Math / symbols" />
                                        <Choice value="URLs" />
                                        <Choice value="Natural language" />
                                        <Choice value="Code" />
                                        <Choice value="Other" />
                                    </Choices>
                                </Panel>
                            </Collapse>
                            
                            <Collapse>
                                <Panel value="Function/Purpose">
                                    <Filter name="filter_function_{turn_num}" toName="function_purpose_{turn_num}" minlength="0" placeholder="Filter functions..."/>
                                    <Choices name="function_purpose_{turn_num}" toName="conversation" choice="multiple" required="true">
                                        <Choice value="Advice, guidance, &amp; recommendations: Instructions / how-to" />
                                        <Choice value="Advice, guidance, &amp; recommendations: Social and personal advice" />
                                        <Choice value="Advice, guidance, &amp; recommendations: Professional advice" />
                                        <Choice value="Advice, guidance, &amp; recommendations: Activity / product recommendations" />
                                        <Choice value="Advice, guidance, &amp; recommendations: Action planning (scheduling, robotics)" />
                                        <Choice value="Editorial &amp; formatting: Natural language content editing" />
                                        <Choice value="Editorial &amp; formatting: Natural language style or re-formatting" />
                                        <Choice value="Editorial &amp; formatting: Code content editing" />
                                        <Choice value="Editorial &amp; formatting: Code style and re-formatting" />
                                        <Choice value="Editorial &amp; formatting: Content summarization" />
                                        <Choice value="Editorial &amp; formatting: Content expansion" />
                                        <Choice value="Editorial &amp; formatting: Information processing &amp; re-formatting" />
                                        <Choice value="Information analysis: Content explanation / interpretation" />
                                        <Choice value="Information analysis: Content quality review or assessment" />
                                        <Choice value="Information analysis: Content classification" />
                                        <Choice value="Information analysis: Ranking or scoring" />
                                        <Choice value="Information analysis: Other content analysis / description" />
                                        <Choice value="Information retrieval: General info from web" />
                                        <Choice value="Information retrieval: General info from prompt content" />
                                        <Choice value="Reasoning: Mathematical or numerical problem solving" />
                                        <Choice value="Reasoning: Verbal problems, logic games, puzzles or riddles" />
                                        <Choice value="Reasoning: Other general problem solving" />
                                        <Choice value="Role-play / social simulation: Platonic companion / friend" />
                                        <Choice value="Role-play / social simulation: Romantic companion" />
                                        <Choice value="Role-play / social simulation: Simulation of real person / celebrity" />
                                        <Choice value="Role-play / social simulation: User study persona simulations or polling" />
                                        <Choice value="Role-play / social simulation: Therapist / coach" />
                                        <Choice value="Translation (language to language)" />
                                        <Choice value="Content generation: Brainstorming / ideation" />
                                        <Choice value="Content generation: Creative / fiction writing" />
                                        <Choice value="Content generation: Academic / essay" />
                                        <Choice value="Content generation: Administrative writing" />
                                        <Choice value="Content generation: Code" />
                                        <Choice value="Content generation: Code documentation" />
                                        <Choice value="Content generation: General prose, discussion or explanation" />
                                        <Choice value="Content generation: Prompts for another AI system" />
                                        <Choice value="Content generation: Other" />
                                        <Choice value="Other" />
                                        <Choice value="No clear ask" />
                                    </Choices>
                                </Panel>
                            </Collapse>

                            <Collapse>
                                <Panel value="Multi-turn Relationship">
                                    <Choices name="multi_turn_relationship_{turn_num}" toName="conversation" choice="single" required="true">
                                        <Choice value="First request" />
                                        <Choice value="Unrelated request" />
                                        <Choice value="Same / similar task, new request" />
                                        <Choice value="Repeated / revision request" />
                                        <Choice value="New task, related request" />
                                    </Choices>
                                </Panel>
                            </Collapse>

                            <Collapse>
                                <Panel value="Interaction Features">
                                    <Choices name="interaction_features_{turn_num}" toName="conversation" choice="multiple" required="true">
                                        <Choice value="Companionship" />
                                        <Choice value="Courtesy / politeness" />
                                        <Choice value="Jailbreak attempt" />
                                        <Choice value="Reinforcement / praise" />
                                        <Choice value="Role-assignment" />
                                        <Choice value="None" />
                                    </Choices>
                                </Panel>
                            </Collapse>

                            <Collapse>
                                <Panel value="Restricted Flags">
                                    <Filter name="filter_flags_{turn_num}" toName="restricted_flags_{turn_num}" minlength="0" placeholder="Filter flags..."/>
                                    <Choices name="restricted_flags_{turn_num}" toName="conversation" choice="multiple" required="true">
                                        <Choice value="Sexually explicit content: Fictitious person" />
                                        <Choice value="Sexually explicit content: Real person" />
                                        <Choice value="Sexually explicit content: Request / discussion of CSAM" />
                                        <Choice value="Sexually explicit content: Other" />
                                        <Choice value="CBRN-related outputs" />
                                        <Choice value="Criminal planning or other suspected illegal activity not listed elsewhere" />
                                        <Choice value="Cyberattacks" />
                                        <Choice value="Discriminatory practices" />
                                        <Choice value="Generating defamatory content" />
                                        <Choice value="Generating spam" />
                                        <Choice value="Impersonation attempts" />
                                        <Choice value="Inciting violence, hateful or other harmful behavior: Harassment &amp; bullying" />
                                        <Choice value="Inciting violence, hateful or other harmful behavior: Physical harm" />
                                        <Choice value="Inciting violence, hateful or other harmful behavior: Self-harm" />
                                        <Choice value="Misinformation" />
                                        <Choice value="Output misrepresentation: Automated decision-making without disclosure" />
                                        <Choice value="Output misrepresentation: Disclaiming AI use" />
                                        <Choice value="Possible presence of copyrighted, unreferenced material" />
                                        <Choice value="Potential violation of external policy / ethics" />
                                        <Choice value="Privacy concerns: Possible identifiable information" />
                                        <Choice value="Privacy concerns: Possible sensitive information" />
                                        <Choice value="Weapons &amp; drugs" />
                                        <Choice value="Other" />
                                        <Choice value="None" />
                                    </Choices>
                                </Panel>
                            </Collapse>

                            <Collapse>
                                <Panel value="Other Feedback">
                                    <TextArea name="other_feedback_prompt_{turn_num}" toName="conversation" 
                                              placeholder="Enter any additional feedback, observations, or notes about this turn (including 'other' selections)..." 
                                              rows="4" maxSubmissions="1" editable="true" />
                                </Panel>
                            </Collapse>
                        </View>
                    </Panel>
                </Collapse>
            </View>
        </View>
"""

        # Create panel for the response
        response_panel = f"""
        <View>
            <View whenTagName="turn_selector" whenChoiceValue="Turn {turn_num}" visibleWhen="choice-selected">
                <Collapse visibleWhen="$turn{turn_num}_dialogue[1].text">
                    <Panel value="Turn {turn_num} - Response">
                        <View>
                            <View style="margin-bottom: 1em;">
                                <Text name="turn_{turn_num}_response_warning" value="⚠️ Please complete all required fields for Turn {turn_num} - Response:" style="color: #ff6b6b; font-weight: bold;" />
                            </View>
                            <Collapse>
                                <Panel value="Media Format">
                                    <Filter name="filter_media_response_{turn_num}" toName="media_format_response_{turn_num}" minlength="0" placeholder="Filter media formats..."/>
                                    <Choices name="media_format_response_{turn_num}" toName="conversation" choice="multiple" required="true">
                                        <Choice value="Audio" />
                                        <Choice value="Charts / graphs" />
                                        <Choice value="Formatted enumeration / itemization" />
                                        <Choice value="HTML" />
                                        <Choice value="Images" />
                                        <Choice value="Likely retrieved / pasted content" />
                                        <Choice value="Math / symbols" />
                                        <Choice value="URLs" />
                                        <Choice value="Natural language" />
                                        <Choice value="Code" />
                                        <Choice value="Other" />
                                    </Choices>
                                </Panel>
                            </Collapse>

                            <Collapse>
                                <Panel value="Answer Form">
                                    <Choices name="answer_form_response_{turn_num}" toName="conversation" choice="single" required="true">
                                        <Choice value="Refusal to answer (with explanation)" />
                                        <Choice value="Refusal to answer (without explanation)" />
                                        <Choice value="Partial refusal / expressing uncertainty / disclaiming" />
                                        <Choice value="Direct answer / open generation" />
                                        <Choice value="Continuation of input" />
                                    </Choices>
                                </Panel>
                            </Collapse>

                            <Collapse>
                                <Panel value="Interaction Features">
                                    <Choices name="interaction_features_response_{turn_num}" toName="conversation" choice="multiple" required="true">
                                        <Choice value="Apology" />
                                        <Choice value="Content: Direct response" />
                                        <Choice value="Content: Preferences / feelings / opinions / religious beliefs" />
                                        <Choice value="Content: Empathy" />
                                        <Choice value="Register and style: Phatic expressions" />
                                        <Choice value="Register and style: Expressions of confidence and doubt" />
                                        <Choice value="Non-personalization" />
                                        <Choice value="Self-disclosure" />
                                        <Choice value="None" />
                                    </Choices>
                                </Panel>
                            </Collapse>

                            <Collapse>
                                <Panel value="Restricted Flags">
                                    <Filter name="filter_flags_response_{turn_num}" toName="restricted_flags_response_{turn_num}" minlength="0" placeholder="Filter flags..."/>
                                    <Choices name="restricted_flags_response_{turn_num}" toName="conversation" choice="multiple" required="true">
                                        <Choice value="Sexually explicit content: Fictitious person" />
                                        <Choice value="Sexually explicit content: Real person" />
                                        <Choice value="Sexually explicit content: Request / discussion of CSAM" />
                                        <Choice value="Sexually explicit content: Other" />
                                        <Choice value="CBRN-related outputs" />
                                        <Choice value="Criminal planning or other suspected illegal activity not listed elsewhere" />
                                        <Choice value="Cyberattacks" />
                                        <Choice value="Discriminatory practices" />
                                        <Choice value="Generating defamatory content" />
                                        <Choice value="Generating spam" />
                                        <Choice value="Impersonation attempts" />
                                        <Choice value="Inciting violence, hateful or other harmful behavior: Harassment &amp; bullying" />
                                        <Choice value="Inciting violence, hateful or other harmful behavior: Physical harm" />
                                        <Choice value="Inciting violence, hateful or other harmful behavior: Self-harm" />
                                        <Choice value="Misinformation" />
                                        <Choice value="Output misrepresentation: Automated decision-making without disclosure" />
                                        <Choice value="Output misrepresentation: Disclaiming AI use" />
                                        <Choice value="Possible presence of copyrighted, unreferenced material" />
                                        <Choice value="Potential violation of external policy / ethics" />
                                        <Choice value="Privacy concerns: Possible identifiable information" />
                                        <Choice value="Privacy concerns: Possible sensitive information" />
                                        <Choice value="Weapons &amp; drugs" />
                                        <Choice value="Other" />
                                        <Choice value="None" />
                                    </Choices>
                                </Panel>
                            </Collapse>

                            <Collapse>
                                <Panel value="Other Feedback">
                                    <TextArea name="other_feedback_response_{turn_num}" toName="conversation" 
                                              placeholder="Enter any additional feedback, observations, or notes about this turn (including 'other' selections)..." 
                                              rows="4" maxSubmissions="1" editable="true" />
                                </Panel>
                            </Collapse>
                        </View>
                    </Panel>
                </Collapse>
            </View>
        </View>
"""
       
        # Create panel for the whole panel
        whole_panel = f"""
            <View>
                <View whenTagName="turn_selector" whenChoiceValue="Turn {turn_num}" visibleWhen="choice-selected">
                    <Collapse visibleWhen="$turn{turn_num}_dialogue[1].text">
                        <Panel value="Turn {turn_num} - Whole Turn">
                            <View>
                                <View style="margin-bottom: 1em;">
                                    <Text name="turn_{turn_num}_whole_turn_warning" value="⚠️ Please complete all required fields for Turn {turn_num} - Whole Turn:" style="color: #ff6b6b; font-weight: bold;" />
                                </View>
                                <Collapse>
                                    <Panel value="Topic">
                                        <Filter name="filter_topic_turn_whole_{turn_num}" toName="topic_turn_whole_{turn_num}" minlength="0" placeholder="Filter topics..."/>
                                        <Choices name="topic_turn_whole_{turn_num}" toName="conversation" choice="multiple" required="true">
                                            <Choice value="Adult &amp; illicit content" />
                                            <Choice value="Art &amp; design" />
                                            <Choice value="Business &amp; finances" />
                                            <Choice value="Culture" />
                                            <Choice value="Economics" />
                                            <Choice value="Education" />
                                            <Choice value="Employment &amp; hiring" />
                                            <Choice value="Entertainment, hobbies &amp; leisure" />
                                            <Choice value="Fantasy / fiction / fanfiction" />
                                            <Choice value="Fashion &amp; beauty" />
                                            <Choice value="Food &amp; dining" />
                                            <Choice value="Geography" />
                                            <Choice value="Health &amp; medicine" />
                                            <Choice value="History" />
                                            <Choice value="Housing" />
                                            <Choice value="Immigration / migration" />
                                            <Choice value="Insurance &amp; social scoring" />
                                            <Choice value="Interpersonal relationships &amp; communication" />
                                            <Choice value="Law, criminal justice, law enforcement" />
                                            <Choice value="Lifestyle" />
                                            <Choice value="Linguistics &amp; languages" />
                                            <Choice value="Literature &amp; writing" />
                                            <Choice value="Math &amp; sciences" />
                                            <Choice value="Nature &amp; environment" />
                                            <Choice value="News &amp; current affairs" />
                                            <Choice value="Non-software engineering &amp; infrastructure" />
                                            <Choice value="Politics &amp; elections" />
                                            <Choice value="Psychology, philosophy &amp; human behavior" />
                                            <Choice value="Religion &amp; spirituality" />
                                            <Choice value="Same topics as prior conversation turn" />
                                            <Choice value="Social issues &amp; movements" />
                                            <Choice value="Sports" />
                                            <Choice value="Technology, software &amp; computing" />
                                            <Choice value="Transportation" />
                                            <Choice value="Travel &amp; tourism" />
                                            <Choice value="Video games" />
                                            <Choice value="Other" />
                                            <Choice value="None" />
                                        </Choices>
                                    </Panel>
                                </Collapse>
                                
                                <Collapse>
                                    <Panel value="Other Feedback">
                                        <TextArea name="other_feedback_response_{turn_num}" toName="conversation" 
                                                placeholder="Enter any additional feedback, observations, or notes about this turn (including 'other' selections)..." 
                                                rows="4" maxSubmissions="1" editable="true" />
                                    </Panel>
                                </Collapse>
                            </View>
                        </Panel>
                    </Collapse>
                </View>
            </View>
"""
        turn_panels += prompt_panel + response_panel + whole_panel

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
        'batch_12.json': 'ZSuperhero'
    }

    while True:
        # Only look for batch files
        data_files = list(DATA_DIR.glob("batch_*.json"))
        
        if not data_files:
            print("\n❌ No batch files found in data directory")
            print(f"Please add your batch file to: {DATA_DIR}/")
            choice = input("\nPress 'r' to refresh after adding your file, or 'q' to quit: ").strip().lower()
            if choice == 'q':
                sys.exit(1)
            elif choice == 'r':
                continue
            else:
                print("Invalid choice. Please press 'r' to refresh or 'q' to quit.")
                continue
        
        print()  # Just add a newline for spacing
        # Create a list of tuples (filename, display_name) sorted by assignee name
        display_files = []
        for file in data_files:
            filename = file.name
            assignee = BATCH_ASSIGNMENTS.get(filename, '')
            # Add the assignee in parentheses if it exists
            display_name = f"{filename} ({assignee})" if assignee else filename
            # Sort by assignee name (or filename if no assignee)
            sort_key = assignee if assignee else filename
            display_files.append((filename, display_name, sort_key, file))
        
        # Sort by assignee name and print
        sorted_files = sorted(display_files, key=lambda x: x[2].lower())
        for i, (filename, display_name, _, _) in enumerate(sorted_files, 1):
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
            if 0 <= file_index < len(sorted_files):
                chosen_file = sorted_files[file_index][3]  # Get the Path object from the tuple
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
    
    # Validate the JSON format
    print("🔍 Validating JSON format...")
    if not validate_and_fix_json(str(input_file)):
        print("❌ Error: Invalid JSON format. Please fix the format and try again.")
        sys.exit(1)
    
    # Read the input file to get the actual number of turns
    with open(input_file, 'r') as f:
        tasks = json.load(f)
        # Calculate a reasonable maximum number of turns
        turn_counts = [(len(task["data"]["conversation"]) + 1) // 2 for task in tasks]
        turn_counts.sort()
        # Use the 95th percentile, capped at MAX_CHAT_TURNS
        percentile_95 = turn_counts[int(len(turn_counts) * 0.95)]
        reasonable_max = min(MAX_CHAT_TURNS, percentile_95)
        print(f"📊 Using a reasonable maximum of {reasonable_max} turns for the interface")
    
    return str(input_file)

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
        project_name = "DUP Taxonomy Annotation (Round 2)"
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
