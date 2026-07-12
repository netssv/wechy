# TUI Application Architecture

## Overview
The **Wechy Web Techy Overview** is designed entirely around a Terminal User Interface (TUI). This architecture completely abandons legacy web and monolithic patterns in favor of a responsive, keyboard-driven terminal application.

## Core Libraries
- **Textual**: A Rapid Application Development framework for Python, providing a modern, reactive approach to terminal interfaces.

## Structure
```
tui_app/
├── __init__.py
├── main.py            # Entry point for the TUI application
└── ui/                # UI Components and Screens
    ├── __init__.py
    └── dashboard.py   # Main dashboard layout
```

## Principles
1. **Terminal-First**: No HTML/CSS or web servers are used. All rendering happens within the terminal emulator using ANSI escape sequences.
2. **Component-Based**: UI elements are structured as reusable Widgets and Screens.
3. **Reactive state**: UI updates reactively based on state changes.
4. **Keyboard-Centric**: Primary interaction is driven by keyboard shortcuts, though mouse support is available via Textual.
