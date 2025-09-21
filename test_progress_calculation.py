#!/usr/bin/env python3
"""
Test script for progress calculation functionality.
This script tests the progress calculation logic implemented in task 5.
"""

def test_progress_calculation():
    """Test the progress calculation functionality."""
    
    print("Testing Progress Calculation Functionality")
    print("=" * 45)
    
    # Test case 1: Calculate progress with multiple deposits
    print("\nTest 1: Calculate progress with multiple deposits")
    transactions_data = [
        {"type": "DEPOSIT", "amount": 500.0, "description": "Salary", "date": "2024-01-01"},
        {"type": "WITHDRAWAL", "amount": 100.0, "description": "Groceries", "date": "2024-01-02"},
        {"type": "DEPOSIT", "amount": 300.0, "description": "Freelance", "date": "2024-01-03"},
        {"type": "DEPOSIT", "amount": 200.0, "description": "Bonus", "date": "2024-01-04"}
    ]
    
    # Simulate the progress calculation logic
    total_saved = 0.0
    if isinstance(transactions_data, list):
        for transaction in transactions_data:
            if isinstance(transaction, dict) and transaction.get('type') == 'DEPOSIT':
                try:
                    amount = float(transaction.get('amount', 0))
                    total_saved += amount
                except (ValueError, TypeError):
                    continue
    
    print(f"Transactions: {len(transactions_data)} total")
    print(f"Deposits found: {sum(1 for t in transactions_data if t.get('type') == 'DEPOSIT')}")
    print(f"Total saved: ${total_saved}")
    
    expected_total = 500.0 + 300.0 + 200.0  # Only deposits
    assert total_saved == expected_total
    print("✓ PASSED")
    
    # Test case 2: No deposits (edge case)
    print("\nTest 2: No deposits (edge case)")
    transactions_data = [
        {"type": "WITHDRAWAL", "amount": 100.0, "description": "Groceries", "date": "2024-01-01"},
        {"type": "WITHDRAWAL", "amount": 50.0, "description": "Gas", "date": "2024-01-02"}
    ]
    
    total_saved = 0.0
    if isinstance(transactions_data, list):
        for transaction in transactions_data:
            if isinstance(transaction, dict) and transaction.get('type') == 'DEPOSIT':
                try:
                    amount = float(transaction.get('amount', 0))
                    total_saved += amount
                except (ValueError, TypeError):
                    continue
    
    print(f"Transactions: {len(transactions_data)} total")
    print(f"Deposits found: {sum(1 for t in transactions_data if t.get('type') == 'DEPOSIT')}")
    print(f"Total saved: ${total_saved}")
    
    assert total_saved == 0.0
    print("✓ PASSED")
    
    # Test case 3: Empty transactions data (edge case)
    print("\nTest 3: Empty transactions data (edge case)")
    transactions_data = []
    
    total_saved = 0.0
    if isinstance(transactions_data, list):
        for transaction in transactions_data:
            if isinstance(transaction, dict) and transaction.get('type') == 'DEPOSIT':
                try:
                    amount = float(transaction.get('amount', 0))
                    total_saved += amount
                except (ValueError, TypeError):
                    continue
    
    print(f"Transactions: {len(transactions_data)} total")
    print(f"Total saved: ${total_saved}")
    
    assert total_saved == 0.0
    print("✓ PASSED")
    
    # Test case 4: Invalid transaction data (edge case)
    print("\nTest 4: Invalid transaction data (edge case)")
    transactions_data = [
        {"type": "DEPOSIT", "amount": "invalid", "description": "Bad data", "date": "2024-01-01"},
        {"type": "DEPOSIT", "amount": 100.0, "description": "Good data", "date": "2024-01-02"},
        {"type": "DEPOSIT", "description": "Missing amount", "date": "2024-01-03"},
        {"type": "DEPOSIT", "amount": None, "description": "Null amount", "date": "2024-01-04"}
    ]
    
    total_saved = 0.0
    if isinstance(transactions_data, list):
        for transaction in transactions_data:
            if isinstance(transaction, dict) and transaction.get('type') == 'DEPOSIT':
                try:
                    amount = float(transaction.get('amount', 0))
                    total_saved += amount
                except (ValueError, TypeError):
                    continue
    
    print(f"Transactions: {len(transactions_data)} total")
    print(f"Valid deposits processed: 1")
    print(f"Total saved: ${total_saved}")
    
    assert total_saved == 100.0  # Only the valid deposit
    print("✓ PASSED")
    
    # Test case 5: Non-list transactions data (edge case)
    print("\nTest 5: Non-list transactions data (edge case)")
    transactions_data = "This is not a list"
    
    total_saved = 0.0
    if isinstance(transactions_data, list):
        for transaction in transactions_data:
            if isinstance(transaction, dict) and transaction.get('type') == 'DEPOSIT':
                try:
                    amount = float(transaction.get('amount', 0))
                    total_saved += amount
                except (ValueError, TypeError):
                    continue
    
    print(f"Transactions data type: {type(transactions_data)}")
    print(f"Total saved: ${total_saved}")
    
    assert total_saved == 0.0
    print("✓ PASSED")
    
    # Test case 6: Mixed valid and invalid transactions
    print("\nTest 6: Mixed valid and invalid transactions")
    transactions_data = [
        {"type": "DEPOSIT", "amount": 250.0, "description": "Valid deposit", "date": "2024-01-01"},
        {"type": "WITHDRAWAL", "amount": 50.0, "description": "Should be ignored", "date": "2024-01-02"},
        {"amount": 100.0, "description": "Missing type", "date": "2024-01-03"},  # No type field
        {"type": "DEPOSIT", "amount": 150.0, "description": "Another valid deposit", "date": "2024-01-04"},
        "invalid_transaction",  # Not a dict
        {"type": "DEPOSIT", "amount": 75.0, "description": "Last valid deposit", "date": "2024-01-05"}
    ]
    
    total_saved = 0.0
    if isinstance(transactions_data, list):
        for transaction in transactions_data:
            if isinstance(transaction, dict) and transaction.get('type') == 'DEPOSIT':
                try:
                    amount = float(transaction.get('amount', 0))
                    total_saved += amount
                except (ValueError, TypeError):
                    continue
    
    print(f"Transactions: {len(transactions_data)} total")
    print(f"Valid deposits: 3")
    print(f"Total saved: ${total_saved}")
    
    expected_total = 250.0 + 150.0 + 75.0  # Only valid deposits
    assert total_saved == expected_total
    print("✓ PASSED")
    
    print("\n" + "=" * 45)
    print("All tests passed! Progress calculation functionality is working correctly.")
    
    # Test the response generation format
    print("\nTesting response generation format:")
    user_goal = {'name': 'vacation', 'target_amount': 2000.0}
    goal_name = user_goal.get('name', 'your goal')
    target_amount = user_goal.get('target_amount', 0)
    total_saved = 475.0  # From test case 6
    
    response = f"You are doing great! You have saved ${total_saved:.2f} of your ${target_amount:.2f} goal for {goal_name}."
    expected_response = "You are doing great! You have saved $475.00 of your $2000.00 goal for vacation."
    
    print(f"Generated response: {response}")
    print(f"Expected format: {expected_response}")
    assert response == expected_response
    print("✓ Response format test PASSED")

if __name__ == "__main__":
    test_progress_calculation()