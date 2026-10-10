import os
import typer
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

app = typer.Typer(
    help="📚 AI Study Assistant - Learn smarter with AI!"
)

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    typer.echo("❌ API key not found.")
    typer.echo("Please add OPENAI_API_KEY to your .env file.")
    raise typer.Exit()

client = OpenAI(api_key=api_key)

MODEL = "gpt-6-luna"


def get_ai_response(prompt):

    try:

        with typer.progressbar(
            length=1,
            label="🤖 Generating response"
        ) as progress:

            response = client.responses.create(
                model=MODEL,
                input=prompt
            )

            progress.update(1)

        return response.output_text

    except Exception as e:

        typer.echo("\n❌ Something went wrong.")
        typer.echo(f"Error: {e}")

        return None


@app.command()
def explain(
    topic: str = typer.Argument(
        ...,
        help="The topic you want to learn."
    )
):

    """
    📖 Explain a topic using AI.
    """

    typer.echo("\n" + "=" * 60)
    typer.echo("                 📖 EXPLAIN TOPIC")
    typer.echo("=" * 60)

    prompt = f"""
You are a helpful AI study assistant.

Explain the following topic in simple language
for a college student.

Topic: {topic}

Include:

1. Simple definition
2. Detailed explanation
3. Important points
4. A simple real-world example
5. Short summary

Use clear headings and bullet points.
"""

    response = get_ai_response(prompt)

    if response:

        typer.echo("\n" + "-" * 60)
        typer.echo(response)
        typer.echo("-" * 60)


@app.command()
def notes(
    topic: str = typer.Argument(
        ...,
        help="The topic for which you want notes."
    )
):

    """
    📝 Generate exam-friendly notes.
    """

    typer.echo("\n" + "=" * 60)
    typer.echo("                  📝 GENERATE NOTES")
    typer.echo("=" * 60)

    prompt = f"""
You are an AI study assistant helping a college student
prepare for exams.

Create concise and exam-friendly notes about:

{topic}

Include:

• Definition
• Important concepts
• Key points
• Examples
• Advantages and disadvantages if applicable
• Important terms
• Short revision summary

Use headings, bullet points and simple language.
"""

    response = get_ai_response(prompt)

    if response:

        typer.echo("\n" + "-" * 60)
        typer.echo(response)
        typer.echo("-" * 60)


@app.command()
def quiz(
    topic: str = typer.Argument(
        ...,
        help="The topic for the quiz."
    )
):

    """
    ❓ Generate a quiz using AI.
    """

    typer.echo("\n" + "=" * 60)
    typer.echo("                    ❓ QUIZ")
    typer.echo("=" * 60)

    prompt = f"""
You are an AI quiz generator.

Create 5 multiple-choice questions about:

{topic}

For each question provide:

1. The question
2. Four options labeled A, B, C and D
3. The correct answer
4. A short explanation of the answer

Make the questions suitable for a college student.

Do not make all correct answers the same option.
"""

    response = get_ai_response(prompt)

    if response:

        typer.echo("\n" + "-" * 60)
        typer.echo(response)
        typer.echo("-" * 60)


@app.command()
def study():
    """
    📚 Start the interactive AI Study Assistant.
    """

    os.system("clear")

    typer.echo("\n" + "=" * 60)
    typer.echo("          📚 AI STUDY ASSISTANT")
    typer.echo("=" * 60)

    typer.echo("\n🤖 Learn smarter with AI!")
    typer.echo("📖 Explain topics | 📝 Generate notes | ❓ Take quizzes")

    while True:

        typer.echo("\n" + "-" * 60)

        typer.echo("\nChoose an option:\n")

        typer.echo("1. 📖 Explain a Topic")
        typer.echo("2. 📝 Generate Notes")
        typer.echo("3. ❓ Generate Quiz")
        typer.echo("4. 🚪 Exit")

        choice = typer.prompt(
            "\nEnter your choice",
            type=int
        )

        if choice == 1:

            topic = typer.prompt(
                "\n📖 Enter the topic"
            )

            explain(topic)

        elif choice == 2:

            topic = typer.prompt(
                "\n📝 Enter the topic"
            )

            notes(topic)

        elif choice == 3:

            topic = typer.prompt(
                "\n❓ Enter the topic"
            )

            quiz(topic)

        elif choice == 4:

            typer.echo("\n" + "=" * 60)
            typer.echo(
                "      Thank you for using AI Study Assistant! 👋"
            )
            typer.echo("=" * 60)

            break

        else:

            typer.echo(
                "\n❌ Please choose a number between 1 and 4."
            )


if __name__ == "__main__":
    study()