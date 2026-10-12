# 🎯 Number Guessing Game

A beginner-friendly Python console game where the player tries to guess a randomly generated number. The game includes multiple difficulty levels, limited attempts, dynamic hints, scoring, game statistics, and colored terminal output using `colorama`.

This project is **Day 1** of my **30 Days, 30 Python Projects** challenge.

---

## 🚀 Features

- 🎲 **Random number generation**
- 🎚️ **Three difficulty levels**
- ❤️ **Limited attempts** based on difficulty
- 🔥 **Hot/cold distance-based hints**
- ⬆️ **Higher/lower directional hints**
- 🏆 **Score calculation system**
- 📊 **Game statistics tracking**
- 🔄 **Play-again functionality**
- 🛡️ **Input validation** with safe exception handling
- 🎨 **Colored terminal interface** using `colorama`

---

## 🎚️ Difficulty Levels

| Level | Number Range | Attempts | Multiplier |
| :--- | :---: | :---: | :---: |
| 🟢 **Easy** | 1 – 100 | 10 | 1.0x |
| 🟡 **Medium** | 1 – 200 | 8 | 1.5x |
| 🔴 **Hard** | 1 – 500 | 6 | 2.0x |

---

## 🔥 Hint System

The game provides feedback based on how close your guess is to the secret number:

| Difference | Feedback |
| :---: | :--- |
| **0** | 🎉 Correct! |
| **1 – 5** | 🔥 Very close |
| **6 – 15** | 🙂 Close |
| **16 – 30** | 😐 Getting warmer |
| **31+** | 🥶 Too far |

*The game also informs the player whether to guess **higher** or **lower**.*

---

## 🏆 Scoring System

The base score depends on the number of attempts used to guess the correct number:

| Attempts Used | Base Score |
| :---: | :---: |
| **1** | 100 |
| **2** | 80 |
| **3 – 4** | 60 |
| **5 – 6** | 40 |
| **7 – 8** | 20 |
| **9+** | 10 |

---

## 🛠️ Technologies Used

- **Language:** Python 3
- **Built-in Modules:** `random`
- **Third-Party Libraries:** `colorama`

---

## 📚 Python Concepts Practiced

Through this project, I practiced:
- Variables & basic data types
- Conditional statements (`if`/`elif`/`else`)
- `while` loops & nested loop control
- Structuring modular code with functions
- Handling invalid user input safely (`try`/`except`)
- Generating pseudorandom numbers (`random.randint`)
- Calculating absolute difference with `abs()`

---

## 🔮 Future Improvements

Features planned for upcoming versions or revisions:

- 🖥️️ **Tkinter graphical user interface**
- 🏅 **Persistent high-score system**
- 📈 **Detailed player statistics**
- 🎨 **Improved GUI design**
- 🔊 **Sound effects**
- 💾 **Saving game history**

---

## 📸 Demo
<img width="1107" height="736" alt="Screenshot 2026-10-01 at 9 39 12 PM" src="https://github.com/user-attachments/assets/b3d89677-c1b0-40ca-9d8a-7a3b8bfe640f" />
