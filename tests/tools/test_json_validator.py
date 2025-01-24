import pytest
import json
from src.tools.validate_labelstudio_json import validate_and_fix_json

def test_valid_label_studio_format():
    """Test that a correctly formatted file passes validation"""
    valid_data = [
        {
            "data": {
                "conversation": [
                    {"role": "human", "text": "Hello"},
                    {"role": "assistant", "text": "Hi"}
                ]
            }
        }
    ]
    
    with open('data/test_valid.json', 'w') as f:
        json.dump(valid_data, f)
    
    assert validate_and_fix_json('data/test_valid.json') == True

def test_invalid_format_missing_data_wrapper():
    """Test that missing 'data' wrapper is caught"""
    invalid_data = [
        {
            "conversation": [  # Missing "data" wrapper
                {"role": "human", "text": "Hello"},
                {"role": "assistant", "text": "Hi"}
            ]
        }
    ]
    
    with open('data/test_invalid.json', 'w') as f:
        json.dump(invalid_data, f)
    
    assert validate_and_fix_json('data/test_invalid.json') == False

def test_invalid_format_wrong_conversation_structure():
    """Test that incorrect conversation structure is caught"""
    invalid_data = [
        {
            "data": {
                "conversation": [
                    {"wrong_key": "human", "message": "Hello"},  # Added comma
                    {"wrong_key": "human", "message": "Hello"}   # Wrong keys
                ]
            }
        }
    ]
    
    with open('data/test_invalid.json', 'w') as f:
        json.dump(invalid_data, f)
    
    assert validate_and_fix_json('data/test_invalid.json') == False 