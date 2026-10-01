import random
from colorama import Fore, Style, init

# Initialize Colorama
init(autoreset=True)


# --------------------------------
# Choose Difficulty
# --------------------------------
def choose_difficulty():

    while True:
        print(Fore.CYAN + "\nChoose your difficulty level:")
        print(Fore.GREEN + "1. Easy   → 1-100  | 10 attempts")
        print(Fore.YELLOW + "2. Medium → 1-200  | 8 attempts")
        print(Fore.RED + "3. Hard   → 1-500  | 6 attempts")

        try:
            difficulty = int(input("Enter your choice (1-3): "))

            if difficulty == 1:
                return 100, 10, 1

            elif difficulty == 2:
                return 200, 8, 1.5

            elif difficulty == 3:
                return 500, 6, 2

            else:
                print(Fore.RED + "❌ Please enter 1, 2, or 3.")

        except ValueError:
            print(Fore.RED + "❌ Please enter a valid number.")


# --------------------------------
# Calculate Score
# --------------------------------
def calculate_score(attempts):

    if attempts == 1:
        return 100

    elif attempts <= 2:
        return 80

    elif attempts <= 4:
        return 60

    elif attempts <= 6:
        return 40

    elif attempts <= 8:
        return 20

    else:
        return 10


# --------------------------------
# Play One Game
# --------------------------------
def play_game():

    max_number, max_attempts, multiplier = choose_difficulty()

    secret_number = random.randint(1, max_number)
    attempts = 0

    print(Fore.CYAN + "\n" + "=" * 45)
    print(Fore.CYAN + f"🎯 Guess a number between 1 and {max_number}")
    print(Fore.CYAN + f"❤️ You have {max_attempts} attempts!")
    print(Fore.CYAN + "=" * 45)

    while attempts < max_attempts:

        try:
            guess = int(input(Fore.WHITE + "\nEnter your guess: "))

        except ValueError:
            print(Fore.RED + "❌ Please enter a valid number.")
            continue

        # Check range
        if guess < 1 or guess > max_number:
            print(
                Fore.RED
                + f"❌ Please enter a number between 1 and {max_number}."
            )
            continue

        attempts += 1

        difference = abs(secret_number - guess)

        # --------------------------------
        # Correct Guess
        # --------------------------------
        if difference == 0:

            print(Fore.GREEN + "\n🎉 Correct! You guessed it!")
            print(
                Fore.GREEN
                + f"🔢 The secret number was {secret_number}."
            )

            print(
                Fore.CYAN
                + f"📊 It took you {attempts} guesses."
            )

            base_score = calculate_score(attempts)

            final_score = int(base_score * multiplier)

            print(
                Fore.GREEN
                + f"🏆 Round Score: {final_score}"
            )

            return final_score, True

        # --------------------------------
        # Hot / Cold Feedback
        # --------------------------------
        if difference <= 5:

            print(
                Fore.MAGENTA
                + "🔥 You are VERY close!"
            )

        elif difference <= 15:

            print(
                Fore.YELLOW
                + "🙂 You are close!"
            )

        elif difference <= 30:

            print(
                Fore.LIGHTYELLOW_EX
                + "😐 You are getting warmer!"
            )

        else:

            print(
                Fore.RED
                + "🥶 You are too far!"
            )

        # --------------------------------
        # Higher / Lower Hint
        # --------------------------------
        if guess < secret_number:

            print(
                Fore.CYAN
                + "⬆️ Hint: Try a higher number."
            )

        else:

            print(
                Fore.CYAN
                + "⬇️ Hint: Try a lower number."
            )

        remaining = max_attempts - attempts

        print(
            Fore.WHITE
            + f"❤️ Attempts remaining: {remaining}"
        )

    # --------------------------------
    # Game Over
    # --------------------------------

    print(Fore.RED + "\n💔 Game Over!")
    print(
        Fore.YELLOW
        + f"🔢 The secret number was: {secret_number}"
    )

    return 0, False


# --------------------------------
# Main Game
# --------------------------------
def main():

    print(Fore.CYAN + "\n" + "=" * 45)
    print(Fore.CYAN + "       🎯 NUMBER GUESSING GAME")
    print(Fore.CYAN + "=" * 45)

    total_score = 0
    games_played = 0
    games_won = 0

    while True:

        score, won = play_game()

        total_score += score
        games_played += 1

        if won:
            games_won += 1

        # --------------------------------
        # Current Statistics
        # --------------------------------

        print(Fore.CYAN + "\n" + "-" * 45)
        print(Fore.GREEN + f"🏆 Total Score : {total_score}")
        print(Fore.CYAN + f"🎮 Games Played: {games_played}")
        print(Fore.GREEN + f"🥇 Games Won   : {games_won}")
        print(Fore.CYAN + "-" * 45)

        # --------------------------------
        # Play Again
        # --------------------------------

        while True:

            answer = input(
                Fore.WHITE
                + "\nDo you want to play again? (yes/no): "
            ).lower().strip()

            if answer == "yes":

                break

            elif answer == "no":

                print(Fore.CYAN + "\n" + "=" * 45)
                print(Fore.CYAN + "           📊 FINAL RESULTS")
                print(Fore.CYAN + "=" * 45)

                print(
                    Fore.WHITE
                    + f"🎮 Games Played : {games_played}"
                )

                print(
                    Fore.GREEN
                    + f"🥇 Games Won    : {games_won}"
                )

                print(
                    Fore.YELLOW
                    + f"🏆 Final Score  : {total_score}"
                )

                print(Fore.CYAN + "\nThanks for playing! Goodbye! 👋")
                print(Fore.CYAN + "=" * 45)

                return

            else:

                print(
                    Fore.RED
                    + "❌ Please enter 'yes' or 'no'."
                )


# --------------------------------
# Start Game
# --------------------------------
if __name__ == "__main__":
    main()