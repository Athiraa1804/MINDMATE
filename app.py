from flask import Flask, render_template, request, jsonify, session
import random
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "mindmate_secret_key"  # REQUIRED for session

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

    intensity_words = [
        "very", "extremely", "so", "really",
        "terribly", "too much", "overwhelming", "completely"
    ]

    intensity = any(word in text for word in intensity_words)

    if any(word in text for word in ["sad", "lonely", "depressed", "upset"]):
        return "sadness_high" if intensity else "sadness"

    elif any(word in text for word in ["happy", "great", "excited", "good", "better"]):
        return "joy_high" if intensity else "joy"

    elif any(word in text for word in ["angry", "frustrated", "annoyed"]):
        return "anger_high" if intensity else "anger"

    elif any(word in text for word in ["scared", "afraid", "tensed", "stressed", "pressure", "anxious", "worried"]):
        return "fear_high" if intensity else "fear"

    else:
        return "neutral"


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
        "That’s really nice to hear 😊",
        "I’m glad something positive is happening for you.",
        "That sounds uplifting!"
    ],
    "sadness": [
        "I’m really sorry you’re feeling this way.",
        "That must feel heavy for you.",
        "It’s okay to feel low sometimes."
    ],
    "anger": [
        "It sounds like something really frustrated you.",
        "That kind of situation can feel overwhelming.",
        "I can sense your frustration."
    ],
    "fear": [
        "It sounds like you’re feeling tense.",
        "That must be stressful for you.",
        "Anxiety can feel exhausting."
    ],
    "neutral": [
        "I’m here with you.",
        "Tell me more about what’s on your mind.",
        "Let’s talk through it."
    ]
}
responses.update({
    "fear_high": [
        "That sounds overwhelming. Let's take this step by step.",
        "It seems this stress is really intense right now."
    ],
    "sadness_high": [
        "That sounds deeply painful. I'm really here for you.",
        "It feels like this is weighing heavily on you."
    ],
    "anger_high": [
        "That must have been extremely frustrating.",
        "It sounds like this really hit you hard."
    ],
    "joy_high": [
        "That’s amazing! I can feel your excitement!",
        "Wow, that sounds incredibly uplifting!"
    ]
})

follow_ups = {
        "fear_high": [
        "Would you like to talk about what’s causing this stress?",
        "What’s making it feel so overwhelming?"
    ],
    "sadness_high": [
        "Do you want to share what happened?",
        "How long has this been building up?"
    ],
    "anger_high": [
        "What triggered this reaction?",
        "Do you want to explain what happened?"
    ],
    "joy_high": [
        "What made this so exciting?",
        "Tell me more about this good news!"
    ]
}

relaxation_tips = {
    "joy": "Keep doing what makes you happy!",
    "sadness": "Try journaling your thoughts.",
    "anger": "Take deep breaths and count to 10.",
    "fear": "Try grounding techniques like 5-4-3-2-1.",
    "neutral": "Take a small pause and breathe slowly."
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

    # ---------------- CRISIS DETECTION ----------------
    if any(word in user_input.lower() for word in crisis_words):
        return jsonify({
            "reply": "I'm really concerned about you. Please contact Kiran Mental Health Helpline: 1800-599-0019 💙"
        })

    # ---------------- STORE CONVERSATION HISTORY ----------------
    # Store conversation history safely
    history = session.get("history", [])

    if isinstance(history, list):
        history.append(user_input)
    else:
        history = [user_input]
    # Keep only last 5 messages
    history = history[-5:]
    session["history"] = history

    # ---------------- EMOTION DETECTION ----------------
    emotion = detect_emotion(user_input)

    if emotion not in responses:
        emotion = "neutral"

    # ---------------- SESSION MEMORY ----------------
    last_emotion = session.get("last_emotion")
    last_reply = session.get("last_reply")

    # ---------------- RESPONSE SELECTION ----------------
    # ---------------- RESPONSE SELECTION ----------------
    base_options = responses.get(emotion, responses["neutral"])
    follow_options = follow_ups.get(emotion, ["Tell me more."])

# Avoid repeating same reply
    filtered_options = [r for r in base_options if r != last_reply]
    if not filtered_options:
       filtered_options = base_options

    selected_base = random.choice(filtered_options)
    selected_follow = random.choice(follow_options)

    # Avoid repeating same reply
    filtered_options = [r for r in base_options if r != last_reply]
    if not filtered_options:
        filtered_options = base_options

    selected_base = random.choice(filtered_options)
    selected_follow = random.choice(follow_options)

    # ---------------- CONTEXT AWARENESS ----------------
    if len(history) > 1:
        previous_message = history[-2]
        if "exam" in previous_message.lower():
            selected_base += " I remember you mentioned exams earlier."

    # ---------------- CONTEXT CONTINUITY ----------------
    if last_emotion == emotion:
        reply = f"I can sense you're still feeling {emotion}. {selected_base} {selected_follow}"
    else:
        reply = f"{selected_base} {selected_follow}"

    # ---------------- PERSONALIZATION ----------------
    if username:
        reply = f"{username}, {reply}"

    # Save memory
    session["last_emotion"] = emotion
    session["last_reply"] = selected_base

    # ---------------- RELAXATION TIP ----------------
    tip = relaxation_tips.get(emotion, "")

    # ---------------- SAVE TO DATABASE ----------------
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

    # Total chats
    cursor.execute("SELECT COUNT(*) FROM chats")
    total_chats = cursor.fetchone()[0]

    # Emotion counts
    cursor.execute("SELECT emotion, COUNT(*) FROM chats GROUP BY emotion")
    emotion_counts = cursor.fetchall()

    # Calculate most frequent emotion
    most_common = max(emotion_counts, key=lambda x: x[1])[0] if emotion_counts else "None"

    conn.close()

    return render_template("dashboard.html",
                           total_chats=total_chats,
                           emotion_counts=emotion_counts,
                           most_common=most_common)
# -------------------------
# RUN APP
# -------------------------
init_db()

if __name__ == "__main__":
    app.run(debug=True)