#!/bin/bash

# Academic Reporting System - Gradio Frontend
# Quick start script

echo "Starting Academic Reporting System (Gradio Frontend)..."

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Run the app
echo "Starting Gradio app on http://localhost:7860"
python app.py
