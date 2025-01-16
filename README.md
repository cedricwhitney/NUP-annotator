# Conversation Project

A tool for annotating conversations using Label Studio.

## Prerequisites

- Python 3.x
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

3. First-time setup (only needed once per computer):
   ```bash
   make create-project
   ```
   This will:
   - Start Label Studio
   - Guide you through getting your API key
   - Create the project with the correct taxonomy structure
   
   Note: You'll be prompted to input your API key if it's not set. To skip this prompt in the future:
   ```bash
   export LABEL_STUDIO_API_KEY=your-key-here
   ```

4. Start Label Studio for regular use:
   ```bash
   make run
   ```
   - Visit http://localhost:8080
   - Log in to your account
   - The project should be available in your workspace

## Project Synchronization

- Each new installation needs to run `make create-project` once
- The project structure is maintained in git (in create_project.py)
- Updates to the project structure will be shared via git
- When project structure changes, users should:
  1. Pull the latest changes: `git pull`
  2. Run `make create-project` again to update their local project

## Available Commands

- `make setup` - First-time setup of virtual environment and dependencies
- `make create-project` - Create/update the Label Studio project structure (will prompt for API key if needed)
- `make run` - Start Label Studio and access the project
- `make convert` - Convert CSV files to JSON format for import
- `make test-converter` - Run tests for the CSV converter
- `make stop-label-studio` - Stop the Label Studio server

## Project Structure

    conversation_project/
    ├── src/
    │   ├── converter.py       # CSV to JSON converter
    │   ├── create_project.py  # Label Studio project setup
    │   └── label_studio_integration.py
    ├── tests/                 # Converter tests
    ├── data/                  # Place CSV files here for conversion
    └── Makefile

## Troubleshooting

If you encounter issues:
1. Ensure Python 3.x is installed: `python3 --version`
2. Check if Label Studio is running: http://localhost:8080
3. Try stopping and restarting Label Studio: `make stop-label-studio && make run`
4. If project is missing: Run `make create-project` to set up the project structure
5. API key issues:
   - Your API key is specific to your Label Studio installation
   - Get a new key from Account & Settings > Access Token
   - Either enter it when prompted or set it as an environment variable

