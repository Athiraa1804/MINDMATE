from flask import Flask, render_template, request, jsonify
import random
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

# -------------------------------------------------
# MODE CONFIGURATION (LOCAL = AI, DEPLOY = LIGHT)
# -------------------------------------------------
USE_TRANSFORMER = os.getenv("USE_TRANSFORMER", "False") == "True"

if USE_TRANSFORMER:
    from emotion_model import detect_emotion
else:
    # Lightweight rule-based fallback
    def detect_emotion(text):
        text = text.lower()
        if any(word in text for word in ["sad", "lonely", "depressed"]):
            return "sadness"
        elif any(word in text for word in ["happy", "great", "excited"]):
            return "joy"
        elif any(word in text for word in ["angry", "frustrated"]):
            return "anger"
        elif any(word in text for word in ["scared", "afraid"]):
            return "fear"
        else:
            return "joy"


# -------------------------
# DATABASE INITIALIZATION
# -------------------------
def init_db():
    conn = sqlite3.connect("mindmate.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            message TEXT,
            emotion TEXT,
            timestamp TEXT
        )
    """)

    conn.commit()
    conn.close()


# -------------------------
# RESPONSE DICTIONARY
# -------------------------
responses = {
    "joy": [
        "That’s wonderful to hear! 😊",
        "I'm so glad you're feeling joyful!"
    ],
    "sadness": [
        "I'm really sorry you're feeling this way.",
        "You are not alone. I'm here for you."
    ],
    "anger": [
        "It's okay to feel angry. Let's breathe together.",
        "Take a moment before reacting."
    ],
    "fear": [
        "It’s okay to feel afraid. You’re safe right now.",
        "Let’s slow things down together."
    ],
    "love": [
        "That’s beautiful 💙",
        "It’s nice to feel love and connection."
    ],
    "surprise": [
        "That sounds unexpected!",
        "Life can surprise us sometimes!"
    ]
}

relaxation_tips = {
    "joy": "Keep doing what makes you happy!",
    "sadness": "Try journaling your thoughts.",
    "anger": "Take deep breaths and count to 10.",
    "fear": "Try grounding techniques like 5-4-3-2-1.",
    "love": "Share your positive feelings with someone.",
    "surprise": "Take a moment to process what happened."
}

crisis_words = ["suicide", "kill myself", "die", "end my life", "can't live"]


# -------------------------
# ROUTES
# -------------------------

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json["message"]
    username = request.json.get("username", "Guest")

    # Crisis detection
    if any(word in user_input.lower() for word in crisis_words):
        return jsonify({
            "reply": "I'm really concerned about you. Please contact Kiran Mental Health Helpline: 1800-599-0019 💙"
        })

    emotion = detect_emotion(user_input)

    if emotion not in responses:
        emotion = "joy"

    reply = random.choice(responses[emotion])
    tip = relaxation_tips.get(emotion, "")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect("mindmate.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO chats (username, message, emotion, timestamp)
        VALUES (?, ?, ?, ?)
    """, (username, user_input, emotion, timestamp))

    conn.commit()
    conn.close()

    return jsonify({
        "reply": reply,
        "tip": tip
    })


@app.route("/dashboard")
def dashboard():
    conn = sqlite3.connect("mindmate.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM chats")
    total_chats = cursor.fetchone()[0]

    cursor.execute("SELECT emotion, COUNT(*) FROM chats GROUP BY emotion")
    emotion_counts = cursor.fetchall()

    conn.close()

    return render_template("dashboard.html",
                           total_chats=total_chats,
                           emotion_counts=emotion_counts)


# -------------------------
# RUN APP
# -------------------------
init_db()

if __name__ == "__main__":
    app.run()