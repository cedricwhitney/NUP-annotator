# Conversation Project

A tool for annotating conversations using Label Studio. This project uses the open source version of [Label Studio](https://github.com/heartexlabs/label-studio) - many thanks to the Label Studio team for making this possible!

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
- **Batch Files**: Generated using Balanced Incomplete Block Design (BIBD)
  - Each task is assigned to exactly 2 raters
  - Each rater gets 20 tasks
  - Balanced overlap between rater pairs
  - Robust against rater dropout
- **Transformed Files**: Processed versions ready for Label Studio
  - Preserves conversation IDs across transformations
  - Maintains consistent formatting
  - Supports dynamic number of turns

## Data Transformation

The project includes tools for transforming conversation data for annotation:

- **Dynamic Turn Support**: Automatically processes conversations with varying numbers of turns
- **Role Standardization**: Normalizes different role names to "User" and "LLM"
- **Task Identification**: Uses persistent conversation IDs for reliable tracking
- **Format Preservation**: Maintains whitespace and formatting in the conversation text

To transform batch files for Label Studio:
```bash
make transform-batches
```

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

## Analysis Tools

The project includes a comprehensive suite of tools for analyzing inter-rater agreement between annotators. See the [Analysis Documentation](src/analysis/README.md) for details on:

- Agreement calculation methodology
- Generated reports and visualizations
- Implementation details
- Usage instructions

To run the analysis:
```bash
python src/tools/analyze_agreement.py
```

This will generate detailed agreement reports in the `reports/` directory.

## Utility Tools

The project includes several utility tools:

- **analyze_turns.py**: Analyzes the number of turns in conversations and provides statistics
- **extract_long_conversation.py**: Extracts and displays the longest conversation in a dataset
- **check_turns.py**: Checks the turn structure in transformed data
- **convert_jsonl_to_json.py**: Converts JSONL files to JSON format
- **validate_labelstudio_json.py**: Validates JSON files for Label Studio compatibility

## Prerequisites

- Python 3.x
- Git (pre-installed on macOS, check version with `git --version`)
- `make` command-line tool
  - **Linux/Mac**: Usually pre-installed
  - **Windows**: Install via [chocolatey](https://chocolatey.org/): `choco install make`
- `uv` package manager (installed automatically if missing)

## Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/cedricwhitney/NUP-annotator.git
   cd NUP-annotator
   ```

2. Set up the environment:
   ```bash
   make setup
   ```

3. Start Label Studio and create your account:
   ```bash
   make first-time-setup
   ```
   - Visit http://localhost:8080
   - Create an account
   - Get your API key from Account & Settings > Access Token

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
    ├── src/
    │   ├── core/                 # Core functionality
    │   │   ├── start_project.py      # Label Studio project setup
    │   │   └── label_studio_integration.py
    │   └── tools/                # Utility tools
    │       ├── add_conversation_ids.py    # Add unique IDs to master file
    │       ├── create_balanced_batches.py # Create balanced batch assignments
    │       ├── transform_all_batches.py   # Transform batches for Label Studio
    │       ├── transform_data_for_dynamic_turns.py  # Transform single batch
    │       └── validate_labelstudio_json.py  # Validate JSON format
    ├── tests/                    # Test suite
    │   └── tools/                # Tests for utility tools
    ├── data/                     # Data directory
    │   ├── master_sample_file.json   # Master file with all conversations
    │   ├── batch_*.json             # Batch files for each annotator
    │   └── batch_*_transformed.json  # Transformed files for Label Studio
    ├── annotator_exports/        # Exported annotations from all annotators
    └── Makefile                  # Project automation

## Common Tasks

Here are some common tasks and how to perform them:

1. Get latest updates:
   ```bash
   make sync-repo
   ```

2. Transform batch files:
   ```bash
   make transform-batches
   ```

3. Start Label Studio:
   ```bash
   make label-studio
   ```

4. Stop Label Studio:
   ```bash
   make stop-label-studio
   ```

5. List available files:
   ```bash
   make refresh-data
   ```

6. Run tests:
   ```bash
   make test
   ```

## Testing

The test suite covers core functionality:

- Batch assignment validation
- Conversation ID persistence
- JSON format validation
- Data transformation accuracy
- Label Studio integration

Run all tests with:
```bash
make test
```

## Core Features
- Project setup and configuration
- JSON validation
- Label Studio integration

## Optional Tools
- CSV to Label Studio JSON conversion (with tests in tests/tools/)
- JSON format fixing

## Data Tools

### File Format Support

The project supports both JSON and JSONL formats:
- JSON: Array of tasks in Label Studio format
- JSONL: One task per line in Label Studio format

When running `make start-project`:
1. All JSON/JSONL files in your data directory will be listed
2. You'll be prompted to choose which file to use
3. JSONL files are automatically converted to JSON
4. The file is validated for Label Studio compatibility

Example formats:
```jsonl
{"conversation": [{"role": "human", "text": "Hello"}, {"role": "assistant", "text": "Hi"}]}
{"conversation": [{"role": "human", "text": "How are you"}, {"role": "assistant", "text": "Good"}]}
```

or

```json
[
  {
    "data": {
      "conversation": [
        {"role": "human", "text": "Hello"},
        {"role": "assistant", "text": "Hi"}
      ]
    }
  }
]
```

### JSON Validation

Before importing tasks into Label Studio, you can validate and fix your JSON format:

```bash
# Just validate
make validate-json

# Validate and fix
python src/tools/validate_labelstudio_json.py input.json fixed_output.json
```

The validator will:
- Check JSON structure
- Attempt to fix common issues
- Provide detailed error messages
- Optionally save a fixed version

### CSV Conversion

For creating new datasets, you can convert CSV files to Label Studio format:

1. Edit the file paths in `src/tools/csv_to_labelstudio.py`:
   ```python
   # Input and output file paths - edit these to change your files
   csv_file = "data/your_input.csv"    # Your input CSV file
   json_file = "data/your_output.json" # Where to save the JSON
   ```

2. Run the conversion:
   ```bash
   make convert-csv
   ```

The script expects a CSV with columns "Turn 0" through "Turn 4":
```csv
Turn 0,Turn 1,Turn 2,Turn 3,Turn 4
"Hello","Hi there","How are you?","I'm good","Great!"
```

## Required JSON Format

Your JSON file must follow this structure for Label Studio:
```json
[
  {
    "data": {
      "conversation": [
        {
          "text": "Hello, how are you?",
          "role": "human"
        },
        {
          "text": "I'm doing well, thank you!",
          "role": "assistant"
        }
      ]
    }
  }
]
```

## Troubleshooting

If you encounter issues:
1. Ensure Python 3.x is installed: `python3 --version`
2. Check if Label Studio is running: http://localhost:8080
3. Try stopping and restarting Label Studio: `make stop-label-studio && make run`
4. If project is missing: Run `make start-project` to set up the project structure
5. If JSON import fails: Run `make validate-json` to check your data format
6. API key issues:
   - Your API key is specific to your Label Studio installation
   - Get a new key from Account & Settings > Access Token
   - Either enter it when prompted or set it as an environment variable

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

