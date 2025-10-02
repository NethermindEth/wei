#!/bin/bash

# Setup script for Wei Auth Service

set -e

echo "Setting up Wei Auth Service..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv .venv

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file from env.example..."
    cp env.example .env
    echo ""
    echo "IMPORTANT: Please edit the .env file and add your Clerk credentials:"
    echo "  - CLERK_SECRET_KEY"
    echo "  - CLERK_PUBLISHABLE_KEY"
    echo "  - ALLOWED_SERVICE_KEYS"
    echo ""
fi

echo ""
echo "Setup complete!"
echo ""
echo "To start the server:"
echo "  1. Activate the virtual environment: source .venv/bin/activate"
echo "  2. Edit .env with your Clerk credentials"
echo "  3. Run: python main.py"
echo ""
echo "To run tests:"
echo "  pytest tests/"
echo ""

