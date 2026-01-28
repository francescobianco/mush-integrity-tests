#!/bin/bash
set -e

# Install MUSH
# TODO: Add MUSH installation steps here

# Install test dependencies
#pip install -e ".[dev]" --quiet
python3 -m venv venv
source venv/bin/activate

# Run test suite
pytest "$@"
