# Design Document

## Overview

The simple goal management feature will be integrated into the existing Flask application by extending the `chat_endpoint` function. The feature will use natural language processing via the existing Gemini AI integration to detect goal-setting and progress-checking intents, then perform appropriate actions using an in-memory storage system.

## Architecture

### High-Level Flow
1. User sends a message through the existing chat interface
2. The `chat_endpoint` function processes the message for goal-related keywords
3. If goal keywords are detected, the system branches to goal-specific logic
4. Goal data is stored/retrieved from in-memory dictionary
5. Transaction data is analyzed for progress calculations
6. Appropriate response is generated and returned

### Integration Points
- **Existing Chat Endpoint**: All goal management logic will be embedded within the current `chat_endpoint` function
- **Gemini AI**: Leverage existing Gemini integration for natural language processing and goal extraction
- **Transaction Data**: Use existing transaction retrieval mechanism to calculate savings progress
- **Response System**: Utilize existing JSON response format for consistency

## Components and Interfaces

### Data Storage Component
```python
# Global in-memory storage at module level
user_goal = {}
```

**Structure:**
```python
user_goal = {
    "name": "trip",           # Goal name extracted from user input
    "target_amount": 500.0,   # Target amount as float
    "created_date": "2024-01-15"  # ISO date string for tracking
}
```

### Goal Detection Component
**Purpose**: Identify goal-related intents in user messages

**Keywords for Goal Setting**:
- "set a goal"
- "I want to save for"
- "save for"
- "goal"

**Keywords for Progress Checking**:
- "goal progress"
- "how am I doing"
- "progress"
- "goal status"

### Goal Extraction Component
**Purpose**: Use Gemini AI to extract structured goal information from natural language

**Input**: User message containing goal-setting intent
**Output**: Dictionary with goal name and target amount
**Method**: Dedicated Gemini API call with specific prompt for extraction

### Progress Calculation Component
**Purpose**: Calculate savings progress based on transaction history

**Logic**:
1. Filter transactions for "DEPOSIT" type only
2. Sum all deposit amounts
3. Calculate percentage progress: (saved_amount / target_amount) * 100
4. Handle edge cases (no deposits, exceeding goal)

### Response Generation Component
**Purpose**: Generate appropriate responses based on goal operations

**Goal Setting Response Template**:
```
"Okay, I've set a goal for you to save $[amount] for [name]."
```

**Progress Response Template**:
```
"You are doing great! You have saved $[saved_amount] of your $[target_amount] goal for your [name]."
```

## Data Models

### Goal Model
```python
{
    "name": str,           # Required: Goal description/name
    "target_amount": float, # Required: Target savings amount
    "created_date": str    # Optional: ISO date string
}
```

### Transaction Model (Existing)
```python
{
    "type": str,           # "DEPOSIT" or "WITHDRAWAL"
    "amount": float,       # Transaction amount
    "description": str,    # Transaction description
    "date": str           # Transaction date
}
```

## Error Handling

### Goal Setting Errors
1. **Extraction Failure**: If Gemini cannot extract goal information
   - Response: "I couldn't understand your goal. Could you please specify what you want to save for and how much?"
   
2. **Invalid Amount**: If extracted amount is not a valid number
   - Response: "Please specify a valid dollar amount for your goal."

### Progress Checking Errors
1. **No Goal Set**: If user asks for progress but no goal exists
   - Response: "You haven't set a savings goal yet. Would you like to set one?"
   
2. **Transaction Data Unavailable**: If transaction service fails
   - Response: "I'm having trouble accessing your transaction data right now. Please try again later."

### General Error Handling
- All goal-related errors should gracefully fall back to the existing chat functionality
- Log errors for debugging but don't expose technical details to users
- Maintain existing error response format for consistency

## Testing Strategy

### Unit Testing Areas
1. **Keyword Detection**: Test various phrasings for goal setting and progress checking
2. **Goal Extraction**: Test Gemini integration with different goal formats
3. **Progress Calculation**: Test deposit summation with various transaction scenarios
4. **Response Generation**: Test template formatting with different goal data

### Integration Testing Areas
1. **End-to-End Goal Setting**: Full flow from user input to goal storage
2. **End-to-End Progress Checking**: Full flow from user input to progress calculation
3. **Error Scenarios**: Test all error conditions and fallback behaviors
4. **Existing Functionality**: Ensure non-goal messages still work correctly

### Test Data Requirements
- Sample transaction data with various deposit amounts and dates
- Sample user messages for goal setting with different phrasings
- Sample user messages for progress checking with different phrasings
- Edge case scenarios (no deposits, very large amounts, etc.)

## Implementation Considerations

### Performance
- In-memory storage is acceptable for single-user demo/prototype
- Goal extraction via Gemini adds latency but provides flexibility
- Transaction data processing is minimal (simple filtering and summation)

### Scalability Limitations
- Single goal per user limitation is by design for simplicity
- In-memory storage will not persist across application restarts
- No user isolation (single global goal dictionary)

### Security
- No additional security concerns beyond existing application
- Goal data is not sensitive financial information
- Leverage existing authentication/authorization mechanisms

### Future Enhancements
- Multiple goals per user
- Persistent storage (database)
- Goal categories and tags
- Progress notifications and reminders
- Goal achievement celebrations