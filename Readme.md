# Pygame Parkour Runner

A fast-paced, side-scrolling parkour game built with Pygame, featuring procedurally generated levels and dynamic difficulty. Dodge obstacles, collect power-ups, and run as far as you can to set a new high score!

![Gameplay Screenshot](placeholder.gif)
*(Suggestion: Record a short GIF of your gameplay and replace `placeholder.gif` with its filename.)*

## Features

-   **Infinite Procedural World**: Never play the same level twice! The game generates platforms and challenges on the fly.
-   **Dynamic Difficulty**: The game speed steadily increases the longer you survive, keeping the challenge fresh.
-   **Fluid Player Movement**: Responsive controls for running, jumping, and double-jumping.
-   **Flight Power-up**: Collect special items to gain the ability to fly for a short duration, avoiding tricky sections.
-   **Persistent High Score**: The game saves your best distance locally, so you always have a record to beat.
-   **Zero Dependencies (besides Pygame)**: All visual assets—from the player and platforms to the background—are generated procedurally by the code, requiring no external image files.

## How to Play

The goal is to travel as far as possible without falling off the screen.

-   **Move Left/Right**: `A` / `D` or `Left Arrow` / `Right Arrow`
-   **Jump / Double Jump**: `Spacebar` or `Up Arrow`
-   **Fly (with power-up active)**: `W` / `S` or `Up Arrow` / `Down Arrow`

## Installation & Setup

This project is built with Python and the Pygame library.

1.  **Prerequisites**:
    * Make sure you have Python 3 installed on your system.

2.  **Clone the Repository**:
    ```bash
    git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
    cd your-repo-name
    ```

3.  **Install Dependencies**:
    The only external library required is Pygame. You can install it using pip.
    ```bash
    pip install pygame
    ```

4.  **Run the Game**:
    Execute the Python script to start the game.
    ```bash
    python parkourgame.py
    ```
    A file named `parkour_highscore.txt` will be created in the same directory to store your high score.

## Code Overview

-   **`Game` Class**: Manages the main game loop, screen setup, events, scoring, and platform generation logic.
-   **`Player` Class**: Handles all player physics, including movement, gravity, jumping, and collision detection.
-   **`Platform` & `Powerup` Classes**: Sprite classes for the objects the player interacts with.
-   **Procedural Asset Functions**: A set of functions (`create_player_image`, `create_platform_image`, etc.) are used to draw the game's visuals directly onto `pygame.Surface` objects. This keeps the project lightweight and self-contained.
