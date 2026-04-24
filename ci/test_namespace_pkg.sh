#!/usr/bin/env bash
# Verifies that `akamai` is a proper namespace package by installing a second
# distribution that contributes akamai.dummy alongside akamai.edgegrid.
# Both sub-packages must be importable from the shared `akamai` namespace.
#
# Usage: bash ci/test_namespace_pkg.sh
set -euo pipefail

export REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV_DIR="$(mktemp -d)"
DUMMY_DIR="$(mktemp -d)"

cleanup() {
    rm -rf "$VENV_DIR" "$DUMMY_DIR"
}
trap cleanup EXIT

echo "==> Creating dummy fragment package in $DUMMY_DIR"
mkdir -p "$DUMMY_DIR/akamai/dummy"

# No akamai/__init__.py — this is a namespace package fragment, just like edgegrid-python.
cat > "$DUMMY_DIR/akamai/dummy/__init__.py" <<'EOF'
SENTINEL = "akamai.dummy is here"
EOF

cat > "$DUMMY_DIR/setup.py" <<'EOF'
from setuptools import setup, find_namespace_packages
setup(
    name="akamai-dummy",
    version="0.0.1",
    packages=find_namespace_packages(),
)
EOF

echo "==> Setting up isolated venv"
python3 -m venv "$VENV_DIR"
# shellcheck disable=SC1091
. "$VENV_DIR/bin/activate"

echo "==> Installing edgegrid-python (the real package)"
pip install --disable-pip-version-check -e "$REPO_DIR" -q

echo "==> Installing akamai-dummy (the second fragment)"
pip install --disable-pip-version-check -e "$DUMMY_DIR" -q

echo "==> Running namespace package import test"
python3 "$REPO_DIR/ci/check_namespace_pkg.py"
