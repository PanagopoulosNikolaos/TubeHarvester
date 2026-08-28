#!/usr/bin/env python3
"""
Main entry point for TubeHarvester application.

Launches the NiceGUI web application interface.
"""

from src.ui.app import createApp

if __name__ == "__main__":
    createApp()
