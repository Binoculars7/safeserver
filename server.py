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
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# Remove the hardcoded API key for security!
# Initialize OpenAI client if available
client = None
if OPENAI_AVAILABLE and OPENAI_API_KEY:
    try:
        # Use simpler initialization to avoid proxy issues
        client = OpenAI(api_key=OPENAI_API_KEY)
        # Test the client with a simple call to verify it works
        print("✅ OpenAI client initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing OpenAI client: {str(e)}")
        client = None
else:
    print(f"⚠️  OpenAI not available - Available: {OPENAI_AVAILABLE}, API Key: {'Set' if OPENAI_API_KEY else 'Not set'}")

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'status': 'running',
        'message': 'SafeNaija Classification API',
        'openai_available': OPENAI_AVAILABLE,
        'openai_configured': bool(OPENAI_API_KEY),
        'openai_client_ready': client is not None
    })

@app.route('/classify', methods=['POST', 'OPTIONS'])
def classify():
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        if not client:
            return jsonify({
                'error': 'OpenAI client not configured properly',
                'openai_available': OPENAI_AVAILABLE,
                'openai_configured': bool(OPENAI_API_KEY),
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
        print(f"Error in classify: {str(e)}")
        return jsonify({
            'error': 'Internal server error during classification',
            'success': False
        }), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok', 
        'openai_available': OPENAI_AVAILABLE,
        'openai_configured': bool(OPENAI_API_KEY),
        'openai_client_ready': client is not None
    })

# Test endpoint to verify OpenAI connectivity
@app.route('/test-openai', methods=['GET'])
def test_openai():
    if not client:
        return jsonify({'error': 'OpenAI client not available'}), 500
    
    try:
        # Simple test call
        response = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[{'role': 'user', 'content': 'Say "hello"'}],
            max_tokens=5
        )
        return jsonify({
            'success': True,
            'response': response.choices[0].message.content
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

if __name__ == '__main__':
    # Get port from environment variable (for deployment) or use 5000 (for local)
    port = int(os.environ.get('PORT', 5000))
    print("🚀 Starting SafeNaija Classification Server...")
    print(f"📡 Server will run on port {port}")
    print(f"🔑 OpenAI Available: {OPENAI_AVAILABLE}")
    print(f"🔑 OpenAI Configured: {bool(OPENAI_API_KEY)}")
    print(f"🔑 OpenAI Client Ready: {client is not None}")
    app.run(debug=False, host='0.0.0.0', port=port)
