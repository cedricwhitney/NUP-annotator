# Conversation Project

A tool for annotating conversations using Label Studio. This project uses the open source version of [Label Studio](https://github.com/heartexlabs/label-studio) - many thanks to the Label Studio team for making this possible!

## Overview

This project facilitates consistent annotation across multiple annotators:
- Each annotator runs their own local instance of Label Studio
- All instances are configured with the same taxonomy structure
- Annotators work independently on their local installations
- Results can be exported and compared across annotators

The setup ensures everyone has identical project configuration while maintaining independent workspaces.

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

## Annotation Workflow

1. Each annotator:
   - Sets up their own local Label Studio instance
   - Works independently on their assigned conversations
   - Maintains their own annotations in their local database

2. For comparison:
   - Annotators export their completed annotations from Label Studio
   - Exports can be collected and compared to assess agreement
   - Results can be analyzed while maintaining independent workspaces

## Available Commands

- `make setup` - First-time setup of virtual environment and dependencies
- `make create-project` - Create/update the Label Studio project structure (will prompt for API key if needed)
- `make run` - Start Label Studio and access the project
- `make convert` - Convert CSV files to JSON format for import
- `make test-converter` - Run tests for the CSV converter
- `make stop-label-studio` - Stop the Label Studio server

## Project Structure

The repository is organized as follows:

    conversation_project/          # This is a directory structure diagram
    ├── src/                      # Source code directory
    │   ├── converter.py          # (Advanced) CSV to JSON converter for new datasets
    │   ├── create_project.py     # Label Studio project setup
    │   └── label_studio_integration.py
    ├── data/                     # Data directory
    │   └── initial_tasks.json    # Pre-converted dataset for all users
    ├── tests/                    # Converter tests
    └── Makefile                  # Project automation

Note: This is a visualization of how the project files are organized, not a configuration file.

## Advanced Usage

The `converter.py` script is available for converting new CSV files to the Label Studio JSON format. This is an advanced feature for users who need to create new datasets:

```bash
make convert
```

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

## Acknowledgments

This project uses [Label Studio](https://github.com/heartexlabs/label-studio), an open source data labeling tool. We're grateful to the Label Studio team for providing this excellent platform for annotation projects.

