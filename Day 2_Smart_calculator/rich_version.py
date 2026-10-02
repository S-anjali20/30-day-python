import math
import requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()

line60 = "=" * 60
def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


def multiply(a, b):
    return a * b


def divide(a, b):
    if b == 0:
        return None
    return a / b


def modulus(a, b):
    if b == 0:
        return None
    return a % b


def power(a, b):
    return a ** b

def square_root(number):
    if number < 0:
        return None

    return math.sqrt(number)


def percentage(percent, number):
    return (percent / 100) * number

# GET CURRENCY LIST FROM FRANKFURTER API
def get_currencies():

    url = "https://api.frankfurter.dev/v2/currencies"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            print("❌ Could not fetch currency list.")
            return None

        currencies = response.json()

        return currencies

    except requests.exceptions.RequestException:

        print("❌ Unable to connect to currency API.")
        print("Please check your internet connection.")

        return None

# DISPLAY CURRENCY MENU
def show_currency_menu(currencies):

    table = Table(
        title="💱 CURRENCY MENU",
        box=box.ROUNDED
    )

    table.add_column("No.", justify="right", style="cyan")
    table.add_column("Code", style="green")
    table.add_column("Currency", style="white")

    for index, currency in enumerate(currencies, start=1):

        code = currency["iso_code"]
        name = currency["name"]

        table.add_row(str(index), code, name)

    console.print(table)

# SELECT CURRENCY
def select_currency(currencies):

    while True:

        try:

            choice = int(input("Enter currency number: "))

            if 1 <= choice <= len(currencies):

                return currencies[choice - 1]["iso_code"]

            else:

                print(f"❌ Please enter a number "f"between 1 and {len(currencies)}.")

        except ValueError:

            print("❌ Please enter a valid number.")

# CURRENCY CONVERTER
def currency_converter():

    print("\n🌐 Fetching supported currencies...")

    currencies = get_currencies()

    if currencies is None:
        return

    print( "\nSelect the currency you are converting FROM:")

    show_currency_menu(currencies)

    from_currency = select_currency(currencies)

    print( "\nSelect the currency you are converting TO:")

    to_currency = select_currency(currencies)

    while True:

        try:

            amount = float(input(f"\nEnter amount in {from_currency}: "))

            if amount < 0:
                print("❌ Amount cannot be negative.")
                continue
            break

        except ValueError:

            print("❌ Please enter a valid amount.")


    if from_currency == to_currency:

        print("\n💡 Both currencies are the same.")

        print(f"{amount:.2f} {from_currency} "f"= {amount:.2f} {to_currency}")

        return

    # API REQUEST
    url = (
        f"https://api.frankfurter.dev/v2/rate/"
        f"{from_currency}/{to_currency}"
    )

    print("\n🌐 Fetching latest exchange rate...")

    try:

        response = requests.get(url,timeout=10)

        if response.status_code != 200:

            print("❌ Could not find the exchange rate for these currencies.")
            return

        data = response.json()

        rate = data["rate"]
        date = data["date"]

        converted_amount = amount * rate

        table = Table(
            title="💱 CONVERSION RESULT",
            box=box.ROUNDED
        )

        table.add_column("Details", style="cyan")
        table.add_column("Value", style="green")

        table.add_row(
            "From",
            f"{amount:.2f} {from_currency}"
        )

        table.add_row(
            "Exchange Rate",
            f"1 {from_currency} = "
            f"{rate:.4f} {to_currency}"
        )

        table.add_row(
            "Converted",
            f"{converted_amount:.2f} {to_currency}"
        )

        table.add_row(
            "Rate Date",
            date
        )

        console.print(table)

        print(line60)

    except requests.exceptions.RequestException:

        print("❌ Unable to connect to currency API.")

        print("Please check your internet connection.")

# MAIN CALCULATOR MENU
def show_menu():

    table = Table(title="🧮 SMART CALCULATOR",box=box.ROUNDED)

    table.add_column("No.", justify="center", style="cyan")
    table.add_column("Operation", style="green")
    table.add_column("Symbol", justify="center", style="yellow")

    table.add_row("1", "Addition", "+")
    table.add_row("2", "Subtraction", "-")
    table.add_row("3", "Multiplication", "*")
    table.add_row("4", "Division", "/")
    table.add_row("5", "Modulus", "%")
    table.add_row("6", "Power", "**")
    table.add_row("7", "Square Root", "√")
    table.add_row("8", "Percentage", "%")
    table.add_row("9", "Currency Converter", "💱")
    table.add_row("10", "Exit", "🚪")

    console.print(table)


    print(line60)


def main():

    print("\n" + line60)
    print("         🧮 WELCOME TO SMART CALCULATOR")
    print(line60)

    while True:

        show_menu()
        try:

            choice = int(input("Enter your choice (1-10): "))

        except ValueError:

            print("❌ Please enter a valid number.")
            continue


        if choice == 10:

            print("\n" + line60)
            print("Thank you for using Smart Calculator! 👋")
            print(line60)
            break


        elif choice == 7:

            try:

                number = float(input("Enter a number: "))

            except ValueError:

                print("❌ Please enter a valid number.")

                continue

            result = square_root(number)

            if result is None:

                print("❌ Square root of a negative number is not possible.")

            else:

                print(f"\n√{number} = {result}")


        elif choice == 8:

            try:

                percent = float(input("Enter percentage: "))

                number = float(input("Enter the number: "))

            except ValueError:

                print("❌ Please enter valid numbers.")

                continue

            result = percentage(percent,number)

            print(f"\n{percent}% of {number} = {result}")

        elif choice == 9:
            currency_converter()

        elif 1 <= choice <= 6:
            try:
                num1 = float(input("Enter first number: "))

                num2 = float(input("Enter second number: "))

            except ValueError:

                print("❌ Please enter valid numbers.")
                continue

            if choice == 1:
                result = add(num1, num2)
                operator = "+"

            elif choice == 2:
                result = subtract(num1, num2)
                operator = "-"

            elif choice == 3:
                result = multiply(num1, num2)
                operator = "*"

            elif choice == 4:
                result = divide(num1, num2)
                operator = "/"
                if result is None:
                    print("❌ Cannot divide by zero.")
                    continue

            elif choice == 5:
                result = modulus(num1, num2)
                operator = "%"
                if result is None:
                    print("❌ Cannot perform ""modulus by zero.")
                    continue

            elif choice == 6:
                result = power(num1, num2)
                operator = "**"

            print(f"\n{num1} {operator} {num2} = {result}")

        else:

            print("❌ Please choose a number between 1 and 10.")

if __name__ == "__main__":
    main()