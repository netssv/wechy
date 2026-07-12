# Wechy Web Techy Overview

```text
 __      __        _           __      __    _    _______        _           ___                  _               
 \ \    / /       | |          \ \    / /   | |  |__   __|      | |         / _ \                (_)              
  \ \  / /__  ___ | |__  _   _  \ \  / /___ | |__   | | ___  ___| |__  _   _| | | |_   _____ _ __ _  _____      __
   \ \/ / _ \/ __|| '_ \| | | |  \ \/ // _ \| '_ \  | |/ _ \/ __| '_ \| | | | | | \ \ / / _ \ '__| |/ _ \ \ /\ / /
    \  /  __/\__ \| | | | |_| |   \  /|  __/| |_) | | |  __/ (__| | | | |_| | |_| |\ V /  __/ |  | |  __/\ V  V / 
     \/ \___||___/|_| |_|\__, |    \/  \___||_.__/  |_|\___|\___|_| |_|\__, |\___/  \_/ \___|_|  |_|\___| \_/\_/  
                          __/ |                                         __/ |                                     
                         |___/                                         |___/                                      
```

Welcome to **Wechy Web Techy Overview**!

This project provides a robust, purely terminal-based user interface (TUI) for system and web tech administration, completely distinct from any legacy web-based or monolithic approaches.

## Project Refactoring & Architecture
This new TUI interface was built by deeply refactoring the legacy code from the `monolith_old` folder. We successfully decoupled the monolithic logic, separating the configuration, UI presentation, and core behavior into a highly modular, component-based terminal architecture using Textual. This allows for far greater maintainability, reusability, and easier integration with AI Agents.

## Features
- **Intuitive TUI**: Navigate via keyboard through a structured, responsive terminal interface.
- **Modular Architecture**: Built from the ground up for maintainability and scalability in terminal environments.
- **Zero Legacy Bloat**: This project abandons all `monolith_old` patterns.

## Installation & Running
Ensure you have Python 3.8+ installed.

```bash
pip install -r requirements_tui.txt
python -m tui_app.main
```
