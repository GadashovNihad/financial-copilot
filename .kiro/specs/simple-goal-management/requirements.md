# Requirements Document

## Introduction

This feature implements a simple financial goal management system that allows users to set a single savings goal and track their progress through natural language interactions. The system will integrate with existing transaction data to calculate savings progress and provide feedback to users about their goal achievement.

## Requirements

### Requirement 1

**User Story:** As a user, I want to set a financial savings goal through natural language, so that I can track my progress toward a specific target.

#### Acceptance Criteria

1. WHEN the user's message contains keywords like "set a goal" or "I want to save for" THEN the system SHALL extract the goal name and target amount using AI processing
2. WHEN a goal is successfully extracted THEN the system SHALL store the goal in an in-memory dictionary with goal name and target amount
3. WHEN a goal is stored THEN the system SHALL respond with confirmation message "Okay, I've set a goal for you to save [amount] for [name]"
4. WHEN a user sets a new goal THEN the system SHALL replace any existing goal (only one goal at a time)

### Requirement 2

**User Story:** As a user, I want to check my progress toward my savings goal through natural language, so that I can understand how close I am to achieving it.

#### Acceptance Criteria

1. WHEN the user's message contains keywords like "goal progress" or "how am I doing" THEN the system SHALL retrieve the current goal from storage
2. WHEN checking progress AND a goal exists THEN the system SHALL calculate total savings from all "DEPOSIT" type transactions
3. WHEN progress is calculated THEN the system SHALL respond with "You are doing great! You have saved [saved_amount] of your $[target_amount] goal for your [name]"
4. WHEN checking progress AND no goal exists THEN the system SHALL inform the user that no goal is currently set

### Requirement 3

**User Story:** As a developer, I want all goal management functionality integrated into the existing chat endpoint, so that the feature works seamlessly with the current application architecture.

#### Acceptance Criteria

1. WHEN implementing goal management THEN the system SHALL add all new logic inside the existing `chat_endpoint` function
2. WHEN implementing goal management THEN the system SHALL NOT create new API endpoints
3. WHEN implementing goal management THEN the system SHALL use a simple Python dictionary named `user_goal` at the top of `app.py` for storage
4. WHEN implementing goal management THEN the system SHALL integrate with existing `transactions_data` for progress calculations

### Requirement 4

**User Story:** As a user, I want the system to handle edge cases gracefully, so that I have a smooth experience even when things don't go as expected.

#### Acceptance Criteria

1. WHEN the user asks about progress AND no goal is set THEN the system SHALL provide a helpful message suggesting they set a goal first
2. WHEN the system cannot extract goal information from user input THEN the system SHALL ask for clarification
3. WHEN calculating progress AND no deposit transactions exist THEN the system SHALL show $0 saved toward the goal
4. WHEN the user has saved more than their target amount THEN the system SHALL congratulate them on exceeding their goal