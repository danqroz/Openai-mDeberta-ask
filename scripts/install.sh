#!/bin/bash -e

set -xo pipefail

PYTHON=$(command -v python3 > /dev/null && echo "python3" || echo "python")

$PYTHON -m pip install -U pip
command -v pipenv > /dev/null || pip install pipenv

pipenv install --dev --ignore-pipfile
