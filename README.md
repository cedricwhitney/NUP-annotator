# Conversation Project

A tool for annotating conversations using Label Studio. This project uses the open source version of [Label Studio](https://github.com/heartexlabs/label-studio) - many thanks to the Label Studio team for making this possible!

## Overview

This project facilitates consistent annotation across multiple annotators:
- Each annotator runs their own local instance of Label Studio
- All instances are configured with the same taxonomy structure
- Annotators work independently on their local installations
- Results can be exported and compared across annotators

The setup ensures everyone has identical project configuration while maintaining independent workspaces.

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

## Prerequisites

- Python 3.x
- Git (pre-installed on macOS, check version with `git --version`)
- `make` command-line tool
  - **Linux/Mac**: Usually pre-installed
  - **Windows**: Install via [chocolatey](https://chocolatey.org/): `choco install make`

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

4. Select your batch file:
   - Your name is next to the batch file you will be working on
   - Each batch contains 20 unique conversations
   - The batch files are already in the `data/` directory
   - Run `make start-project` and select your assigned batch file

   Note: You can also add your own JSON/JSONL files to the `data/` directory if needed.
   The system supports both formats and will automatically convert and validate them.

5. Set up the pre-configured project:
   ```bash
   make start-project
   ```
   This will:
   - Show available batch files (batch_1.json through batch_12.json)
   - Guide you to select your assigned batch
   - Set up a new project with your batch's conversations
   - Configure the correct taxonomy structure

## Annotation Export & Sharing

To save and share your annotations with other annotators:

1. Make sure you've submitted your annotations in Label Studio
   - Click the "Submit" button after each annotation, and "Update" if you've made changes

2. Export your annotations:
   ```bash
   make export-data
   ```

   The first time you run this, you'll need your Label Studio API key:
   - Visit http://localhost:8080
   - Go to Account & Settings > Access Token
   - Copy your API key
   - Optional: Set it as an environment variable to skip the prompt next time:
     ```bash
     export LABEL_STUDIO_API_KEY=your_key_here
     ```

3. When prompted, type 'y' to share your annotations with other annotators

Your annotations will be:
- Saved in `annotator_exports/[your_git_username]_annotations.json`
- Automatically shared with other annotators via GitHub
- Preserved with full history of all your exports

To get updates from other annotators:
```bash
git pull origin main
```

## Project Structure

The repository is organized as follows:

    conversation_project/          # This is a directory structure diagram
    ├── src/
    │   ├── core/                 # Core functionality
    │   │   ├── start_project.py      # Label Studio project setup
    │   │   └── label_studio_integration.py
    │   └── tools/                # Utility tools
    │       ├── csv_to_labelstudio.py     # Convert CSV to Label Studio format
    │       ├── convert_jsonl_to_json.py   # Convert JSONL to Label Studio format
    │       └── validate_labelstudio_json.py  # Validate JSON format
    ├── tests/
    │   └── tools/                # Tests for utility tools
    │       ├── test_csv_converter.py     # CSV conversion tests
    │       ├── test_json_validator.py    # JSON validation tests
    │       └── test_jsonl_converter.py   # JSONL conversion tests
    ├── data/                     # Data directory
    │   └── your_tasks.json       # Your annotation tasks in Label Studio format
    └── Makefile                  # Project automation

## Testing

### Setting Up a Test Environment
To test with a fresh Label Studio installation:

1. Stop Label Studio if running:
   ```bash
   make stop-label-studio
   ```

2. Backup existing database:
   ```bash
   mv label-studio.sqlite3 label-studio.sqlite3.backup
   ```

3. Start fresh and create new account:
   ```bash
   make ensure-label-studio
   ```

To restore previous account:
```bash
make stop-label-studio
mv label-studio.sqlite3 label-studio.sqlite3.new
mv label-studio.sqlite3.backup label-studio.sqlite3
```

### Running Tests
```bash
make test           # Run all tests
make test-csv      # Run CSV tests only
make test-json     # Run JSON tests only
make test-jsonl    # Run JSONL tests only
```

### What's Tested

1. CSV Conversion (`test_csv_converter.py`)
   - Converts Turn 0-4 format to Label Studio JSON
   - Validates role assignment (human/llm)
   - Ensures proper JSON structure

2. JSON Validation (`test_json_validator.py`)
   - Validates Label Studio JSON format
   - Catches common format issues:
     - Missing "data" wrapper
     - Incorrect conversation structure
     - Invalid role/text fields

3. JSONL Conversion (`test_jsonl_converter.py`)
   - Converts JSONL to Label Studio JSON format
   - Adds required "data" wrapper if missing
   - Handles empty files correctly

### Example Valid Formats

CSV Input:
```csv
Turn 0,Turn 1,Turn 2,Turn 3,Turn 4
"Hello","Hi there","How are you?","I'm good","Great!"
```

JSON Output:
```json
[
  {
    "data": {
      "conversation": [
        {"role": "human", "text": "Hello"},
        {"role": "llm", "text": "Hi there"}
      ]
    }
  }
]
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

