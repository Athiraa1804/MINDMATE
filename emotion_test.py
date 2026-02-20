from transformers import pipeline

print("Loading emotion model... (first time may take 1-2 minutes)")

emotion_classifier = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    device=-1  # CPU mode
)

while True:
    text = input("You: ")

    if text.lower() == "exit":
        print("Chatbot: Take care! 💙")
        break

    result = emotion_classifier(text)[0]
    emotion = result['label']
    confidence = result['score']

    print(f"Detected Emotion: {emotion} (Confidence: {confidence:.2f})")