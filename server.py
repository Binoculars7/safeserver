from flask import Flask, request, jsonify
from flask_cors import CORS
import os

# Try to import openai, but don't crash if it fails
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("WARNING: OpenAI library not installed")

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Set your OpenAI API key from environment variable
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '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')

# Initialize OpenAI client if available
if OPENAI_AVAILABLE and OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)
else:
    client = None

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'status': 'running',
        'message': 'SafeNaija Classification API',
        'openai_available': OPENAI_AVAILABLE,
        'openai_configured': bool(OPENAI_API_KEY)
    })

@app.route('/classify', methods=['POST', 'OPTIONS'])
def classify():
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        if not OPENAI_AVAILABLE or not client:
            return jsonify({
                'error': 'OpenAI not configured properly',
                'success': False
            }), 500
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided', 'success': False}), 400
            
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided', 'success': False}), 400
        
        print(f"Classifying: {text}")
        
        # Create the prompt
        prompt = f"""Classify this emergency into ONE category. Return ONLY the category name.

Categories: accident, fire, robbery, kidnapping, fraud, health, vandalism, misplace

Emergency: "{text}"

Category (one word only):"""
        
        # Call OpenAI API with new syntax
        response = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[
                {
                    'role': 'system',
                    'content': 'You must respond with ONLY ONE word from this list: accident, fire, robbery, kidnapping, fraud, health, vandalism, misplace. No other text.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            temperature=0,
            max_tokens=5
        )
        
        category = response.choices[0].message.content.strip().lower()
        
        # Clean the category
        category = ''.join(c for c in category if c.isalpha())
        
        print(f"Result: {category}")
        
        return jsonify({
            'category': category,
            'success': True
        })
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok', 
        'openai_available': OPENAI_AVAILABLE,
        'openai_configured': bool(OPENAI_API_KEY)
    })

if __name__ == '__main__':
    # Get port from environment variable (for deployment) or use 5000 (for local)
    port = int(os.environ.get('PORT', 5000))
    print("🚀 Starting SafeNaija Classification Server...")
    print(f"📡 Server will run on port {port}")
    print(f"🔑 OpenAI Available: {OPENAI_AVAILABLE}")
    print(f"🔑 OpenAI Configured: {bool(OPENAI_API_KEY)}")
    app.run(debug=False, host='0.0.0.0', port=port)
