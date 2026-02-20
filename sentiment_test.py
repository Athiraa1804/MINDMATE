from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

text = input("Enter a sentence: ")

score = analyzer.polarity_scores(text)

print(score)

if score['compound'] >= 0.05:
    print("Positive Mood 😊")
elif score['compound'] <= -0.05:
    print("Negative Mood 😔")
else:
    print("Neutral Mood 😐")
