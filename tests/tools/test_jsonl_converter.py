import pytest
import json
from src.tools.convert_jsonl_to_json import convert_jsonl_to_json

def test_jsonl_to_json_conversion():
    """Test basic JSONL to JSON conversion"""
    # Create test JSONL file
    with open('data/test_input.jsonl', 'w') as f:
        f.write('{"conversation": [{"role": "human", "text": "Hello"}]}\n')
        f.write('{"conversation": [{"role": "assistant", "text": "Hi"}]}\n')
    
    # Convert to JSON
    convert_jsonl_to_json('data/test_input.jsonl', 'data/test_output.json')
    
    # Check the output
    with open('data/test_output.json', 'r') as f:
        data = json.load(f)
        
    expected = [
        {
            "data": {
                "conversation": [
                    {"role": "human", "text": "Hello"}
                ]
            }
        },
        {
            "data": {
                "conversation": [
                    {"role": "assistant", "text": "Hi"}
                ]
            }
        }
    ]
    
    assert data == expected

def test_jsonl_to_json_empty_file():
    """Test conversion of empty JSONL file"""
    # Create empty JSONL file
    with open('data/test_empty.jsonl', 'w') as f:
        f.write('')
    
    # Convert to JSON
    convert_jsonl_to_json('data/test_empty.jsonl', 'data/test_empty_output.json')
    
    # Check the output
    with open('data/test_empty_output.json', 'r') as f:
        data = json.load(f)
    
    assert data == []

def test_jsonl_to_json_adds_data_wrapper():
    """Test that conversion adds 'data' wrapper if missing"""
    # Create JSONL without data wrapper
    with open('data/test_nowrap.jsonl', 'w') as f:
        f.write('{"conversation": [{"role": "human", "text": "Hello"}]}\n')
    
    # Convert to JSON
    convert_jsonl_to_json('data/test_nowrap.jsonl', 'data/test_nowrap_output.json')
    
    # Check the output
    with open('data/test_nowrap_output.json', 'r') as f:
        data = json.load(f)
    
    expected = [
        {
            "data": {
                "conversation": [
                    {"role": "human", "text": "Hello"}
                ]
            }
        }
    ]
    
    assert data == expected 