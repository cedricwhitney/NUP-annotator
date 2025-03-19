# Define base paths without spaces
VENV_DIR := $(shell pwd)/.venv
BIN_DIR := $(VENV_DIR)/bin

# Export venv activation to all commands
export VIRTUAL_ENV=$(VENV_DIR)
export PATH := $(BIN_DIR):$(PATH)
export PYTHONPATH := .
export LABEL_STUDIO_DATABASE_ENGINE=sqlite
export LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED=true
export LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT=/

.PHONY: setup run label-studio stop-label-studio create-project sync-repo validate-json refresh-data export-data test

# Check for uv installation
check-uv:
	@which uv > /dev/null || (echo "❌ uv is not installed. Please install uv first:\n\ncurl -LsSf https://astral.sh/uv/install.sh | sh\n" && exit 1)
	@echo "✅ uv found"

# Sync repository with latest changes
sync-repo:
	@echo "🔄 Syncing repository with remote..."
	@git pull origin main || (echo "❌ Failed to pull latest changes" && exit 1)
	@echo "✅ Repository synced"

# Step 1: Set up the environment
setup: check-uv
	@echo "🚀 Setting up project..."
	@rm -rf "$(VENV_DIR)"
	uv venv
	. $(VENV_DIR)/bin/activate && uv pip install -r requirements.txt
	@echo "✅ Setup complete!"
	@echo "\nFirst time setup:"
	@echo "1. Run 'make first-time-setup' to start the server"
	@echo "2. Create an account at http://localhost:8080"
	@echo "3. Get your API key from Account & Settings > Access Token"
	@echo "4. Run 'make start-project' to set up your labeling project"
	@echo "\nSubsequent usage:"
	@echo "- 'make label-studio'    - Quick start the server"
	@echo "- 'make stop-label-studio' - Stop the server"

# Step 2: Start Label Studio (depends on sync-repo to ensure latest code)
label-studio: sync-repo
	@echo "Starting Label Studio..."
	label-studio start &
	@echo "Waiting for Label Studio to start up..."
	@sleep 10  # Give Label Studio time to start

# First time setup and configuration
first-time-setup: sync-repo
	@echo "Starting Label Studio..."
	label-studio start &
	@echo "Waiting for Label Studio to start up..."
	@sleep 10
	@echo "\n✅ Label Studio should now be running at http://localhost:8080"
	@echo "\nIf this is your first time:"
	@echo "1. Create an account at http://localhost:8080"
	@echo "2. Get your API key from Account & Settings > Access Token"
	@echo "3. Copy your API key - you'll need it in the next step!"
	@echo "4. Run 'make start-project' to set up the pre-configured labeling project"
	@echo "\nIf you're already logged in:"
	@echo "1. Get your API key from Account & Settings > Access Token"
	@echo "2. Copy your API key - you'll need it in the next step!"
	@echo "3. Run 'make start-project' to set up the pre-configured labeling project"
	@echo "\nTip: Set LABEL_STUDIO_API_KEY environment variable to skip the API key prompt:"
	@echo "export LABEL_STUDIO_API_KEY=your_key_here"

# Step 3: Create project (depends on sync-repo to ensure latest code)
start-project: sync-repo
	@echo "Starting pre-configured Label Studio project..."
	@echo "\nThis will:"
	@echo "1. Show available batch files"
	@echo "2. Set up the project in Label Studio"
	@echo "3. Configure the correct taxonomy structure"
	@echo "\nTip: Make sure to select your assigned batch when prompted\n"
	PYTHONPATH=. python src/core/start_project.py

# Step 4: Run the workflow (depends on sync-repo and label-studio)
run: sync-repo label-studio
	python -m src.label_studio_integration

# Step 5: Stop Label Studio
stop-label-studio:
	@echo "Stopping Label Studio..."
	@pkill -f "label-studio" || true

# Validate JSON format
validate-json:
	@echo "Validating JSON format..."
	python src/tools/validate_labelstudio_json.py data/batch_1.json

# Run tests
test:
	@echo "Running all tests..."
	pytest tests/

# List available data files (depends on sync-repo to ensure latest files)
refresh-data: sync-repo
	@echo "\n📁 Available batch files:"
	@ls -1 data/batch_*.json 2>/dev/null || echo "No batch files found in data directory"
	@echo "\nTo use a new file:"
	@echo "1. Copy your batch file to the data/ directory"
	@echo "2. Run 'make refresh-data' to verify it's detected"
	@echo "3. Run 'make start-project' to create a new project with the file"

# Export Label Studio data (depends on sync-repo and label-studio to ensure server is running)
export-data: sync-repo label-studio
	@if [ -z "$$LABEL_STUDIO_API_KEY" ]; then \
		echo "\n🔑 No API key found in environment."; \
		echo "Please get your API key from Label Studio:"; \
		echo "1. Visit http://localhost:8080"; \
		echo "2. Go to Account & Settings > Access Token"; \
		echo "\nTip: Set LABEL_STUDIO_API_KEY environment variable to skip this prompt:"; \
		echo "export LABEL_STUDIO_API_KEY=your_key_here\n"; \
		read -p "Enter your API key: " api_key; \
		LABEL_STUDIO_API_KEY=$$api_key PYTHONPATH=. python src/tools/export_labelstudio.py; \
	else \
		PYTHONPATH=. python src/tools/export_labelstudio.py; \
	fi
	@echo "\n📁 Checking for changes in your annotations..."
	@if git diff --quiet annotator_exports/; then \
		echo "✨ No new changes found since your last export"; \
		echo "💡 Tip: If you've made new annotations, make sure you've submitted them in Label Studio!"; \
		exit 0; \
	fi
	@echo "✨ New changes detected in your annotations"
	@echo "\n💭 Would you like to share these updates with other annotators?"
	@echo "   • Your new annotations will be saved to GitHub"
	@echo "   • Your previous annotations will be preserved"
	@echo "   • Other annotators will be able to see your work\n"
	@read -p "Share your annotations? [y/N] " answer; \
	if [ "$$answer" = "y" ] || [ "$$answer" = "Y" ]; then \
		echo "\n🔄 Checking Git permissions..."; \
		if ! git push --dry-run origin main > /dev/null 2>&1; then \
			echo "❌ Error: You don't have permission to push to this repository."; \
			echo "Please contact the repository administrator for access."; \
			exit 1; \
		fi; \
		echo "\n🔄 Saving your annotations..."; \
		git add annotator_exports/; \
		git commit -m "Update annotations"; \
		echo "\n🚀 Sharing your work..."; \
		git push origin main; \
		echo "\n✅ Success! Your annotations have been shared."; \
	else \
		echo "\n💡 Your annotations were exported but not shared."; \
		echo "   To share them later, run:"; \
		echo "   make export-data"; \
	fi
