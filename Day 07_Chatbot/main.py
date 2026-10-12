import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("❌ API key not found.")
    print("Please add OPENAI_API_KEY to your .env file.")
    exit()

client = OpenAI(api_key=api_key)

MODEL = "gpt-6-luna"


def show_welcome():

    print("\n" + "=" * 60)
    print("              🤖 AI CHATBOT — VERSION 2")
    print("=" * 60)

    print("\n💬 Chat with the AI!")
    print("Type 'clear' to start a new conversation.")
    print("Type 'exit' to quit.")

    print("-" * 60)


def chatbot():

    show_welcome()

    conversation = []

    while True:

        user_input = input("\n👤 You: ").strip()

        if not user_input:
            print("❌ Please enter something.")
            continue

        if user_input.lower() == "exit":

            print("\n🤖 Goodbye! 👋")
            break

        if user_input.lower() == "clear":

            conversation = []

            print("\n🗑️ Conversation memory cleared!")
            print("You can start a new conversation.")

            continue

        conversation.append({
            "role": "user",
            "content": user_input
        })

        try:

            response = client.responses.create(
                model=MODEL,
                input=conversation
            )

            ai_response = response.output_text

            print(f"\n🤖 AI: {ai_response}")

            conversation.append({
                "role": "assistant",
                "content": ai_response
            })

        except Exception as e:

            print("\n❌ Something went wrong.")
            print(f"Error: {e}")

            conversation.pop()


if __name__ == "__main__":
    chatbot()