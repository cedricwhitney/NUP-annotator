.PHONY: setup run label-studio stop-label-studio create-project convert test-converter check-python validate-json convert-csv test test-csv test-json test-jsonl

# Check Python installation
check-python:
	@which python3 > /dev/null || (echo "❌ Python 3 is not installed. Please install Python 3.x first." && exit 1)
	@echo "✅ Python 3 found"

# Step 1: Set up the environment
setup: check-python
	@echo "🚀 Setting up project..."
	python3 -m venv venv
	. venv/bin/activate && pip install -U pip && pip install -r requirements.txt
	@echo "✅ Setup complete!"
	@echo "Available commands:"
	@echo "  make create-project  - Create new Label Studio project (one-time setup)"
	@echo "  make run            - Start Label Studio and access existing project"
	@echo "  make convert        - Convert CSV files to JSON format"
	@echo "  make test-converter - Run tests for the CSV to JSON converter"

# Step 2: Start Label Studio
label-studio:
	@echo "Starting Label Studio..."
	. venv/bin/activate && label-studio start &
	@echo "Waiting for Label Studio to start up..."
	@sleep 10  # Give Label Studio time to start

# Ensure Label Studio is running and get API key if needed
ensure-label-studio:
	@echo "Starting Label Studio..."
	. venv/bin/activate && label-studio start &
	@echo "Waiting for Label Studio to start up..."
	@sleep 10
	@echo "\n✅ Label Studio should now be running at http://localhost:8080"
	@echo "If this is your first time, please create an account."
	@echo "Then get your API key from Account & Settings > Access Token"

# Step 3: Create project (only needed once)
create-project:
	@echo "Creating Label Studio project..."
	@echo "This will:"
	@echo "1. List available data files"
	@echo "2. Convert and validate your chosen file"
	@echo "3. Set up the project in Label Studio"
	PYTHONPATH=. . venv/bin/activate && python src/core/create_project.py

# Step 4: CSV Converter Tools
convert:
	@echo "Converting CSV to JSON format..."
	. venv/bin/activate && python src/converter.py

test-converter:
	@echo "Running converter tests..."
	. venv/bin/activate && pytest tests/
	@echo "✅ Converter tests completed"

# Step 5: Run the workflow
run: label-studio
	. venv/bin/activate && python -m src.label_studio_integration

# Step 6: Stop Label Studio
stop-label-studio:
	@echo "Stopping Label Studio..."
	@pkill -f "label-studio" || true

# Validate JSON format
validate-json:
	@echo "Validating JSON format..."
	. venv/bin/activate && python src/tools/validate_labelstudio_json.py data/your_tasks.json

# Convert CSV to Label Studio format
convert-csv:
	@echo "Converting CSV to Label Studio format..."
	. venv/bin/activate && python src/tools/csv_to_labelstudio.py

# Run all tests
test:
	@echo "Running all tests..."
	PYTHONPATH=. . venv/bin/activate && pytest tests/tools/

# Run CSV conversion tests
test-csv:
	@echo "Running CSV conversion tests..."
	PYTHONPATH=. . venv/bin/activate && pytest tests/tools/test_csv_converter.py

# Run JSON validation tests
test-json:
	@echo "Running JSON validation tests..."
	PYTHONPATH=. . venv/bin/activate && pytest tests/tools/test_json_validator.py

# Run JSONL conversion tests
test-jsonl:
	@echo "Running JSONL conversion tests..."
	PYTHONPATH=. . venv/bin/activate && pytest tests/tools/test_jsonl_converter.py
