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
        print("\nNote: The terminal will keep scrolling with Label Studio logs.")
        print("Don't worry - just paste your API key and press Enter!\n")
        api_key = input("Enter your API key: ").strip()
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
            <Panel value="1st Prompt">
                <View>
                    <Collapse>
                        <Panel value="Media Format">
                            <Filter name="filter_media_1" toName="media_format_1" minlength="0" placeholder="Filter media formats..."/>
                            <Choices name="media_format_1" toName="conversation" choice="multiple">
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
                        </Panel>
                    </Collapse>
                    
                    <Collapse>
                        <Panel value="Function/Purpose">
                            <Filter name="filter_function_1" toName="function_purpose_1" minlength="0" placeholder="Filter functions..."/>
                            <Choices name="function_purpose_1" toName="conversation" choice="multiple">
                                <Choice value="Information retrieval: general info from web" />
                                <Choice value="Information retrieval: general info from prompt content" />
                                <Choice value="Content generation: brainstorming / ideation" />
                                <Choice value="Content generation: creative / fiction writing" />
                                <Choice value="Content generation: non-fiction / academic / essay writing" />
                                <Choice value="Content generation: administrative writing" />
                                <Choice value="Content generation: code" />
                                <Choice value="Content generation: code documentation" />
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
                                <Choice value="Translation (language to language)" />
                                <Choice value="Role-play / social simulation: platonic companion / friend" />
                                <Choice value="Role-play / social simulation: romantic companion" />
                                <Choice value="Role-play / social simulation: simulation of real person / celebrity" />
                                <Choice value="Role-play / social simulation: user study persona simulations or polling" />
                                <Choice value="Role-play / social simulation: therapist / coach" />
                                <Choice value="Advice, Guidance, &amp; Recommendations: Instructions / How-to" />
                                <Choice value="Advice, Guidance, &amp; Recommendations: Social and personal advice" />
                                <Choice value="Advice, Guidance, &amp; Recommendations: Professional advice" />
                                <Choice value="Advice, Guidance, &amp; Recommendations: Activity / product recommendations" />
                                <Choice value="Advice, Guidance, &amp; Recommendations: Action planning (scheduling, robotics)" />
                                <Choice value="Reasoning: Mathematical or numerical problem solving" />
                                <Choice value="Reasoning: Verbal problems, logic games, puzzles or riddles" />
                                <Choice value="Reasoning: Other general problem solving" />
                                <Choice value="Other" />
                            </Choices>
                        </Panel>
                    </Collapse>

                    <Collapse>
                        <Panel value="Multi-turn Relationship">
                            <Choices name="multi_turn_relationship_1" toName="conversation" choice="single">
                                <Choice value="First request" />
                                <Choice value="Unrelated request" />
                                <Choice value="Same task, new request" />
                                <Choice value="Repeat request" />
                                <Choice value="Related request" />
                            </Choices>
                        </Panel>
                    </Collapse>

                    <Collapse>
                        <Panel value="Anthropomorphization">
                            <Choices name="anthropomorphization_1" toName="conversation" choice="single">
                                <Choice value="Yes" />
                                <Choice value="No" />
                            </Choices>
                        </Panel>
                    </Collapse>

                    <Collapse>
                        <Panel value="Restricted Flags">
                            <Filter name="filter_flags_1" toName="restricted_flags_1" minlength="0" placeholder="Filter flags..."/>
                            <Choices name="restricted_flags_1" toName="conversation" choice="multiple">
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
                        </Panel>
                    </Collapse>
                </View>
            </Panel>
        </Collapse>

        <Collapse>
            <Panel value="1st Response">
                <View>
                    <Collapse>
                        <Panel value="Media Format">
                            <Filter name="filter_media_response_1" toName="media_format_response_1" minlength="0" placeholder="Filter media formats..."/>
                            <Choices name="media_format_response_1" toName="conversation" choice="multiple">
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
                        </Panel>
                    </Collapse>

                    <Collapse>
                        <Panel value="Answer Form">
                            <Choices name="answer_form_1" toName="conversation" choice="single">
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
                        <Choices name="self_disclosure_1" toName="conversation" choice="single">
                                <Choice value="Yes" />
                                <Choice value="No" />
                            </Choices>
                        </Panel>
                    </Collapse>

                    <Collapse>
                        <Panel value="Restricted Flags">
                            <Filter name="filter_flags_response_1" toName="restricted_flags_response_1" minlength="0" placeholder="Filter flags..."/>
                        <Choices name="restricted_flags_response_1" toName="conversation" choice="multiple">
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
                        </Panel>
                    </Collapse>
                </View>
            </Panel>
        </Collapse>

        <Collapse>
            <Panel value="2nd Prompt">
                <View>
                    <Collapse>
                        <Panel value="Media Format">
                            <Filter name="filter_media_2" toName="media_format_2" minlength="0" placeholder="Filter media formats..."/>
                            <Choices name="media_format_2" toName="conversation" choice="multiple">
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
                        </Panel>    
                    </Collapse>

                    <Collapse>
                        <Panel value="Function/Purpose">
                            <Filter name="filter_function_2" toName="function_purpose_2" minlength="0" placeholder="Filter functions..."/>
                            <Choices name="function_purpose_2" toName="conversation" choice="multiple">
                                <Choice value="Information retrieval: general info from web" />
                                <Choice value="Information retrieval: general info from prompt content" />
                                <Choice value="Content generation: brainstorming / ideation" />
                                <Choice value="Content generation: creative / fiction writing" />
                                <Choice value="Content generation: non-fiction / academic / essay writing" />
                                <Choice value="Content generation: administrative writing" />
                                <Choice value="Content generation: code" />
                                <Choice value="Content generation: code documentation" />
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
                                <Choice value="Translation (language to language)" />
                                <Choice value="Role-play / social simulation: platonic companion / friend" />
                                <Choice value="Role-play / social simulation: romantic companion" />
                                <Choice value="Role-play / social simulation: simulation of real person / celebrity" />
                                <Choice value="Role-play / social simulation: user study persona simulations or polling" />
                                <Choice value="Role-play / social simulation: therapist / coach" />
                                <Choice value="Advice, Guidance, &amp; Recommendations: Instructions / How-to" />
                                <Choice value="Advice, Guidance, &amp; Recommendations: Social and personal advice" />
                                <Choice value="Advice, Guidance, &amp; Recommendations: Professional advice" />
                                <Choice value="Advice, Guidance, &amp; Recommendations: Activity / product recommendations" />
                                <Choice value="Advice, Guidance, &amp; Recommendations: Action planning (scheduling, robotics)" />
                                <Choice value="Reasoning: Mathematical or numerical problem solving" />
                                <Choice value="Reasoning: Verbal problems, logic games, puzzles or riddles" />
                                <Choice value="Reasoning: Other general problem solving" />
                                <Choice value="Other" />
                            </Choices>
                        </Panel>
                    </Collapse>

                    <Collapse>
                        <Panel value="Multi-turn Relationship">
                            <Choices name="multi_turn_relationship_2" toName="conversation" choice="single">
                                <Choice value="First request" />
                                <Choice value="Unrelated request" />
                                <Choice value="Same task, new request" />
                                <Choice value="Repeat request" />
                                <Choice value="Related request" />
                            </Choices>
                        </Panel>
                    </Collapse>

                    <Collapse>
                        <Panel value="Anthropomorphization">
                            <Choices name="anthropomorphization_2" toName="conversation" choice="single">
                                <Choice value="Yes" />
                                <Choice value="No" />
                            </Choices>
                        </Panel>
                    </Collapse>

                    <Collapse>
                        <Panel value="Restricted Flags">
                            <Filter name="filter_flags_2" toName="restricted_flags_2" minlength="0" placeholder="Filter flags..."/>
                             <Choices name="restricted_flags_2" toName="conversation" choice="multiple">
                                `<Choice value="Inciting violence, hateful or other harmful behavior: harassment &amp; bullying" />
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
                        </Panel>
                    </Collapse>
                </View>
            </Panel>
        </Collapse>

        <Collapse>
            <Panel value="2nd Response">
                <View>
                    <Collapse>
                        <Panel value="Media Format">
                            <Filter name="filter_media_response_2" toName="media_format_response_2" minlength="0" placeholder="Filter media formats..."/>
                            <Choices name="media_format_response_2" toName="conversation" choice="multiple">
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
                        </Panel>
                    </Collapse>

                    <Collapse>
                        <Panel value="Answer Form">
                            <Choices name="answer_form_2" toName="conversation" choice="single">
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
                            <Choices name="self_disclosure_2" toName="conversation" choice="single">
                                <Choice value="Yes" />
                                <Choice value="No" />
                            </Choices>
                        </Panel>
                    </Collapse>

                    <Collapse>
                        <Panel value="Restricted Flags">
                            <Filter name="filter_flags_response_2" toName="restricted_flags_response_2" minlength="0" placeholder="Filter flags..."/>
                            <Choices name="restricted_flags_response_2" toName="conversation" choice="multiple">
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
                        </Panel>
                    </Collapse>
                </View>
            </Panel>
        </Collapse>

        <Collapse>
            <Panel value="3rd Prompt">
                <View>
                    <Collapse>
                        <Panel value="Media Format">
                            <Filter name="filter_media_3" toName="media_format_3" minlength="0" placeholder="Filter media formats..."/>
                            <Choices name="media_format_3" toName="conversation" choice="multiple">
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
                        </Panel>
                    </Collapse>

                    <Collapse>
                        <Panel value="Function/Purpose">
                            <Filter name="filter_function_3" toName="function_purpose_3" minlength="0" placeholder="Filter functions..."/>
                            <Choices name="function_purpose_3" toName="conversation" choice="multiple">
                                <Choice value="Information retrieval: general info from web" />
                                <Choice value="Information retrieval: general info from prompt content" />
                                <Choice value="Content generation: brainstorming / ideation" />
                                <Choice value="Content generation: creative / fiction writing" />
                                <Choice value="Content generation: non-fiction / academic / essay writing" />
                                <Choice value="Content generation: administrative writing" />
                                <Choice value="Content generation: code" />
                                <Choice value="Content generation: code documentation" />
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
                                <Choice value="Translation (language to language)" />
                                <Choice value="Role-play / social simulation: platonic companion / friend" />
                                <Choice value="Role-play / social simulation: romantic companion" />
                                <Choice value="Role-play / social simulation: simulation of real person / celebrity" />
                                <Choice value="Role-play / social simulation: user study persona simulations or polling" />
                                <Choice value="Role-play / social simulation: therapist / coach" />
                                <Choice value="Advice, Guidance, &amp; Recommendations: Instructions / How-to" />
                                <Choice value="Advice, Guidance, &amp; Recommendations: Social and personal advice" />
                                <Choice value="Advice, Guidance, &amp; Recommendations: Professional advice" />
                                <Choice value="Advice, Guidance, &amp; Recommendations: Activity / product recommendations" />
                                <Choice value="Advice, Guidance, &amp; Recommendations: Action planning (scheduling, robotics)" />
                                <Choice value="Reasoning: Mathematical or numerical problem solving" />
                                <Choice value="Reasoning: Verbal problems, logic games, puzzles or riddles" />
                                <Choice value="Reasoning: Other general problem solving" />
                                <Choice value="Other" />
                            </Choices>
                        </Panel>
                    </Collapse>

                    <Collapse>
                        <Panel value="Multi-turn Relationship">
                            <Choices name="multi_turn_relationship_3" toName="conversation" choice="single">
                                <Choice value="First request" />
                                <Choice value="Unrelated request" />
                                <Choice value="Same task, new request" />
                                <Choice value="Repeat request" />
                                <Choice value="Related request" />
                            </Choices>
                        </Panel>
                    </Collapse>

                    <Collapse>
                        <Panel value="Anthropomorphization">
                            <Choices name="anthropomorphization_3" toName="conversation" choice="single">
                                <Choice value="Yes" />
                                <Choice value="No" />
                            </Choices>
                        </Panel>
                    </Collapse>

                    <Collapse>
                        <Panel value="Restricted Flags">
                            <Filter name="filter_flags_3" toName="restricted_flags_3" minlength="0" placeholder="Filter flags..."/>
                            <Choices name="restricted_flags_3" toName="conversation" choice="multiple">
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
                        </Panel>
                    </Collapse>
                </View>
            </Panel>
        </Collapse>

        <Collapse>
            <Panel value="3rd Response">
                <View>
                    <Collapse>
                        <Panel value="Media Format">
                            <Filter name="filter_media_response_3" toName="media_format_response_3" minlength="0" placeholder="Filter media formats..."/>
                            <Choices name="media_format_response_3" toName="conversation" choice="multiple">
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
                        </Panel>
                    </Collapse>

                    <Collapse>
                        <Panel value="Answer Form">
                            <Choices name="answer_form_3" toName="conversation" choice="single">
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
                            <Choices name="self_disclosure_3" toName="conversation" choice="single">
                                <Choice value="Yes" />
                                <Choice value="No" />
                            </Choices>
                        </Panel>
                    </Collapse>

                    <Collapse>
                        <Panel value="Restricted Flags">
                            <Filter name="filter_flags_response_3" toName="restricted_flags_response_3" minlength="0" placeholder="Filter flags..."/>
                            <Choices name="restricted_flags_response_3" toName="conversation" choice="multiple">
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
    while True:
        # Use DATA_DIR instead of creating new Path
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
        
        if len(data_files) == 1:
            chosen_file = data_files[0]
            print(f"📁 Found file: {chosen_file}")
        else:
            print("\n📁 Available files:")
            for i, file in enumerate(data_files, 1):
                print(f"{i}. {file}")
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
    
    return str(input_file)

def start_project():
    """Start a new Label Studio project with pre-configured settings."""
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
    start_project()
