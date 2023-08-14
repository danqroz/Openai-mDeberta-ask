#!/bin/sh -e

SOURCE_FILES="app"
[[ $# -ge 1 ]] && SOURCE_FILES=$@

RUN=$([[ $PIPENV_ACTIVE == 1 ]] || echo "pipenv run")

set -xo pipefail

$RUN isort $SOURCE_FILES
$RUN black $SOURCE_FILES