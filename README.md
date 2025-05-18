3D zombie maze survival game built using **Python + PyOpenGL**, where you explore a procedurally generated maze, evade or shoot down enemies, and try to escape alive. This project showcases real-time rendering, basic AI, and keyboard/mouse interaction using OpenGL.

![Zombie Maze Demo](https://github.com/k-m-abrar-ahsan/Zombie_Maze/blob/master/zombie_maze.gif?raw=true)

---

## 🎮 Features

- 🧠 Procedurally generated maze using DFS backtracking
- 👾 AI-controlled zombie enemies with health, movement, and collision
- 🔫 Bullet shooting mechanics with collision detection
- 🔁 Dynamic camera switching: First-person and third-person view
- 🧱 Real-time 3D rendering using OpenGL (GL, GLUT, GLU)
- 📈 Scoring system, life counter, and UI elements
- 🌲 Environmental design: bushes, trees, and horizon background

---

## 📦 Requirements

Install dependencies using:

```bash
pip install -r requirements.txt
```

### `requirements.txt`
```
PyOpenGL
PyOpenGL_accelerate
```

---

## 🚀 How to Run

1. Clone this repo:
   ```bash
   git clone https://github.com/k-m-abrar-ahsan/Zombie_Maze.git
   cd Zombie_Maze
   ```

2. Run the game:
   ```bash
   python game.py
   ```

> ℹ️ Make sure your system supports OpenGL and you're running this in a GUI-enabled environment (e.g., Windows, macOS, or a Linux desktop session).

---

## 🕹️ Controls

| Key / Mouse | Action |
|-------------|--------|
| `W`, `A`, `S`, `D` | Move player |
| `Left Click` | Shoot bullet |
| `Right Click` | Switch between 1st and 3rd person |
| `P` | Pause / Unpause game |
| `R` | Restart game |
| `+ / -` | Increase / Decrease speed |
| `Arrow Keys` | Adjust camera angle and height |

---

## 📸 Screenshots

| Third-Person View | First-Person View |
|------------------|-------------------|
| ![image](https://github.com/user-attachments/assets/11efdb9a-0cc6-4870-bd54-6bb7e910d2d7)|![image](https://github.com/user-attachments/assets/d964ea73-57da-446f-be76-d32c6c2a928b)|

---

## 🧠 How It Works

- Maze is generated using a randomized depth-first search.
- Enemies spawn randomly in open cells and patrol using random directions.
- Collision is checked between player-enemy, bullet-enemy, and player-exit.
- Game ends on:
  - 🎯 Victory: Reaching the exit
  - ☠️ Game Over: Losing all lives

---

## 🛠️ Technologies Used

- `Python`
- `PyOpenGL`
- `OpenGL.GL`, `GLUT`, `GLU`
- `math`, `random` for physics and game logic

---

## 📌 Credits

Developed by K M Abrar Ahsan (https://github.com/k-m-abrar-ahsan)  
Inspired by the classics — Doom, Pac-Man, and Maze Runner

---

## ⭐️ Give it a Star!

If you enjoyed the project or found it useful, consider giving it a ⭐ on GitHub!
