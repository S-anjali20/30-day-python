# 🧩 Day 13 — Sudoku Game

A classic and interactive Sudoku puzzle game built with Python and Pygame as part of my **30 Days, 30 Python Projects Challenge**!

Challenge your logical thinking, solve puzzles across three difficulty levels, use hints when needed, or watch the backtracking algorithm solve the puzzle automatically! 🧠

---

## 🎮 About the Project

**Sudoku Game** brings the classic 9×9 Sudoku puzzle to life with an interactive graphical interface. Players can select cells, enter numbers, track mistakes, request hints, and solve puzzles using an algorithm.

This project combines game development with **Data Structures and Algorithms (DSA)** concepts, especially recursion and backtracking, to create an engaging puzzle-solving experience.

---

## ✨ Features

- 🔢 **Interactive Sudoku Grid:** Play using a classic 9×9 Sudoku board.
- 🎯 **Three Difficulty Levels:** Choose from Easy, Medium, and Hard.
- 🎨 **Smart Cell Highlighting:** Highlight selected cells, rows, columns, and 3×3 boxes.
- ⌨️ **Keyboard Input:** Enter numbers directly using your keyboard.
- ❌ **Mistake Detection:** Incorrect entries are highlighted in red.
- 💡 **Hint System:** Reveal the correct number when you need help.
- ⏱️ **Game Timer:** Track the time taken to solve the puzzle.
- 📊 **Mistake & Hint Counters:** Keep track of your progress.
- 🧠 **Automatic Solver:** Solve the puzzle using a recursive backtracking algorithm.
- 🔄 **New Puzzle:** Generate a new puzzle whenever you want.
- 🏆 **Completion Message:** Get notified when you successfully solve the puzzle.

---

## 🛠️ Technologies Used

| Technology / Library | Purpose |
| :--- | :--- |
| **Python** | Core programming language |
| **Pygame** | Game interface, rendering, game loop, and keyboard and mouse interactions |
| **Recursion & Backtracking** | Algorithm for solving Sudoku puzzles |
| **Random Module** | Randomized puzzle generation and number selection |

---


---

## 🧠 How the Sudoku Solver Works

The game uses the **backtracking algorithm**, a popular DSA technique for solving constraint-based problems.

1. Find an empty cell in the Sudoku grid.
2. Try placing numbers from 1 to 9.
3. Check whether each number is valid in its row, column, and 3×3 box.
4. If a number is valid, place it and recursively solve the remaining grid.
5. If no number works, undo the previous choice and try another number.
6. Continue until the puzzle is solved or no solution exists.

This approach demonstrates how recursion and backtracking can efficiently explore possible solutions to a Sudoku puzzle.

---

## 📚 What I Learned

Through this project, I practised:

- Building interactive games using Pygame.
- Handling keyboard and mouse events.
- Working with two-dimensional lists.
- Implementing recursion and backtracking.
- Validating Sudoku rules programmatically.
- Managing game states, timers, and user feedback.
- Organizing Python projects using Git and dependency files.

---

## 🚀 Future Improvements

- 📝 Add pencil marks and candidate numbers.
- 🎨 Introduce light and dark themes.
- 🔊 Add sound effects.
- 💾 Save and resume unfinished puzzles.
- 🏅 Add a leaderboard and best-time tracking.
- 🧩 Generate puzzles with guaranteed unique solutions.
- 📈 Introduce difficulty levels based on solving techniques.

---

##Demo
<img width="980" height="755" alt="Screenshot 2026-10-14 at 9 42 06 PM" src="https://github.com/user-attachments/assets/79ea1ffc-4c4d-48c3-9a2f-b4da953ffca4" />



---

*Built with Python, powered by logic, and inspired by curiosity! 💜🧩*
