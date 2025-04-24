#!/bin/sh
set -e
REPO_ROOT=$(git rev-parse --show-toplevel)
IMAGE="edgegrid-python-unittest:$(uuidgen | tr '[:upper:]' '[:lower:]')"

echo "Building docker image: $IMAGE in $REPO_ROOT/ci"
docker build -t "$IMAGE" "$REPO_ROOT/ci"

echo "Running unit tests inside the container..."
set -x
# umask 0000: provide permissive access rights to files created as root on the mounted volume.
CMD=". ~/.profile && umask 0000 && pyenv local 3.9 3.10 3.11 3.12 3.13 && tox"
docker run --rm -v $REPO_ROOT:/testdir -w /testdir "$IMAGE" sh -c "$CMD"
