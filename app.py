from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import joblib
import re
import os
import warnings
from groq import Groq  # Import the official Groq client
from dotenv import load_dotenv

# Load environment variables from .env if it exists
from pathlib import Path
project_root = Path(__file__).resolve().parent
load_dotenv(dotenv_path=project_root / '.env')

# Silence scikit-learn InconsistentVersionWarning when unpickling models
try:
    from sklearn.exceptions import InconsistentVersionWarning
    warnings.filterwarnings("ignore", category=InconsistentVersionWarning)
except Exception:
    pass

app = Flask(__name__, template_folder='Frontend', static_folder='Frontend', static_url_path='')
CORS(app)

# 1. Load your trained models
try:
    model = joblib.load('personality_model.pkl')
    vectorizer = joblib.load('vectorizer.pkl')
    print("Models loaded successfully.")
except FileNotFoundError:
    print("Error: Files not found. Ensure .pkl files are in the directory.")

# ---------------------------------------------------------
# 2. INITIALIZE GROQ CLIENT
# Read API key from environment variable `GROQ_API_KEY`.
groq_api_key = os.environ.get("GROQ_API_KEY")
# Debug printing (masked) to help troubleshoot env loading
def _mask_key(k: str) -> str:
    if not k:
        return None
    return k[:4] + "..." + k[-4:]

print(f"Working directory: {os.getcwd()}")
print(f"Looking for .env at: {project_root / '.env'} (exists={ (project_root / '.env').exists() })")
print(f"Resolved GROQ_API_KEY: {_mask_key(groq_api_key)}")

if groq_api_key:
    try:
        client = Groq(api_key=groq_api_key)
        print("Groq client initialized.")
    except Exception as e:
        client = None
        print(f"Groq initialization failed: {e}")
else:
    client = None
    print("Warning: GROQ_API_KEY not set; Groq client disabled.")


# 3. Define Communication Styles
personality_styles = {
    "INTJ": "The user is an INTJ. Be logical, strategic, and concise.",
    "INTP": "The user is an INTP. Be analytical, precise, and abstract.",
    "ENTJ": "The user is an ENTJ. Be direct, efficient, and commanding.",
    "ENTP": "The user is an ENTP. Be witty, debate-friendly, and innovative.",
    "INFJ": "The user is an INFJ. Be empathetic, deep, and insightful.",
    "INFP": "The user is an INFP. Be gentle, authentic, and imaginative.",
    "ENFJ": "The user is an ENFJ. Be inspiring, warm, and collaborative.",
    "ENFP": "The user is an ENFP. Be enthusiastic, creative, and spontaneous.",
    "ISTJ": "The user is an ISTJ. Be factual, reliable, and structured.",
    "ISFJ": "The user is an ISFJ. Be supportive, polite, and detailed.",
    "ESTJ": "The user is an ESTJ. Be practical, organized, and decisive.",
    "ESFJ": "The user is an ESFJ. Be friendly, helpful, and community-focused.",
    "ISTP": "The user is an ISTP. Be practical, calm, and solution-focused.",
    "ISFP": "The user is an ISFP. Be observant, kind, and artistic.",
    "ESTP": "The user is an ESTP. Be energetic, direct, and action-oriented.",
    "ESFP": "The user is an ESFP. Be fun, lively, and entertaining."
}

def clean_post(text):
    if text is None: return ""
    text = str(text).lower()
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^a-z\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

@app.route('/')
def home():
    return render_template('personality.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json(force=True)
    user_input = data.get('text', '')
    
    # A. Predict Personality
    cleaned_text = clean_post(user_input)
    vectorized_text = vectorizer.transform([cleaned_text])
    predicted_type = model.predict(vectorized_text)[0]
    
    # B. Get Style Instruction
    style_instruction = personality_styles.get(predicted_type, "Be helpful.")
    
    # C. Generate Response using GROQ (if configured)
    if client is None:
        bot_response = "Groq client is not configured. Set the GROQ_API_KEY environment variable to enable AI responses."
    else:
        try:
            completion = client.chat.completions.create(
                model="moonshotai/kimi-k2-instruct-0905",
                messages=[
                    {
                        "role": "system",
                        "content": f"You are a helpful AI assistant. {style_instruction}"
                    },
                    {
                        "role": "user",
                        "content": user_input
                    }
                ],
                temperature=0.7,
                max_tokens=1024,
                top_p=1,
            )
            bot_response = completion.choices[0].message.content
        except Exception as e:
            print(f"Groq Error: {e}")
            bot_response = "I'm having trouble connecting right now."

    return jsonify({
        'prediction': predicted_type,
        'response': bot_response
    })

if __name__ == '__main__':
    app.run(debug=True)
