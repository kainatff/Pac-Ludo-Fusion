🧩 Pac Ludo Fusion 
Pac Ludo Fusion is a dynamic Pac-Man-inspired maze game built with pygame, where players collect pellets, avoid AI-controlled ghosts, and navigate a rotating hexagonal maze. It combines pathfinding, decision-making AI, and reinforcement learning to create intelligent ghost behaviors and an engaging challenge for players.
🎮 Features
Hex-based Maze: A hexagonal grid offers a twist on the classic square maze layout.


Dynamic Maze Rotation: The entire maze rotates every 15 seconds, changing paths and strategies.


Pellet Collection: Eat yellow pellets to score points and occasionally freeze ghosts.


Player Invincibility: Players get temporary invincibility on respawn.


Smart Ghosts:


🔴 Minimax Ghost: Predicts your moves using the minimax algorithm.


🟦 A Ghost*: Finds shortest paths using A* pathfinding.


💗 RL Ghost: Learns optimal moves via Q-learning and a neural network.


🕹️ Controls
Move using:


W: Up


A: Left


S: Down


D: Right


From the home screen, click Start Game to begin.


Press R to restart after Game Over or Victory.


🧠 AI Technologies Used
A* Pathfinding – For shortest-path movement.


Minimax Algorithm – For predictive decision-making.


Reinforcement Learning – Ghost learns optimal paths via a TensorFlow-based Q-network.


📦 Requirements
Install the following packages (preferably in a virtual environment):
pip install pygame numpy tensorflow

🚀 Run the Game
python game.py

🧩 Game Objective
Collect all pellets while avoiding ghosts.


Maze rotates to challenge your spatial reasoning.


Survive with your 5 lives and aim for the highest score!


📸 Screenshots
(Optional – add screenshots showing the maze, gameplay, and ghost behavior.)
📁 File Structure
game.py – Main game logic and AI implementations


HexTile, DynamicMaze, Player, Ghost – Core game objects


AStarPathfinder, MinimaxAI, QLearningAI – AI engines for ghosts


GameController – Handles drawing, inputs, states, and gameplay


🧠 Inspiration
Inspired by Pac-Man, but reimagined with a modern AI twist and a rotating maze mechanic to encourage adaptability and strategy.
🛠️ Future Improvements
Multiplayer support


Save/load high scores


Enhanced animations and sound effects


Better-trained Q-learning agent with persistent learning


📜 License
GNU License — feel free to use, modify, and share!

