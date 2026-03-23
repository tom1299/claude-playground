#!/bin/bash
set -e

if [ ! -d "$WORKSPACE_FOLDER/.venv" ]; then
    echo "Creating virtual environment with python at /usr/bin/python..."
    # Use specific path to python so that it also works on the host
    uv venv --python=/usr/bin/python "$WORKSPACE_FOLDER/.venv"
    echo "Virtual environment created at /workspace/.venv"
fi

source "$WORKSPACE_FOLDER/.venv/bin/activate"

echo "Syncing project dependencies with uv..."
cd "$WORKSPACE_FOLDER"
uv sync --python=/usr/bin/python --active

