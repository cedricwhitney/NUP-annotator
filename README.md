# Conversation Project (Round 2)

A tool for annotating conversations using Label Studio. This project uses the open source version of [Label Studio](https://github.com/heartexlabs/label-studio) - many thanks to the Label Studio team for making this possible!

## Quick Start

0. Install prerequisites:
   - Python 3.x
   - Git (pre-installed on macOS, check version with `git --version`)
   - `make` command-line tool (pre-installed on Linux/Mac, Windows users: `choco install make`)
   - `uv` package manager:
     ```bash
     curl -LsSf https://astral.sh/uv/install.sh | sh
     ```
     After installing uv, you'll need to:
     - Close and reopen your terminal
     - Navigate back to your projects directory:
       ```bash
       cd path/to/project
       ```

1. Clone the repository:
   ```bash
   git clone https://github.com/cedricwhitney/NUP-annotator.git
   cd NUP-annotator
   ```

2. Set up the environment:
   ```bash
   make setup
   ```

3. Start Label Studio:

   If you're new to Label Studio or can't access your old account:
   ```bash
   make first-time-setup
   ```
   - Visit http://localhost:8080
   - Create a new account
   - Get your API key from Account & Settings > Access Token

   If you already have a Label Studio account:
   ```bash
   make label-studio
   ```
   - Visit http://localhost:8080 and log in
   - Your previous API key will still work
   - If needed, you can get your API key from Account & Settings > Access Token
   - Note: Your previous annotations are stored separately, so this is a fresh start for Round 2

4. Start your project:
   ```bash
   make start-project
   ```
   This will:
   - Pull the latest code and batch files
   - Show available batch files
   - Guide you to select your assigned batch
   - Set up a new project with your batch's conversations
   - Configure the correct taxonomy structure

## Overview

This project facilitates consistent annotation across multiple annotators:
- Each annotator runs their own local instance of Label Studio
- All instances are configured with the same taxonomy structure
- Annotators work independently on their local installations
- Results can be exported and compared across annotators
- Balanced batch assignments ensure even distribution of work
- Unique conversation IDs enable reliable tracking across batches

The setup ensures everyone has identical project configuration while maintaining independent workspaces.

## Data Organization

The project uses a structured approach to manage conversation data:

- **Master Sample File**: Contains all conversations with unique IDs
- **Batch Files**: Distributed tasks for each annotator
  - Each task is assigned to exactly 2 raters
  - Each rater gets 20 tasks
  - Balanced overlap between rater pairs
  - Robust against rater dropout

## Annotation Interface

The Label Studio interface is configured with:

- **Conversation Display**: Shows the full conversation with proper formatting
- **Turn Selection**: Allows annotators to focus on specific turns
- **Comprehensive Taxonomy**: Includes categories for:
  - Media Format
  - Function/Purpose
  - Topic Classification
  - Interaction Features
  - Restricted Flags
  - Prompt Quality
  - Answer Form
  - Self-Disclosure
- **Task Identification**: Displays conversation IDs for reference

## Annotation Export & Sharing

To save and share your annotations with other annotators:

1. Export your annotations:
   ```bash
   make export-data
   ```
   This will:
   - Pull the latest updates from other annotators
   - Export your annotations from Label Studio
   - Check for changes since your last export
   - Prompt you to share your annotations

2. When prompted, type 'y' to share your annotations with other annotators

Your annotations will be:
- Saved in `annotator_exports/[your_git_username]_annotations.json`
- Automatically shared with other annotators via GitHub
- Preserved with full history of all your exports

## Project Structure

The repository is organized as follows:

    conversation_project/
    ├── src/                      # Source code
    │   ├── core/                 # Core functionality
    │   │   ├── start_project.py      # Label Studio project setup
    │   │   └── label_studio_integration.py
    │   └── tools/                # Utility tools
    ├── tests/                    # Test suite
    ├── data/                     # Data directory
    │   └── batch_*.json             # Batch files for each annotator
    ├── annotator_exports/        # Exported annotations from all annotators
    └── Makefile                  # Project automation

## Common Tasks

Here are some common tasks and how to perform them:

1. Start Label Studio:
   ```bash
   make label-studio
   ```

2. Stop Label Studio:
   ```bash
   make stop-label-studio
   ```

3. Export your annotations:
   ```bash
   make export-data
   ```

4. List available files:
   ```bash
   make refresh-data
   ```

## Troubleshooting

If you encounter issues:
1. Ensure Python 3.x is installed: `python3 --version`
2. Check if Label Studio is running: http://localhost:8080
3. Try stopping and restarting Label Studio: `make stop-label-studio && make label-studio`
4. If project is missing: Run `make start-project` to set up the project structure
5. API key issues:
   - Your API key is specific to your Label Studio installation
   - Get a new key from Account & Settings > Access Token
   - Either enter it when prompted or set it as an environment variable:
     ```bash
     export LABEL_STUDIO_API_KEY=your_key_here
     ```

## Acknowledgments

This project uses [Label Studio](https://github.com/heartexlabs/label-studio), an open source data labeling tool. We're grateful to the Label Studio team for providing this excellent platform for annotation projects.

## Contributing

1. Make your changes to the relevant files
2. Check status of changes:
   ```bash
   git status
   ```

3. Stage your changes:
   ```bash
   git add .
   ```

4. Commit your changes:
   ```bash
   git commit -m "your descriptive message"
   ```

5. Push your changes:
   ```bash
   git push origin main
   ```

