#!/bin/bash

set -e
python3 -m pip install --upgrade pip
python3 -m pip install uv
uv sync --active
uv run hypercorn 'quartapp.app:create_app()' --bind=0.0.0.0
