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
   git clone [your-repo-url]
   cd conversation_project
   ```

2. Set up the environment:
   ```bash
   make setup
   ```

3. Start Label Studio and create an account:
   ```bash
   make run
   ```
   - Visit http://localhost:8080
   - Create an account or log in
   - The project should be available in your workspace

## Available Commands

- `make setup` - First-time setup of virtual environment and dependencies
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
