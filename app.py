import os
import requests
import google.generativeai as genai
from flask import Flask, request, jsonify, send_from_directory
import jwt
import json
import re
from datetime import datetime
import logging

# --- Global In-Memory Storage ---
# For a real app, this would be a database.
user_goal = {}
user_budgets = {}

# --- Flask App Initialization ---
app = Flask(__name__, static_folder='static')

# --- Helper Functions ---

def configure_gemini():
    """Configures and returns a Gemini model instance."""
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logging.error("GEMINI_API_KEY environment variable not set.")
            return None
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
        return model
    except Exception as e:
        logging.exception("Failed to configure Gemini.")
        return None

def get_transactions(auth_header):
    """Fetches transactions from the transactionhistory service."""
    if not (auth_header and auth_header.startswith("Bearer ")):
        return []
    
    jwt_token = auth_header.split(" ")[1]
    headers = {'Authorization': auth_header}
    try:
        decoded_token = jwt.decode(jwt_token, options={"verify_signature": False})
        account_id = decoded_token.get('acct')
        if account_id:
            service_url = f'http://transactionhistory:8080/transactions/{account_id}'
            response = requests.get(service_url, headers=headers, timeout=5)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logging.exception("Failed to fetch transactions.")
    return []

def categorize_transactions(transactions_data, model):
    """Uses Gemini to add a 'category' to each transaction."""
    if not isinstance(transactions_data, list) or not transactions_data:
        return transactions_data
    
    transactions_to_process = transactions_data[:75]  # Limit to 75 most recent for stability
    
    try:
        simplified_transactions = [{"amount": t.get("amount"), "description": t.get("description")} for t in transactions_to_process]
        prompt = f"""
        Analyze the following list of bank transactions. For each transaction, assign a relevant category from this list:
        ["Salary/Income", "Groceries", "Utilities", "Rent/Mortgage", "Transport", "Shopping", "Entertainment", "Health", "Dining", "Transfers", "Other"].
        IMPORTANT: Your entire response must be ONLY a valid JSON list of objects, without any extra text, explanations, or markdown. Each object must contain "description", "amount", and a new "category" key.
        Transaction Data:
        {json.dumps(simplified_transactions)}
        """
        response = model.generate_content(prompt)
        json_match = re.search(r'\[.*\]', response.text, re.DOTALL)
        if not json_match:
            raise ValueError("No valid JSON list found in Gemini's response.")
        
        categorized_list = json.loads(json_match.group(0))
        desc_amount_to_category = {(item.get('description'), item.get('amount')): item.get('category', 'Other') for item in categorized_list}

        for t in transactions_data:
            key = (t.get('description'), t.get('amount'))
            t['category'] = desc_amount_to_category.get(key, 'Other')
            
        return transactions_data
    except Exception as e:
        logging.exception("An error occurred during categorization.")
        for t in transactions_data:
            t["category"] = "Uncategorized"
        return transactions_data

# --- Flask Routes ---

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/proactive_tip', methods=['POST'])
def proactive_tip_endpoint():
    """Provides a proactive financial tip based on recent transactions."""
    auth_header = request.headers.get('Authorization')
    transactions = get_transactions(auth_header)
    
    if not isinstance(transactions, list) or not transactions:
        return jsonify({}), 200

    # Find the largest expense in the last 30 days
    largest_expense = None
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    for t in transactions:
        try:
            transaction_date = datetime.fromisoformat(t['date'].split('T')[0])
            if transaction_date >= thirty_days_ago and t.get('amount', 0) < 0:
                if largest_expense is None or abs(t['amount']) > abs(largest_expense['amount']):
                    largest_expense = t
        except (ValueError, KeyError):
            continue
            
    if largest_expense:
        amount_dollars = abs(largest_expense['amount']) / 100.0
        tip = f"Proactive Tip: Your largest expense in the last 30 days was ${amount_dollars:.2f} for '{largest_expense.get('description', 'an item')}'. Reviewing large expenses can help you save more!"
        return jsonify({"tip": tip}), 200
        
    return jsonify({}), 200

@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    """Main chat endpoint to handle all user intents."""
    model = configure_gemini()
    if not model:
        return jsonify({"error": "API Key not configured"}), 500
        
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"error": "Invalid request"}), 400
        
    user_message = data['message']
    user_message_lower = user_message.lower()

    # Get and categorize transactions
    auth_header = request.headers.get('Authorization')
    transactions_data = get_transactions(auth_header)
    transactions_data = categorize_transactions(transactions_data, model)
    
    # --- Intent Handling ---
    
    # 1. Set Goal
    if any(k in user_message_lower for k in ["set a goal", "i want to save"]):
        # ... (goal setting logic here, as it doesn't need transactions)
        return jsonify({'reply': "Goal setting logic goes here."})

    # 2. Set Budget
    elif any(k in user_message_lower for k in ["set a budget", "budget for"]):
        # ... (budget setting logic here) ...
        return jsonify({'reply': "Budget setting logic goes here."})
    
    # 3. Check Budget
    elif any(k in user_message_lower for k in ["check my budget", "how is my budget"]):
        # ... (budget checking logic here) ...
        return jsonify({'reply': "Budget checking logic goes here."})
    
    # 4. Check Goal Progress
    elif any(k in user_message_lower for k in ["check goal", "how am i doing"]):
        # ... (goal progress logic here) ...
        return jsonify({'reply': "Goal progress logic goes here."})

    # 5. General Q&A
    else:
        try:
            system_instruction = "You are a helpful financial co-pilot..."
            prompt = f"{system_instruction}\n\nTransaction Data:\n{json.dumps(transactions_data)}\n\nUser's Question:\n{user_message}"
            response = model.generate_content(prompt)
            return jsonify({'reply': response.text}), 200
        except Exception:
            logging.exception("Error in general Q&A")
            return jsonify({'reply': 'Sorry, I encountered an error.'}), 500

if __name__ == '__main__':
    # Add timedelta for proactive tip logic
    from datetime import timedelta
    app.run(host='0.0.0.0', port=8080)