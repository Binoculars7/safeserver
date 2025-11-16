from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Set your OpenAI API key
openai.api_key = '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'

@app.route('/classify', methods=['POST'])
def classify():
    try:
        data = request.get_json()
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Create the prompt
        prompt = f"""Classify this emergency into ONE category. Return ONLY the category name.

Categories: accident, fire, robbery, kidnapping, fraud, health, vandalism, misplace

Emergency: "{text}"

Category (one word only):"""
        
        # Call OpenAI API
        response = openai.ChatCompletion.create(
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
        
        print(f"Classified '{text}' as '{category}'")
        
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
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    # Get port from environment variable (for deployment) or use 5000 (for local)
    port = int(os.environ.get('PORT', 5000))
    print("🚀 Starting SafeNaija Classification Server...")
    print(f"📡 Server will run on port {port}")
    app.run(debug=False, host='0.0.0.0', port=port)
else:
    # For production (Render, etc.)
    print("🚀 Running in production mode")
