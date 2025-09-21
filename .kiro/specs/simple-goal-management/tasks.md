# Implementation Plan

- [x] 1. Set up goal storage infrastructure





  - Add global `user_goal = {}` dictionary at the top of `app.py` after imports
  - Initialize empty dictionary to store single goal data
  - _Requirements: 3.3_

- [x] 2. Implement goal detection logic





  - Create keyword detection for goal setting ("set a goal", "I want to save for", "save for", "goal")
  - Create keyword detection for progress checking ("goal progress", "how am I doing", "progress", "goal status")
  - Add conditional logic in `chat_endpoint` to branch based on detected keywords
  - _Requirements: 1.1, 2.1_

- [x] 3. Implement goal extraction functionality





  - Create Gemini prompt for extracting goal name and target amount from user message
  - Add Gemini API call to extract structured goal data from natural language input
  - Handle extraction errors gracefully with user-friendly error messages
  - _Requirements: 1.1, 4.2_

- [x] 4. Implement goal storage and confirmation





  - Store extracted goal data (name, target_amount, created_date) in `user_goal` dictionary
  - Replace existing goal when new goal is set (single goal limitation)
  - Generate confirmation response using template: "Okay, I've set a goal for you to save $[amount] for [name]"
  - _Requirements: 1.2, 1.3, 1.4_

- [x] 5. Implement progress calculation logic





  - Filter existing `transactions_data` for "DEPOSIT" type transactions only
  - Calculate total savings by summing all deposit amounts
  - Handle edge cases: no deposits (show $0), no transactions data
  - _Requirements: 2.2, 4.3_

- [x] 6. Implement progress response generation





  - Generate progress response using template: "You are doing great! You have saved $[saved_amount] of your $[target_amount] goal for your [name]"
  - Handle case where user has exceeded their goal with congratulatory message
  - Handle case where no goal is set with helpful suggestion message
  - _Requirements: 2.3, 4.1, 4.4_

- [ ] 7. Integrate goal management with existing chat flow
  - Ensure goal-related messages are processed before falling back to general Gemini chat
  - Maintain existing error handling and response format for non-goal messages
  - Test that existing chat functionality remains unaffected
  - _Requirements: 3.1, 3.2_

- [ ] 8. Add comprehensive error handling
  - Handle Gemini extraction failures with user-friendly messages
  - Handle invalid amounts with validation error messages
  - Handle transaction service failures gracefully
  - Ensure all errors fall back to existing chat functionality
  - _Requirements: 4.1, 4.2_

- [ ] 9. Create unit tests for goal functionality
  - Write tests for keyword detection with various user message phrasings
  - Write tests for goal extraction with different goal formats and edge cases
  - Write tests for progress calculation with various transaction scenarios
  - Write tests for response generation with different goal data combinations
  - _Requirements: 1.1, 1.2, 2.2, 2.3_

- [ ] 10. Create integration tests for end-to-end flows
  - Write test for complete goal setting flow from user input to storage and confirmation
  - Write test for complete progress checking flow from user input to calculation and response
  - Write test for error scenarios and fallback behaviors
  - Write test to ensure existing non-goal chat functionality remains intact
  - _Requirements: 1.1, 1.2, 1.3, 2.1, 2.2, 2.3_