# 🧩 Pac Ludo Fusion

**Pac Ludo Fusion** is a modern AI-enhanced maze game inspired by the classic **Pac-Man**, developed using **Pygame**. Players navigate a **rotating hexagonal maze**, collect pellets, and avoid intelligent AI-controlled ghosts. With each ghost powered by different algorithms—**Minimax**, **A\***, and **Q-learning**—the game blends strategic movement with real-time decision-making, offering a challenging and engaging experience.

---

## 🎮 Features

* **🔷 Hexagonal Grid Maze**
  A unique hex-tile layout replaces the traditional square maze, creating complex movement paths and a fresh spatial experience.

* **🔁 Dynamic Maze Rotation**
  The entire maze rotates **every 15 seconds**, altering all paths and forcing both the player and AI to re-strategize constantly.

* **🔸 Pellet Collection**
  Collect yellow pellets to score points. Every 50 pellets grants an **extra life**, and some pellets temporarily **freeze ghosts**.

* **🛡️ Player Invincibility**
  On respawn or life loss, players gain a few seconds of invincibility to recover and reposition.

* **👻 Smart AI-Controlled Ghosts**

  * 🔴 **Minimax Ghost**: Uses the Minimax algorithm to predict and intercept your next moves.
  * 🟦 **A\* Ghost**: Efficiently calculates the shortest path using the A\* pathfinding algorithm.
  * 💗 **RL Ghost**: Trained with **Q-learning** and **TensorFlow**, this ghost learns and adapts during gameplay.

---

## 🕹️ Controls

| Key | Action                        |
| --- | ----------------------------- |
| W   | Move Up                       |
| A   | Move Left                     |
| S   | Move Down                     |
| D   | Move Right                    |
| R   | Restart Game (after win/loss) |

* Click **"Start Game"** on the home screen to begin.

---

## 🧠 AI Technologies Used

* **A\* Pathfinding**: Ensures shortest-path pursuit to the player.
* **Minimax Algorithm**: Simulates future moves to trap the player.
* **Q-Learning (Reinforcement Learning)**: The RL ghost learns through trial and error using a TensorFlow-based neural network.

---

## 📦 Requirements

Install dependencies using pip (preferably in a virtual environment):

```bash
pip install pygame numpy tensorflow
```

---

## 🚀 Running the Game

Execute the following command in your terminal:

```bash
python game.py
```

---

## 🧩 Game Objective

* Collect **all pellets** to win.
* Avoid being caught by the AI ghosts.
* **Survive** with your **5 lives** and aim for the **highest score** possible.
* Adapt to the constantly shifting maze layout.

---

## 📸 Screenshots
![image](https://github.com/user-attachments/assets/a16e4089-033c-44ec-a42a-a63949f4361e)
![image](https://github.com/user-attachments/assets/cbf3daec-e71c-4c26-84b8-76cad413591f)
![image](https://github.com/user-attachments/assets/b2c4ccf4-ad1e-4525-b5d5-999cde217a21)
![image](https://github.com/user-attachments/assets/70c51ced-7678-4d0c-8eb2-42f4984934dd)

---
## 🧠 Inspiration

This game reimagines the classic **Pac-Man** through a fusion with **Ludo**, blending fast-paced maze navigation with strategic token-based gameplay. Drawing from Ludo’s mechanics, players guide tokens from a home position to a destination, making calculated moves to outmaneuver AI opponents, reminiscent of Ludo’s competitive board dynamics. The rotating hexagonal maze and diverse AI ghosts—powered by **Minimax**, **A*pathfinding**, and **Q-learning**—introduce unpredictable challenges, forcing players to adapt dynamically as the maze shifts. This hybrid design pushes both players and algorithms to balance Pac-Man’s reflex-driven pellet collection with Ludo’s thoughtful path planning, creating a unique, AI-enhanced experience.

---

## 🛠️ Future Improvements

* ✅ Multiplayer support for co-op or versus mode
* ✅ Persistent high score system
* ✅ Advanced animations and sound design
* ✅ Improved Q-learning with saved training sessions
* ✅ Additional power-ups (e.g., speed boost, ghost freeze)

---

## 📜 License

**GNU General Public License (GPL)**
Feel free to use, modify, and distribute this project.

