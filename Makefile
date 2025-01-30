# Export venv activation to all commands
export VIRTUAL_ENV=$(shell pwd)/venv
export PATH := $(VIRTUAL_ENV)/bin:$(PATH)
export LABEL_STUDIO_DATABASE_ENGINE=sqlite
export LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED=true
export LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT=/

.PHONY: setup run label-studio stop-label-studio create-project convert test-converter check-python validate-json convert-csv test test-csv test-json test-jsonl refresh-data

# Check Python installation
check-python:
	@which python3 > /dev/null || (echo "❌ Python 3 is not installed. Please install Python 3.x first." && exit 1)
	@echo "✅ Python 3 found"

# Step 1: Set up the environment
setup: check-python
	@echo "🚀 Setting up project..."
	python3 -m venv venv
	$(VIRTUAL_ENV)/bin/pip install -U pip wheel setuptools
	$(VIRTUAL_ENV)/bin/pip install psycopg2-binary --force-reinstall
	$(VIRTUAL_ENV)/bin/pip install label-studio
	$(VIRTUAL_ENV)/bin/pip install label-studio-sdk
	$(VIRTUAL_ENV)/bin/pip install pandas pytest pytest-mock black flake8
	@echo "✅ Setup complete!"
	@echo "\nFirst time setup:"
	@echo "1. Run 'make ensure-label-studio' to start the server"
	@echo "2. Create an account at http://localhost:8080"
	@echo "3. Get your API key from Account & Settings > Access Token"
	@echo "4. Run 'make create-project' to set up your labeling project"
	@echo "\nSubsequent usage:"
	@echo "- 'make label-studio'    - Quick start the server"
	@echo "- 'make convert'         - Convert CSV files to JSON format"
	@echo "- 'make test-converter'  - Run tests for the CSV to JSON converter"
	@echo "- 'make stop-label-studio' - Stop the server"

# Step 2: Start Label Studio
label-studio:
	@echo "Starting Label Studio..."
	label-studio start &
	@echo "Waiting for Label Studio to start up..."
	@sleep 10  # Give Label Studio time to start

# Ensure Label Studio is running and get API key if needed
ensure-label-studio:
	@echo "Starting Label Studio..."
	label-studio start &
	@echo "Waiting for Label Studio to start up..."
	@sleep 10
	@echo "\n✅ Label Studio should now be running at http://localhost:8080"
	@echo "\nIf this is your first time:"
	@echo "1. Create an account at http://localhost:8080"
	@echo "2. Get your API key from Account & Settings > Access Token"
	@echo "\nIf you're already logged in:"
	@echo "1. Get your API key from Account & Settings > Access Token"
	@echo "2. Run 'make create-project' to set up your labeling project"
	@echo "\nTip: Set LABEL_STUDIO_API_KEY environment variable to skip the API key prompt:"
	@echo "export LABEL_STUDIO_API_KEY=your_key_here"

# Step 3: Create project (only needed once)
create-project:
	@echo "Creating Label Studio project..."
	@echo "This will:"
	@echo "1. List available data files"
	@echo "2. Convert and validate your chosen file"
	@echo "3. Set up the project in Label Studio"
	PYTHONPATH=. python src/core/create_project.py

# Step 4: CSV Converter Tools
convert:
	@echo "Converting CSV to JSON format..."
	python src/converter.py

test-converter:
	@echo "Running converter tests..."
	pytest tests/
	@echo "✅ Converter tests completed"

# Step 5: Run the workflow
run: label-studio
	python -m src.label_studio_integration

# Step 6: Stop Label Studio
stop-label-studio:
	@echo "Stopping Label Studio..."
	@pkill -f "label-studio" || true

# Validate JSON format
validate-json:
	@echo "Validating JSON format..."
	python src/tools/validate_labelstudio_json.py data/your_tasks.json

# Convert CSV to Label Studio format
convert-csv:
	@echo "Converting CSV to Label Studio format..."
	python src/tools/csv_to_labelstudio.py

# Run all tests
test:
	@echo "Running all tests..."
	pytest tests/tools/

# Run CSV conversion tests
test-csv:
	@echo "Running CSV conversion tests..."
	pytest tests/tools/test_csv_converter.py

# Run JSON validation tests
test-json:
	@echo "Running JSON validation tests..."
	pytest tests/tools/test_json_validator.py

# Run JSONL conversion tests
test-jsonl:
	@echo "Running JSONL conversion tests..."
	pytest tests/tools/test_jsonl_converter.py

# List available data files
refresh-data:
	@echo "\n📁 Available files in data directory:"
	@ls -1 data/*.json* 2>/dev/null || echo "No JSON/JSONL files found in data directory"
	@echo "\nTo use a new file:"
	@echo "1. Copy your file to the data/ directory"
	@echo "2. Run 'make refresh-data' to verify it's detected"
	@echo "3. Run 'make create-project' to create a new project with the file"
