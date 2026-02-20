from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import random

analyzer = SentimentIntensityAnalyzer()

# Emotion keyword detection
emotion_keywords = {
    "stress": ["stressed", "pressure", "overwhelmed", "exams"],
    "anxiety": ["anxious", "nervous", "worried", "scared"],
    "sadness": ["sad", "lonely", "depressed", "unhappy"],
    "anger": ["angry", "frustrated", "annoyed"],
    "happy": ["happy", "excited", "good", "great"]
}

# Empathetic responses
responses = {
    "stress": [
        "It sounds like you're under a lot of pressure. Let's slow down together 💙",
        "Stress can feel heavy. You are stronger than you think."
    ],
    "anxiety": [
        "Take a deep breath with me. You are safe right now.",
        "It's okay to feel anxious. Let's handle it step by step."
    ],
    "sadness": [
        "I'm really sorry you're feeling this way.",
        "You are not alone. I'm here to listen."
    ],
    "anger": [
        "It's okay to feel angry. Let's try to understand what's bothering you.",
        "Take a moment to breathe before reacting."
    ],
    "happy": [
        "That’s wonderful to hear! 😊",
        "I'm so glad you're feeling good!"
    ],
    "neutral": [
        "I understand. Tell me more.",
        "I'm here to listen."
    ]
}

# Relaxation tips
relaxation_tips = {
    "stress": "Try the 4-7-8 breathing technique.",
    "anxiety": "Use the 5-4-3-2-1 grounding method.",
    "sadness": "Write down three small things you're grateful for.",
    "anger": "Take a short walk and breathe deeply.",
    "happy": "Keep doing what makes you feel good!",
    "neutral": "Drink some water and take a short stretch break."
}

def detect_emotion(text):
    text = text.lower()
    for emotion, keywords in emotion_keywords.items():
        for word in keywords:
            if word in text:
                return emotion
    return "neutral"

print("MindMate AI 💙 (type 'exit' to stop)")
crisis_words = ["suicide", "kill myself", "die", "end my life", "can't live"]
while True:
    user_input = input("You: ")

    if user_input.lower() == "exit":
        print("MindMate: Take care of yourself 💙")
        break
    if any(word in user_input.lower() for word in crisis_words):
      print("MindMate: I'm really concerned about you. 💙")
      print("Please consider talking to someone you trust immediately.")
      print("You can contact Kiran Mental Health Helpline: 1800-599-0019 (India)")
      print()
      continue

    emotion = detect_emotion(user_input)

    reply = random.choice(responses[emotion])
    tip = relaxation_tips[emotion]

    print("MindMate:", reply)
    print("Tip:", tip)
    print()
