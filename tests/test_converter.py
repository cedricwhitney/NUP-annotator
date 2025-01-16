import pytest
import os
import json
from src.converter import main


@pytest.fixture
def sample_csv(tmp_path):
    """
    Create a sample CSV file for testing.
    """
    csv_content = (
        "Turn 0,Turn 1,Turn 2,Turn 3,Turn 4\n"
        '"Hello!","Hi, how can I help?","I need assistance.","Of course!","Thanks!"\n'
        '"Hi there!","Hello!","What\'s the weather?","It\'s sunny!","Great!"\n'
    )
    csv_file = tmp_path / "test_input.csv"
    csv_file.write_text(csv_content)
    return csv_file


@pytest.fixture
def expected_json():
    """
    Define the expected JSON structure for the sample CSV.
    """
    return [
        {
            "conversation": [
                {"role": "human", "text": "Hello!"},
                {"role": "llm", "text": "Hi, how can I help?"},
                {"role": "human", "text": "I need assistance."},
                {"role": "llm", "text": "Of course!"},
                {"role": "human", "text": "Thanks!"}
            ]
        },
        {
            "conversation": [
                {"role": "human", "text": "Hi there!"},
                {"role": "llm", "text": "Hello!"},
                {"role": "human", "text": "What's the weather?"},
                {"role": "llm", "text": "It's sunny!"},
                {"role": "human", "text": "Great!"}
            ]
        }
    ]


def test_csv_to_json(sample_csv, expected_json, tmp_path):
    """
    Test the converter script with a sample CSV input.
    """
    # Set paths for input and output files
    output_file = tmp_path / "test_output.json"

    # Temporarily override file paths
    os.environ["TEST_CSV_FILE"] = str(sample_csv)
    os.environ["TEST_JSON_FILE"] = str(output_file)

    # Run the converter script
    main()

    # Assert the JSON file was created
    assert os.path.exists(output_file), "❌ JSON output file was not created."

    # Verify the JSON content
    with open(output_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data == expected_json, f"❌ JSON output does not match expected: {data}"

    print(f"✅ Test passed! JSON file contains {len(data)} tasks.")
