*This project has been created as part of the 42 curriculum by fomanca and etchipoq.*

## Description

Pac-Man is a 2D maze game developed in Python using the Pygame CE library as part of the 42 curriculum.

The objective is to control Pac-Man through a maze, collect all the pellets, avoid the ghosts, and progress through multiple levels. Players can collect Super Pellets to make ghosts vulnerable and eat them for extra points.

### Game Features

- A main menu with different game options.
- Multiple levels with randomly generated mazes.
- Four ghosts with different behaviours.
- A scoring and lives system.
- A timer for each level.
- A pause and resume system.
- A persistent Top 10 highscore system.
- A cheat mode with additional gameplay features.

The project was developed using **Object-Oriented Programming (OOP)** principles and includes configurable game settings through a JSON configuration file.

## Instructions

### Requirements

- Python 3.12 or higher.
- uv package manager.
- Pygame CE.
- NumPy.

### Installation

Clone the repository and navigate to the project directory.

Install the dependencies:

```bash
make install
```

### Running the Game

Start the game using:

```bash
make run
```

### Controls

| Key | Action |
|---|---|
| Arrow Keys / WASD | Move Pac-Man |
| SPACE | Pause or resume the game |
| ESC | Return to the main menu while paused |

## Resources

### Libraries

- **Python 3.12** - Main programming language.
- **Pygame CE** - Used to create the game window, graphics, animation, keyboard input and game loop.
- **NumPy** - Used for numerical operations.

### Maze Generator

The project uses the A-Maze-ing maze generator provided for the 42 curriculum.

The external maze generator is used without modifying its original source code.

### Fonts and Assets

- **Press Start 2P** - Font used for the game's text and menus.

### Development Tools

- **uv** - Python package and dependency manager.
- **git** - Version Control.
- **Make** - Project automation through the Makefile.

## Configuration

The game settings can be custommized through the `config.json` file located in the root of the project.

The configuration file supports the following parameters:

| Parameter | Type | Default Value | Description |
|---|---|---|---|
| `maze_size` | List | `[15, 15]` | Defines the dimensions of the maze (rows and columns). |
| `perfect` | Boolean | `false` | Determines whether the maze generator creates a perfect maze. |
| `entry_cell` | List | `[0, 0]` | Defines the maze entrance coordinates. |
| `exit_cell` | List | `[14, 14]` | Defines the maze exit coordinates. |
| `seed` | Integer | `42` | Sets the random seed used to generate the first maze. |
| `level_time` | Integer | `120` | Sets the time limit for each level, in seconds. |
| `max_levels` | Integer | `10` | Defines the maximum number of levels in the game. |


### Example Configuration

```json
{
    "maze_size": [15, 15],
    "perfect": false,
    "entry_cell": [0, 0],
    "exit_cell": [14, 14],
    "seed": 42,
    "level_time": 120,
    "max_levels": 10,
}
```

### Configuration Notes

- The first level uses the seed specified in the configiration file.
- Subsequent levels use randomly generated seed.
- The time limit applies individually to each level.
- If a player runs out of time, one life is lost.
- The game use default values when configuration parameters are missing or invalid.

## Highscores

The game includes a persistent Top 10 Highscors system.

Player scores are stored in a JSON name `highscore.json`.

### How It Works

- At the end of game, the player is asked to enter their name.
- Player names can contain up to 10 caracteres.
- Only letters, numbers and spaces are allowed.
- Scores must be non-negative integers.
- Scores are sorted in descending order.
- Only the 10 highest scores are saved.
- Highscores are loaded when the game starts.
- Highscores are save automatically after a valid score is submitted.

### Highscores Display

- The main menu displays the top 4 scores.
The Highscores menu displays the complete Top 10 ranking.

### Data Storage

The `highscore.json` file stores player names and their corresponding scores.

Example:

```json
[
    {
        "name": "Pacman"
        "score": 1500
    },
    {
        "name": "Player1"
        "score": 500
    }
]
```

## Maze Generation

The game uses the external **A-Maze-ing** maze generator provided as part of te 42 curriculum

The original maze generator package is used without modifying its source code.

### Maze Configuration

The maze generator receives the following parameters from `config.json`:

- `maze_size`: Defines the dimensions of the maze.
- `perfect`: Determine whether a perfect maze is generated.
- `entry_cell`: Defines the entrance coordinates.
- `exit_cell`: Defines the exit coordinates
- `seed`: Defines the random seed used for maze generation.

### Level Generation

- The first level uses the seed defined in `config.json`.
- Subsequent levels use randomly generated seeds.
- Each new level generates a different maze.
- Previously used seeds are not reused during the same game session.

The maze is generated when a new level starts.

## Implementation

The game is developed in Python using Object-Oriented Programming (OOP) principles and the Pygame CE library.

### Programming Language and Libraries

- **Python:** Main programming language.
- **Python CE:** Handles graphics, animation, keyboard input and the game loop.
- **NumPy:** Used for numerical operations.

### Main Game Components

The project is diveded into several Python modules, each responsible for a specific part of the game:

- `pacman.py`: Implements the Pac-Man character, including movements and player behaviour.
- `ghosts.py`: Implements the ghosts, their movement and behaviour modes.
- `entity.py`: Provides shared funtionality for game entities.
- `nodes.py`: Handles the maze nodes and connections between corridors.
- `pellets.py`: Manages the pellets collected by pac-man
- `modes.py`: Controls the different ghost behaviour modes.
- `pauser.py`: Handles the game's pause system
- `sprites.py`: Manages sprite images and animations.
- `text.py`: Handles game text, score, lives, level and timer displays.
- `run.py`: Contains the main menu game controller and coordinates the game components.
- `higscores.py`: Handles loading, saving and sorting high scores.

### Game Loop

The main game loop is responsible for:

1. Processing keyboard and window events.
2. Updating the player and ghost positions.
3. Checking collisions and pellet collections.
4. Updating the score, lives and timer .
5. Rendering the game elements on the screen.

the game continues running until the player exits, loses all lives or completes all the available levels.

## General Software Architecture

the project follows an Object-Oriented Programming (OOP) architecture. Each module is responsible for a specific part of the game, making the code easier to maintain and extend.

### Architecture Overview

The main game controller, implemented in `run.py`, coordinates the different components of the game.

The architecture is organized into the following main part:

- **Game Controller:** Manages the game loop, events, levels, menus and overall game state.
- **Player:** Handles Pac-Man movement, animations and interactions.
- **Ghosts:** Controls ghost movement, artificial intelligence and behaviour modes.
- **Maze:** Manages the maze structure, nodes and connections.
- **Collectibles:** Handles Pac-Gums, Super Pac-Gums and scoring.
- **User Interface:** Displays menus, score, lives, timer, level information and messages.
- **Highscores:** Manages persistent player rankings.
- **Pause System:** Controls pausing and resuming the game.

### Object-Oriented Desing

The projrct uses classes to represent the main game elements.

This approach allows each component to manage its own responsibilities while interacting with other components when necessary.

The game contrller coordinates these objects to ensure that the game runs correctly.

## Project Management

The project was developed collaboratively by two students as part of the 42 curriculum.

Project management documentation is organized in a dedicated directory.

### Project Documentation

The project management directory includes:

- **Timeline:** Project schedule and development milestones.
- **Progress Tracking:** Tasks completed and remaining work.
- **Technical Decisions:** Important decisions made during development.
- **Risk Analysis:** Potential risks and proposed solutions.
- **Team Organization:** Responsibilities and collaboration between team members.
- **Testing Plan:** Acceptance tests and validation procedures.

### Team Members

- **fomanca**
- **etchipoq**
