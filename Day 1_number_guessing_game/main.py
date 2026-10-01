import random


# -------------------------------
# Choose Difficulty
# -------------------------------
def choose_difficulty():
    while True:
        print("\nChoose your difficulty level:")
        print("1. Easy   (1-100, 10 attempts)")
        print("2. Medium (1-200, 8 attempts)")
        print("3. Hard   (1-500, 6 attempts)")

        try:
            difficulty = int(input("Enter your choice (1-3): "))

            if difficulty == 1:
                return 100, 10, 1

            elif difficulty == 2:
                return 200, 8, 1.5

            elif difficulty == 3:
                return 500, 6, 2

            else:
                print("❌ Please enter 1, 2, or 3.")

        except ValueError:
            print("❌ Please enter a valid number.")


# -------------------------------
# Calculate Score
# -------------------------------
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


# -------------------------------
# Play One Game
# -------------------------------
def play_game():
    max_number, max_attempts, multiplier = choose_difficulty()

    secret_number = random.randint(1, max_number)
    attempts = 0

    print(f"\n🎯 I have chosen a number between 1 and {max_number}.")
    print(f"You have {max_attempts} attempts to guess it!\n")

    while attempts < max_attempts:

        try:
            guess = int(input("Enter your guess: "))

        except ValueError:
            print("❌ Please enter a valid number.")
            continue

        if guess < 1 or guess > max_number:
            print(f"❌ Please enter a number between 1 and {max_number}.")
            continue

        attempts += 1

        difference = abs(secret_number - guess)

        # Correct guess
        if difference == 0:
            print("\n🎉 Correct! You guessed it!")
            print(f"🔢 The number was {secret_number}.")
            print(f"📊 It took you {attempts} guesses.")

            base_score = calculate_score(attempts)
            final_score = int(base_score * multiplier)

            print(f"🏆 Round Score: {final_score}")

            return final_score, True

        # Hot / Cold feedback
        if difference <= 5:
            print("🔥 You are very close!")

        elif difference <= 15:
            print("🙂 You are close!")

        elif difference <= 30:
            print("😐 You are getting warmer!")

        else:
            print("🥶 You are too far!")

        # Higher / Lower hint
        if guess < secret_number:
            print("⬆️ Hint: Try a higher number.")
        else:
            print("⬇️ Hint: Try a lower number.")

        remaining = max_attempts - attempts
        print(f"❤️ Attempts remaining: {remaining}\n")

    # If attempts are finished
    print("\n💔 Game Over!")
    print(f"🔢 The secret number was: {secret_number}")

    return 0, False


# -------------------------------
# Main Game
# -------------------------------
def main():

    print("=" * 40)
    print("      🎯 NUMBER GUESSING GAME")
    print("=" * 40)

    total_score = 0
    games_played = 0
    games_won = 0

    while True:

        score, won = play_game()

        total_score += score
        games_played += 1

        if won:
            games_won += 1

        print("\n" + "-" * 40)
        print(f"🏆 Total Score: {total_score}")
        print(f"🎮 Games Played: {games_played}")
        print(f"🥇 Games Won: {games_won}")
        print("-" * 40)

        while True:
            answer = input("\nDo you want to play again? (yes/no): ").lower()

            if answer == "yes":
                break

            elif answer == "no":
                print("\n" + "=" * 40)
                print("           📊 FINAL RESULTS")
                print("=" * 40)
                print(f"🎮 Games Played : {games_played}")
                print(f"🥇 Games Won    : {games_won}")
                print(f"🏆 Final Score  : {total_score}")
                print("\nThanks for playing! Goodbye! 👋")
                print("=" * 40)
                return

            else:
                print("❌ Please enter 'yes' or 'no'.")


# Start the game
main()