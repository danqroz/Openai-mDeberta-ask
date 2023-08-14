#!/bin/bash -e

SOURCE_FILES="app"
[[ $# -ge 1 ]] && SOURCE_FILES=$@

RUN=$([[ $PIPENV_ACTIVE == 1 ]] || echo "pipenv run")

set -xo pipefail

$RUN isort --check --diff $SOURCE_FILES
$RUN black --check --diff $SOURCE_FILES
$RUN flake8 $SOURCE_FILES