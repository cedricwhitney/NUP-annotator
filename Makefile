.PHONY: setup run label-studio stop-label-studio create-project convert test-converter check-python

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

# Step 3: Create project (only needed once)
create-project: label-studio
	. venv/bin/activate && python src/create_project.py

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
