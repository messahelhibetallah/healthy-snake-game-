# Healthy Snake Adventure

**Date:** June 27, 2026

Healthy Snake Adventure is a Python game built with Pygame. Players
control a snake that collects healthy foods to gain health and points
while avoiding unhealthy foods that reduce health.

## Features

-   Classic Snake gameplay with health system
-   Healthy and unhealthy food items
-   Animated food and particle effects
-   Power-ups:
    -   Speed Boost
    -   Health Boost
    -   Double Points
    -   Magnet
-   Daily score saving using JSON
-   Pause, restart, and game over screens
-   Automatic placeholder images if food images are missing

## Requirements

-   Python 3.9+
-   pygame

Install:

``` bash
pip install pygame
```

## Project Structure

    healthy.py
    images/
    daily_scores.json
    README.md

## Run

``` bash
python healthy.py
```

## Controls

-   Arrow Keys: Move
-   P: Pause
-   R: Restart after game over
-   Q: Quit after game over

## Notes

If the `images` folder does not contain the required PNG files, the game
automatically generates placeholder graphics.

