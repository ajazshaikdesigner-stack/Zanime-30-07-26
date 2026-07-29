# Zanime Installation Guide

Welcome to Zanime! To install the application from source or via the Portable Edition, follow these instructions.

## Prerequisites
Zanime requires **FFmpeg** to function. Without it, the `ProductionRenderer` will silently fail.
1. Download FFmpeg for Windows.
2. Extract the `.zip` file.
3. Add the `/bin` directory to your System Environment Variables `PATH`.

## Installing from Source
1. Clone the repository.
2. Ensure you have Python 3.11 installed.
3. Run `pip install -r requirements.txt`.
4. Run `python src/app.py`.

## GPU Requirements
For local AI execution, an AMD RX6500M 4GB (or Nvidia equivalent) is highly recommended. Ensure your GPU drivers are up to date.
