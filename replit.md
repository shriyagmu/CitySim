# Overview

This is a web-based city simulation game built with Flask where players manage a 5×5 grid city. The game allows users to zone different areas (residential, commercial, industrial, parks) and build structures (schools, hospitals, power plants, roads) to grow their city. The simulation tracks population, happiness levels, and progression through years, providing an interactive city-building experience in the browser.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
The frontend uses a traditional server-rendered approach with Flask templates, enhanced by vanilla JavaScript for interactive grid management. The main interface consists of a 5×5 grid where users can click cells to select and modify them. Bootstrap provides the UI framework with a dark theme, while custom CSS handles the grid layout and hover effects. JavaScript manages client-side interactions like cell selection, zone buttons, and keyboard shortcuts.

## Backend Architecture
The application follows a simple MVC pattern using Flask as the web framework. The main application logic is split between `app.py` (handling HTTP routes and session management) and `game_logic.py` (containing the core game simulation). The CitySimulation class encapsulates all game state and business logic, including grid management, zone validation, and city statistics tracking.

## Data Storage
The application uses Flask sessions for data persistence, storing the entire city state as a serialized dictionary in the user's session. This approach eliminates the need for a database while providing stateful gameplay. The CitySimulation class includes `to_dict()` and `from_dict()` methods to handle serialization and deserialization of game state.

## Game Logic
The core simulation revolves around a 5×5 grid where each cell can contain different zone types (R, C, I, P) or building types (School, Hospital, Power, Road). The system tracks city metrics like population and happiness, providing feedback on the player's city management decisions. The game progresses through years, allowing for temporal progression of the simulation.

# External Dependencies

## Web Framework
- **Flask**: Core web framework handling routing, templating, and session management
- **Bootstrap**: Frontend CSS framework providing responsive design and dark theme support

## Client-Side Libraries
- **Bootstrap JavaScript**: Handles interactive components like dismissible alerts and responsive behavior
- **Vanilla JavaScript**: Custom game logic for grid interaction, cell selection, and user interface management

## Development Tools
- **Python logging**: Built-in logging for debugging and monitoring application behavior
- **Flask development server**: Local development environment with debug mode enabled

The application is designed to run standalone without external databases or complex deployment requirements, making it suitable for educational purposes or simple game prototyping.