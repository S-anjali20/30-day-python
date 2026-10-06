from transformers import pipeline

LINE = "=" * 60


def load_model():

    print("\n🤖 Loading AI sentiment model...")
    print("Please wait...\n")

    try:

        sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model="cardiffnlp/twitter-roberta-base-sentiment-latest"
        )

        print("✅ AI model loaded successfully!")

        return sentiment_analyzer

    except Exception as e:

        print("❌ Could not load the AI model.")
        print(f"Error: {e}")

        return None


def show_criteria():

    print("\n" + LINE)
    print("             🤖 AI SENTIMENT ANALYZER")
    print(LINE)

    print("\n📋 SENTIMENT CATEGORIES")
    print("-" * 60)

    print("😊 POSITIVE  → Happy, satisfied or favorable")
    print("😐 NEUTRAL   → Neither positive nor negative")
    print("😞 NEGATIVE  → Unhappy, dissatisfied or unfavorable")

    print("-" * 60)

    print("\n🧠 This application uses a pre-trained")
    print("   Natural Language Processing (NLP) model.")

    print(LINE)


def analyze_sentiment(model, text):

    try:

        result = model(text)[0]

        label = result["label"].upper()
        score = result["score"]

        if "POSITIVE" in label:

            emoji = "😊"
            sentiment = "POSITIVE"

        elif "NEGATIVE" in label:

            emoji = "😞"
            sentiment = "NEGATIVE"

        else:

            emoji = "😐"
            sentiment = "NEUTRAL"

        print("\n" + LINE)
        print("                  📊 RESULT")
        print(LINE)

        print(f"\n{emoji} Sentiment  : {sentiment}")
        print(f"📈 Confidence : {score * 100:.2f}%")

        print(LINE)

    except Exception as e:

        print("\n❌ Unable to analyze the text.")
        print(f"Error: {e}")


def main():

    show_criteria()

    model = load_model()

    if model is None:
        return

    while True:

        print("\n" + LINE)

        text = input(
            "📝 Enter your text: "
        ).strip()

        if not text:

            print("\n❌ Please enter some text.")
            continue

        print("\n🤖 Analyzing your text...")

        analyze_sentiment(
            model,
            text
        )

        print("\nWould you like to analyze another text?")

        choice = input(
            "Enter yes/no: "
        ).strip().lower()

        if choice != "yes":

            print("\n" + LINE)
            print("Thank you for using AI Sentiment Analyzer! 👋")
            print(LINE)

            break


if __name__ == "__main__":
    main()
    