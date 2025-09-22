import os
import re
import json
import logging
import requests
import google.generativeai as genai
from flask import Flask, request, jsonify, send_from_directory
import jwt
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global storage for hackathon (single user)
user_goal = {}
user_budgets = {}

# Create Flask application
app = Flask(__name__, static_folder='static')

def configure_gemini():
    """Initialize Gemini model with API key from environment."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY not found in environment variables")
        return None
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
        return model
    except Exception as e:
        logger.exception("Failed to configure Gemini model")
        return None

def get_transactions(auth_header):
    """
    Fetch transactions from the transactionhistory service.
    Returns list of transactions or empty list on error.
    """
    if not auth_header or not auth_header.startswith("Bearer "):
        logger.warning("No valid authorization header provided")
        return []
    
    try:
        jwt_token = auth_header.split(" ")[1]
        decoded_token = jwt.decode(jwt_token, options={"verify_signature": False})
        account_id = decoded_token.get('acct')
        
        if not account_id:
            logger.warning("No account ID found in JWT token")
            return []
        
        service_url = f'http://transactionhistory:8080/transactions/{account_id}'
        headers = {'Authorization': auth_header}
        
        response = requests.get(service_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        transactions_data = response.json()
        if isinstance(transactions_data, list):
            logger.info(f"Successfully fetched {len(transactions_data)} transactions")
            return transactions_data
        else:
            logger.warning("Transaction data is not a list")
            return []
            
    except jwt.PyJWTError as e:
        logger.exception("JWT token decoding failed")
        return []
    except requests.exceptions.RequestException as e:
        logger.exception("Failed to fetch transactions from service")
        return []
    except Exception as e:
        logger.exception("Unexpected error in get_transactions")
        return []

def categorize_transactions(transactions_data, model):
    """
    Categorize transactions using Gemini AI.
    Takes latest 75 transactions and adds 'category' field to each.
    """
    if not isinstance(transactions_data, list) or not transactions_data or not model:
        return transactions_data
    
    # Limit to latest 75 transactions for performance
    transactions_to_process = transactions_data[:75]
    
    try:
        # Prepare simplified transaction data for Gemini
        simplified_transactions = []
        for t in transactions_to_process:
            simplified_transactions.append({
                "amount": t.get("amount", 0),
                "description": t.get("description", "")
            })
        
        prompt = f"""
        Analyze the following bank transactions and assign each one a category from this list:
        ["Salary/Income", "Groceries", "Utilities", "Rent/Mortgage", "Transport", "Shopping", "Entertainment", "Health", "Dining", "Transfers", "Other"]
        
        IMPORTANT: Return ONLY a valid JSON array of objects. Each object must have "description", "amount", and "category" fields.
        Do not include any explanations, markdown, or extra text.
        
        Transactions:
        {json.dumps(simplified_transactions)}
        """
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Use regex to extract JSON array from response
        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if not json_match:
            raise ValueError("No valid JSON array found in Gemini response")
        
        categorized_list = json.loads(json_match.group(0))
        
        # Create mapping from (description, amount) to category
        category_mapping = {}
        for item in categorized_list:
            key = (item.get('description'), item.get('amount'))
            category_mapping[key] = item.get('category', 'Other')
        
        # Apply categories to original transactions
        for transaction in transactions_data:
            key = (transaction.get('description'), transaction.get('amount'))
            transaction['category'] = category_mapping.get(key, 'Other')
        
        logger.info("Successfully categorized transactions")
        return transactions_data
        
    except Exception as e:
        logger.exception("Error categorizing transactions")
        # Fallback: assign 'Uncategorized' to all transactions
        for transaction in transactions_data:
            transaction['category'] = 'Uncategorized'
        return transactions_data

def extract_goal_from_message(user_message, model):
    """Extract goal name and target amount from user message."""
    if not model:
        return None
    
    try:
        prompt = f"""
        Extract the financial goal information from this message:
        "{user_message}"
        
        Return ONLY a JSON object with "name" (string) and "target_amount" (number) fields.
        Example: {{"name": "vacation", "target_amount": 1500}}
        If you cannot extract both pieces of information, return: {{}}
        """
        
        response = model.generate_content(prompt)
        response_text = response.text.strip().replace("```json", "").replace("```", "").strip()
        
        goal_data = json.loads(response_text)
        if 'name' in goal_data and 'target_amount' in goal_data:
            return goal_data
        return None
        
    except Exception as e:
        logger.exception("Error extracting goal from message")
        return None

def extract_budget_from_message(user_message, model):
    """Extract budget category and amount from user message."""
    if not model:
        return None
    
    try:
        prompt = f"""
        Extract the budget information from this message:
        "{user_message}"
        
        Return ONLY a JSON object with "category" (string) and "amount" (number) fields.
        Example: {{"category": "Groceries", "amount": 500}}
        If you cannot extract both pieces of information, return: {{}}
        """
        
        response = model.generate_content(prompt)
        response_text = response.text.strip().replace("```json", "").replace("```", "").strip()
        
        budget_data = json.loads(response_text)
        if 'category' in budget_data and 'amount' in budget_data:
            return budget_data
        return None
        
    except Exception as e:
        logger.exception("Error extracting budget from message")
        return None

@app.route('/')
def index():
    """Serve the main page."""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/proactive_tip', methods=['POST'])
def proactive_tip_endpoint():
    """Find the largest expense in the last 30 days and return a helpful tip."""
    try:
        model = configure_gemini()
        if not model:
            return jsonify({}), 200
        
        auth_header = request.headers.get('Authorization')
        transactions_data = get_transactions(auth_header)
        
        if not transactions_data:
            return jsonify({}), 200
        
        # Find transactions from last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_expenses = []
        
        for transaction in transactions_data:
            try:
                date_str = transaction.get('date', '')
                if date_str:
                    transaction_date = datetime.fromisoformat(date_str.split('T')[0])
                    amount = transaction.get('amount', 0)
                    
                    # Only consider expenses (negative amounts) from last 30 days
                    if transaction_date >= thirty_days_ago and amount < 0:
                        recent_expenses.append({
                            'amount': abs(amount),
                            'description': transaction.get('description', ''),
                            'date': date_str
                        })
            except (ValueError, TypeError):
                continue
        
        if not recent_expenses:
            return jsonify({}), 200
        
        # Find the largest expense
        largest_expense = max(recent_expenses, key=lambda x: x['amount'])
        amount_dollars = largest_expense['amount'] / 100.0
        
        tip = f"I noticed your largest expense in the last 30 days was ${amount_dollars:.2f} for {largest_expense['description']}. Consider reviewing if this aligns with your financial goals."
        
        return jsonify({'tip': tip}), 200
        
    except Exception as e:
        logger.exception("Error in proactive_tip_endpoint")
        return jsonify({}), 200

@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    """
    Main chat endpoint with robust error handling and complete logic.
    CRITICAL: Every logical path MUST end with a return statement.
    """
    try:
        # Step 1: Initialize Gemini model
        model = configure_gemini()
        if not model:
            return jsonify({"error": "AI service is currently unavailable. Please try again later."}), 500
        
        # Step 2: Get user message
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': "Invalid request: missing 'message' field"}), 400
        
        user_message = data['message']
        user_message_lower = user_message.lower()
        
        # Step 3: Fetch raw transaction data
        auth_header = request.headers.get('Authorization')
        transactions_data = get_transactions(auth_header)
        
        # Step 4: IMMEDIATELY categorize transactions
        transactions_data = categorize_transactions(transactions_data, model)
        
        # Step 5: Intent handling with if/elif/else structure
        
        # Intent 1: Set Goal
        if any(keyword in user_message_lower for keyword in ["set a goal", "i want to save", "save for", "goal to save"]):
            try:
                goal_data = extract_goal_from_message(user_message, model)
                if goal_data:
                    user_goal['name'] = goal_data['name']
                    user_goal['target'] = float(goal_data['target_amount'])
                    user_goal['start_date'] = datetime.now().isoformat()
                    reply_text = f"Perfect! I've set a savings goal of ${user_goal['target']:.2f} for your {user_goal['name']}. I'll help you track your progress!"
                else:
                    reply_text = "I couldn't understand your goal. Please try again with something like: 'I want to save $1000 for a vacation'"
                return jsonify({'reply': reply_text}), 200
            except Exception as e:
                logging.exception("Error in set goal intent")
                return jsonify({'reply': "I'm having trouble setting up your goal right now. Please try again."}), 200
        
        # Intent 2: Set Budget
        elif any(keyword in user_message_lower for keyword in ["set a budget", "my budget is", "budget for"]):
            try:
                budget_data = extract_budget_from_message(user_message, model)
                if budget_data:
                    category = budget_data['category'].title()
                    amount = float(budget_data['amount'])
                    user_budgets[category] = amount
                    reply_text = f"Great! I've set a monthly budget of ${amount:.2f} for {category}. I'll help you track your spending in this category."
                else:
                    reply_text = "I couldn't understand your budget. Please try again with something like: 'Set a $500 budget for Groceries'"
                return jsonify({'reply': reply_text}), 200
            except Exception as e:
                logging.exception("Error in set budget intent")
                return jsonify({'reply': "I'm having trouble setting up your budget right now. Please try again."}), 200
        
        # Intent 3: Check Budget
        elif any(keyword in user_message_lower for keyword in ["check my budget", "budget status", "how is my budget"]):
            try:
                if not user_budgets:
                    return jsonify({'reply': "You haven't set any budgets yet. Try saying 'Set a $500 budget for Groceries' to get started!"}), 200
                
                # Find which category the user is asking about
                asked_category = None
                for category in user_budgets.keys():
                    if category.lower() in user_message_lower:
                        asked_category = category
                        break
                
                if not asked_category:
                    categories_list = ", ".join(user_budgets.keys())
                    return jsonify({'reply': f"Which budget would you like to check? You have budgets for: {categories_list}"}), 200
                
                # Calculate spending for this category in current month
                budget_amount = user_budgets[asked_category]
                total_spent = 0.0
                current_month = datetime.now().month
                current_year = datetime.now().year
                
                if isinstance(transactions_data, list):
                    for transaction in transactions_data:
                        try:
                            date_str = transaction.get('date', '')
                            if date_str:
                                transaction_date = datetime.fromisoformat(date_str.split('T')[0])
                                amount = transaction.get('amount', 0)
                                category = transaction.get('category', '')
                                
                                # Only count negative amounts (expenses) in the current month for this category
                                if (transaction_date.month == current_month and
                                    transaction_date.year == current_year and
                                    amount < 0 and
                                    category == asked_category):
                                    total_spent += abs(amount) / 100.0  # Convert cents to dollars
                        except (ValueError, TypeError):
                            continue
                
                remaining_budget = budget_amount - total_spent
                
                if total_spent == 0:
                    reply_text = f"Good news! You haven't spent anything from your {asked_category} budget of ${budget_amount:.2f} this month."
                elif remaining_budget >= 0:
                    percentage_used = (total_spent / budget_amount) * 100
                    reply_text = f"For your {asked_category} budget of ${budget_amount:.2f}, you've spent ${total_spent:.2f} ({percentage_used:.1f}%). You have ${remaining_budget:.2f} remaining this month."
                else:
                    overspent = abs(remaining_budget)
                    reply_text = f"Alert! You've exceeded your {asked_category} budget of ${budget_amount:.2f}. You've spent ${total_spent:.2f}, which is ${overspent:.2f} over budget this month."
                
                return jsonify({'reply': reply_text}), 200
            except Exception as e:
                logging.exception("Error in check budget intent")
                return jsonify({'reply': "I'm having trouble checking your budget right now. Please try again."}), 200
        
        # Intent 4: Check Goal Progress
        elif any(keyword in user_message_lower for keyword in ["goal progress", "how am i doing", "my goal", "check goal"]):
            try:
                if not user_goal:
                    return jsonify({'reply': "You haven't set a savings goal yet. Try saying 'I want to save $1000 for a vacation' to get started!"}), 200
                
                # Calculate total savings since goal was set
                total_saved = 0.0
                goal_start_date = None
                
                if 'start_date' in user_goal:
                    try:
                        goal_start_date = datetime.fromisoformat(user_goal['start_date'].split('T')[0])
                    except (ValueError, TypeError):
                        goal_start_date = None
                
                if isinstance(transactions_data, list):
                    for transaction in transactions_data:
                        try:
                            amount = transaction.get('amount', 0)
                            # Only count positive amounts (deposits/income) as savings
                            if amount > 0:
                                if goal_start_date:
                                    date_str = transaction.get('date', '')
                                    if date_str:
                                        transaction_date = datetime.fromisoformat(date_str.split('T')[0])
                                        if transaction_date >= goal_start_date:
                                            total_saved += amount / 100.0  # Convert cents to dollars
                                else:
                                    total_saved += amount / 100.0
                        except (ValueError, TypeError):
                            continue
                
                goal_name = user_goal.get('name', 'your goal')
                target_amount = user_goal.get('target', 0)
                
                # Generate progress response
                if total_saved >= target_amount:
                    excess = total_saved - target_amount
                    reply_text = f"🎉 Congratulations! You've exceeded your savings goal! You've saved ${total_saved:.2f} for your {goal_name}, which is ${excess:.2f} more than your ${target_amount:.2f} target. Amazing work!"
                else:
                    percentage_complete = (total_saved / target_amount) * 100 if target_amount > 0 else 0
                    remaining = target_amount - total_saved
                    reply_text = f"Great progress! You've saved ${total_saved:.2f} of your ${target_amount:.2f} goal for your {goal_name} ({percentage_complete:.1f}% complete). You need ${remaining:.2f} more to reach your goal!"
                
                return jsonify({'reply': reply_text}), 200
            except Exception as e:
                logging.exception("Error in check goal progress intent")
                return jsonify({'reply': "I'm having trouble checking your goal progress right now. Please try again."}), 200
        
        # Intent 5: General Q&A (default case)
        else:
            try:
                system_instruction = """
                You are a helpful and friendly financial co-pilot for a bank customer.
                Provide clear, concise answers based on the transaction data provided.
                - Give direct answers in the first sentence
                - Keep responses conversational and helpful
                - Don't use markdown formatting
                - If asked about spending patterns, use the categorized transaction data
                """
                
                # Format transaction data for Gemini (limit for performance)
                if isinstance(transactions_data, list) and transactions_data:
                    recent_transactions = transactions_data[:30]  # Latest 30 transactions
                    transaction_summary = f"Recent Transaction Data:\n{json.dumps(recent_transactions, indent=2)}"
                else:
                    transaction_summary = "No transaction data available."
                
                combined_prompt = f"{system_instruction}\n\n{transaction_summary}\n\nUser Question: {user_message}"
                
                response = model.generate_content(combined_prompt)
                reply_text = response.text.strip()
                
                return jsonify({'reply': reply_text}), 200
            except Exception as e:
                logging.exception("Error in general Q&A intent")
                return jsonify({'reply': "I'm having trouble processing your question right now. Please try again or rephrase your question."}), 200
    
    except Exception as e:
        logging.exception("Unexpected error in chat_endpoint")
        return jsonify({'error': 'An unexpected error occurred. Please try again.'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)