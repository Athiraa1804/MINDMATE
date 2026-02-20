from transformers import pipeline

print("Loading transformer emotion model... Please wait.")

emotion_classifier = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    device=-1
)

def detect_emotion(text):
    result = emotion_classifier(text)[0]
    return result["label"]