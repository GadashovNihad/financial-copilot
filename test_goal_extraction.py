#!/usr/bin/env python3
"""
Test script for goal extraction functionality.
This script tests the extract_goal_from_message function with various inputs.
"""

import json

# Mock Gemini model for testing
class MockGeminiModel:
    def __init__(self, response_text):
        self.response_text = response_text
    
    def generate_content(self, prompt):
        class MockResponse:
            def __init__(self, text):
                self.text = text
        return MockResponse(self.response_text)

def extract_goal_from_message(user_message, model):
    """
    Extract goal name and target amount from user message using Gemini AI.
    
    Args:
        user_message (str): The user's natural language message
        model: Configured Gemini model instance
    
    Returns:
        dict: Dictionary with 'name' and 'target_amount' keys, or None if extraction fails
    """
    extraction_prompt = f"""
    You are a financial assistant that extracts savings goal information from user messages.
    
    Your task is to extract:
    1. Goal name/description (what they want to save for)
    2. Target amount (how much money they want to save)
    
    Rules:
    - Return ONLY a JSON object with "name" and "target_amount" fields
    - The "name" should be a short, descriptive phrase (e.g., "vacation", "new car", "emergency fund")
    - The "target_amount" should be a number (without dollar sign or commas)
    - If you cannot extract both pieces of information clearly, return an empty JSON object: {{}}
    - Do not include any explanation or additional text
    
    User message: "{user_message}"
    
    JSON response:
    """
    
    try:
        response = model.generate_content(extraction_prompt)
        response_text = response.text.strip()
        
        # Try to parse the JSON response
        goal_data = json.loads(response_text)
        
        # Validate that we have both required fields
        if isinstance(goal_data, dict) and 'name' in goal_data and 'target_amount' in goal_data:
            # Validate target_amount is a valid number
            try:
                target_amount = float(goal_data['target_amount'])
                if target_amount > 0:
                    return {
                        'name': str(goal_data['name']).strip(),
                        'target_amount': target_amount
                    }
            except (ValueError, TypeError):
                pass
        
        return None
        
    except (json.JSONDecodeError, Exception) as e:
        print(f"Goal extraction parsing error: {e}")
        return None

def test_goal_extraction():
    """Test the goal extraction functionality with various scenarios."""
    
    print("Testing Goal Extraction Functionality")
    print("=" * 40)
    
    # Test case 1: Valid goal extraction
    print("\nTest 1: Valid goal extraction")
    mock_model = MockGeminiModel('{"name": "vacation", "target_amount": 2000}')
    result = extract_goal_from_message("I want to save $2000 for a vacation", mock_model)
    print(f"Input: 'I want to save $2000 for a vacation'")
    print(f"Result: {result}")
    assert result == {'name': 'vacation', 'target_amount': 2000.0}
    print("✓ PASSED")
    
    # Test case 2: Invalid JSON response
    print("\nTest 2: Invalid JSON response")
    mock_model = MockGeminiModel('This is not valid JSON')
    result = extract_goal_from_message("I want to save for something", mock_model)
    print(f"Input: 'I want to save for something'")
    print(f"Result: {result}")
    assert result is None
    print("✓ PASSED")
    
    # Test case 3: Empty JSON response
    print("\nTest 3: Empty JSON response")
    mock_model = MockGeminiModel('{}')
    result = extract_goal_from_message("unclear message", mock_model)
    print(f"Input: 'unclear message'")
    print(f"Result: {result}")
    assert result is None
    print("✓ PASSED")
    
    # Test case 4: Invalid target amount
    print("\nTest 4: Invalid target amount")
    mock_model = MockGeminiModel('{"name": "car", "target_amount": "not_a_number"}')
    result = extract_goal_from_message("I want to save for a car", mock_model)
    print(f"Input: 'I want to save for a car'")
    print(f"Result: {result}")
    assert result is None
    print("✓ PASSED")
    
    # Test case 5: Negative target amount
    print("\nTest 5: Negative target amount")
    mock_model = MockGeminiModel('{"name": "house", "target_amount": -5000}')
    result = extract_goal_from_message("I want to save for a house", mock_model)
    print(f"Input: 'I want to save for a house'")
    print(f"Result: {result}")
    assert result is None
    print("✓ PASSED")
    
    # Test case 6: Missing fields
    print("\nTest 6: Missing fields")
    mock_model = MockGeminiModel('{"name": "emergency fund"}')
    result = extract_goal_from_message("I want to save for emergency fund", mock_model)
    print(f"Input: 'I want to save for emergency fund'")
    print(f"Result: {result}")
    assert result is None
    print("✓ PASSED")
    
    print("\n" + "=" * 40)
    print("All tests passed! Goal extraction functionality is working correctly.")

if __name__ == "__main__":
    test_goal_extraction()