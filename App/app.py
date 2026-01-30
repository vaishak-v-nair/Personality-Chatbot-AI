from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import joblib
import re
import os
import warnings
from groq import Groq

# Silence scikit-learn InconsistentVersionWarning when unpickling models
try:
    from sklearn.exceptions import InconsistentVersionWarning
    warnings.filterwarnings("ignore", category=InconsistentVersionWarning)
except Exception:
    pass

# Initialize Flask app with custom template and static folders
app = Flask(__name__, 
            template_folder='.',  # Templates in root directory
            static_folder='.',     # Static files in root directory
            static_url_path='')
CORS(app)

# 1. Load your trained models
try:
    model = joblib.load('personality_model.pkl')
    vectorizer = joblib.load('vectorizer.pkl')
    print("✓ Models loaded successfully.")
except FileNotFoundError as e:
    print(f"✗ Error: Model files not found - {e}")
    print("  Ensure 'personality_model.pkl' and 'vectorizer.pkl' are in the directory.")

# 2. INITIALIZE GROQ CLIENT
# IMPORTANT: Set your actual API key via environment variable or .env
GROQ_API_KEY = "Add Groq API key"
groq_api_key = os.environ.get("GROQ_API_KEY", GROQ_API_KEY)

if groq_api_key:
    try:
        client = Groq(api_key=groq_api_key)
        print("✓ Groq client initialized.")
    except Exception as e:
        client = None
        print(f"✗ Groq initialization failed: {e}")
else:
    client = None
    print("⚠ Warning: GROQ_API_KEY not set; Groq client disabled.")

# 3. Define Communication Styles for each MBTI type
personality_styles = {
    "INTJ": "The user is an INTJ. Be logical, strategic, and concise. Provide well-structured insights.",
    "INTP": "The user is an INTP. Be analytical, precise, and abstract. Encourage intellectual exploration.",
    "ENTJ": "The user is an ENTJ. Be direct, efficient, and commanding. Focus on results and leadership.",
    "ENTP": "The user is an ENTP. Be witty, debate-friendly, and innovative. Challenge ideas constructively.",
    "INFJ": "The user is an INFJ. Be empathetic, deep, and insightful. Connect on an emotional level.",
    "INFP": "The user is an INFP. Be gentle, authentic, and imaginative. Honor their values and creativity.",
    "ENFJ": "The user is an ENFJ. Be inspiring, warm, and collaborative. Encourage growth and harmony.",
    "ENFP": "The user is an ENFP. Be enthusiastic, creative, and spontaneous. Share excitement for possibilities.",
    "ISTJ": "The user is an ISTJ. Be factual, reliable, and structured. Provide clear, practical information.",
    "ISFJ": "The user is an ISFJ. Be supportive, polite, and detailed. Show care and consideration.",
    "ESTJ": "The user is an ESTJ. Be practical, organized, and decisive. Focus on efficiency and order.",
    "ESFJ": "The user is an ESFJ. Be friendly, helpful, and community-focused. Emphasize relationships.",
    "ISTP": "The user is an ISTP. Be practical, calm, and solution-focused. Get straight to the point.",
    "ISFP": "The user is an ISFP. Be observant, kind, and artistic. Appreciate their unique perspective.",
    "ESTP": "The user is an ESTP. Be energetic, direct, and action-oriented. Make it exciting and dynamic.",
    "ESFP": "The user is an ESFP. Be fun, lively, and entertaining. Bring energy and positivity."
}

def clean_post(text):
    """Clean and preprocess text for personality prediction"""
    if text is None: 
        return ""
    text = str(text).lower()
    text = re.sub(r'http\S+', '', text)  # Remove URLs
    text = re.sub(r'[^a-z\s]', ' ', text)  # Keep only letters and spaces
    text = re.sub(r'\s+', ' ', text).strip()  # Remove extra whitespace
    return text

# Routes
@app.route('/')
def home():
    """Serve the main chatbot page"""
    return render_template('index.html')

@app.route('/styles.css')
def serve_css():
    """Serve the CSS file"""
    return send_from_directory('.', 'styles.css', mimetype='text/css')

@app.route('/script.js')
def serve_js():
    """Serve the JavaScript file"""
    return send_from_directory('.', 'script.js', mimetype='application/javascript')

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages and return personality-based responses"""
    try:
        data = request.get_json(force=True)
        user_input = data.get('text', '')
        
        if not user_input:
            return jsonify({
                'prediction': 'UNKNOWN',
                'response': 'Please type something so I can detect your personality!'
            })
        
        # A. Predict Personality Type
        cleaned_text = clean_post(user_input)
        vectorized_text = vectorizer.transform([cleaned_text])
        predicted_type = model.predict(vectorized_text)[0]
        
        print(f"🔍 Detected personality: {predicted_type}")
        
        # B. Get Style Instruction for this personality
        style_instruction = personality_styles.get(
            predicted_type, 
            "Be helpful and adaptive to the user's needs."
        )
        
        # C. Generate Response using Groq AI
        if client is None:
            bot_response = (
                "I've detected your personality type, but I'm not fully configured yet. "
                "Please set up the Groq API key to enable personalized AI responses."
            )
        else:
            try:
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",  # Using a reliable Groq model
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                f"You are a helpful AI assistant in an MBTI personality chatbot. "
                                f"{style_instruction} Adapt your communication style accordingly. "
                                f"Keep responses conversational, friendly, and concise (2-4 sentences max)."
                            )
                        },
                        {
                            "role": "user",
                            "content": user_input
                        }
                    ],
                    temperature=0.7,
                    max_tokens=150,  # Keep responses concise
                    top_p=0.9,
                )
                bot_response = completion.choices[0].message.content.strip()
                print(f"✓ Response generated successfully")
                
            except Exception as e:
                print(f"✗ Groq Error: {e}")
                bot_response = (
                    "I'm having trouble generating a response right now. "
                    "Please try again in a moment!"
                )
        
        return jsonify({
            'prediction': predicted_type,
            'response': bot_response
        })
        
    except Exception as e:
        print(f"✗ Error in /chat endpoint: {e}")
        return jsonify({
            'prediction': 'ERROR',
            'response': 'Something went wrong. Please try again.'
        }), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'models_loaded': 'model' in globals() and 'vectorizer' in globals(),
        'groq_configured': client is not None
    })

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 MBTI Personality Chatbot Server")
    print("="*50)
    print(f"📍 Running on: http://127.0.0.1:5000")
    print(f"🌐 Open this URL in your browser to start chatting!")
    print("="*50 + "\n")
    
    app.run(debug=True, host='127.0.0.1', port=5000)