import os
from label_studio_sdk import Client

LABEL_STUDIO_URL = os.getenv("LABEL_STUDIO_URL", "http://localhost:8080")
LABEL_STUDIO_API_KEY = os.getenv("LABEL_STUDIO_API_KEY", "712b782e7e9f192994ceec6044bc6c24bd953dda")
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

def main():
    # Initialize Label Studio client
    ls = Client(url=LABEL_STUDIO_URL, api_key=LABEL_STUDIO_API_KEY)
    print(f"📡 Connecting to Label Studio at {LABEL_STUDIO_URL}...")

    project_name = "DUP Taxonomy Annotation"
    print(f"🛠 Creating new project: {project_name}")
    project = ls.start_project(
        title=project_name,
        label_config=LABEL_CONFIG,
    )
    print(f"🎉 Project created: {project.id}")

if __name__ == "__main__":
    main()
