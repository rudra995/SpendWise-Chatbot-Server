from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel(model_name="models/gemini-1.5-pro")

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route("/")
def home():
    return "Chatbot server running..."

@socketio.on("connect")
def on_connect():
    print("🟢 Client connected")

@socketio.on("disconnect")
def on_disconnect():
    print("🔴 Client disconnected")

def build_prompt(user_input):
    return f"""
You are an AI classifier. Your job is to determine whether the user's purchase is **impulsive**.

ONLY respond with:
- "It is an impulsive purchase" → if the purchase is impulsive
- "It is not an impulsive purchase" → if the purchase is not impulsive

Do NOT explain. Do NOT add extra words. ONLY say "Yes" or "No".

Examples:
User: I saw a hoodie on Instagram and bought it immediately.
Assistant: Yes

User: I bought a fridge after comparing prices for a week.
Assistant: No

User: I grabbed a chocolate bar while waiting in line at the grocery store.
Assistant: Yes

Please use some intelliget reasoning to determine if the purchase is impulsive or not.
Apart from the given examples.

Now, evaluate:
User: {user_input}
Assistant:
"""


@socketio.on("user_message")
def handle_user_message(message):
    print("📩 User:", message)

    try:
        response = model.generate_content(
            build_prompt(message),
    generation_config={
        "temperature": 0,
        "max_output_tokens": 10,
        "stop_sequences": ["\n", "."]
    })
        bot_reply = response.text.strip()
        print("🤖 Gemini:", bot_reply)
        socketio.emit("bot_response", bot_reply)
    except Exception as e:
        print("❌ Gemini Error:", e)
        socketio.emit("bot_response", "Sorry, Gemini couldn't respond.") 

if __name__ == "__main__":
    socketio.run(app, host="127.0.0.1", port=5000, debug=True)
