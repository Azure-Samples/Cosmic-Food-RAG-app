#!/bin/bash

set -e
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 -m hypercorn quartapp --bind=0.0.0.0
