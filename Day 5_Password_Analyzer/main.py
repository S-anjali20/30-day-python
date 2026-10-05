import re

def show_criteria():

    print("\n" + "=" * 55)
    print("             🔐 PASSWORD STRENGTH CRITERIA")
    print("=" * 55)

    print("✓ At least 8 characters")
    print("✓ At least 12 characters for extra strength")
    print("✓ At least one uppercase letter (A-Z)")
    print("✓ At least one lowercase letter (a-z)")
    print("✓ At least one number (0-9)")
    print("✓ At least one special character")
    print("✓ Avoid commonly used passwords")

    print("=" * 55)


def check_length(password):
    return len(password) >= 8


def has_uppercase(password):
    return bool(re.search(r"[A-Z]", password))


def has_lowercase(password):
    return bool(re.search(r"[a-z]", password))


def has_number(password):
    return bool(re.search(r"[0-9]", password))


def has_special_character(password):
    return bool(re.search(r"[^A-Za-z0-9]", password))



def calculate_score(password):

    score = 0

    if check_length(password):
        score += 1

    if len(password) >= 12:
        score += 1

    if has_uppercase(password):
        score += 1

    if has_lowercase(password):
        score += 1

    if has_number(password):
        score += 1

    if has_special_character(password):
        score += 1

    return score


def get_strength(score):

    if score <= 2:
        return "🔴 Very Weak"

    elif score == 3:
        return "🟠 Weak"

    elif score == 4:
        return "🟡 Medium"

    elif score == 5:
        return "🟢 Strong"

    else:
        return "💪 Very Strong"


def show_analysis(password):

    print("\n" + "=" * 55)
    print("                 📊 PASSWORD ANALYSIS")
    print("=" * 55)

    if not password:
        print("❌ Password cannot be empty.")
        return


    print("\nPASSWORD CRITERIA")
    print("-" * 55)

    if check_length(password):
        print("✅ Length: At least 8 characters")
    else:
        print("❌ Length: Less than 8 characters")

    if len(password) >= 12:
        print("✅ Length: At least 12 characters")
    else:
        print("❌ Length: Less than 12 characters")

    if has_uppercase(password):
        print("✅ Contains uppercase letter")
    else:
        print("❌ Missing uppercase letter")

    if has_lowercase(password):
        print("✅ Contains lowercase letter")
    else:
        print("❌ Missing lowercase letter")

    if has_number(password):
        print("✅ Contains number")
    else:
        print("❌ Missing number")

    if has_special_character(password):
        print("✅ Contains special character")
    else:
        print("❌ Missing special character")

    score = calculate_score(password)
    strength = get_strength(score)

    print("\n" + "-" * 55)

    print(f"📈 Score: {score}/6")
    print(f"🔐 Strength: {strength}")

    print("-" * 55)

    suggestions = []

    if len(password) < 8:
        suggestions.append(
            "Use at least 8 characters."
        )

    if len(password) < 12:
        suggestions.append(
            "For better security, use at least 12 characters."
        )

    if not has_uppercase(password):
        suggestions.append(
            "Add at least one uppercase letter."
        )

    if not has_lowercase(password):
        suggestions.append(
            "Add at least one lowercase letter."
        )

    if not has_number(password):
        suggestions.append(
            "Add at least one number."
        )

    if not has_special_character(password):
        suggestions.append(
            "Add at least one special character."
        )


    if suggestions:

        print("\n💡 SUGGESTIONS")

        for suggestion in suggestions:
            print(f"• {suggestion}")

    else:

        print("\n🎉 Excellent! Your password meets all checks.")

    print("=" * 55)


def main():

    print("\n" + "=" * 55)
    print("          🔐 WELCOME TO PASSWORD ANALYZER")
    print("=" * 55)

    show_criteria()

    while True:

        password = input(
            "\nEnter your password: "
        )

        show_analysis(password)

        choice = input(
            "\nDo you want to analyze another password? (yes/no): "
        )

        if choice.lower() != "yes":

            print("\n🔒 Thank you for using Password Analyzer!")
            print("Goodbye! 👋")
            break


if __name__ == "__main__":
    main()