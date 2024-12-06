#!/usr/bin/env bash

# Get script directory
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Get the path to biom-calc-engine
BASEDIR=$(realpath $SCRIPT_DIR/..)
cd "$BASEDIR"
rm -rf .pytest_cache/
rm -rf dist/
rm -rf build/

# if venv exists, activate it, else create it
if [ -d "$BASEDIR/venv" ]; then
    source "$BASEDIR/venv/bin/activate"
else
    python3 -m venv "$BASEDIR/venv"
    source "$BASEDIR/venv/bin/activate"
fi


# Install requirements
pip3 install pytest pytest-asyncio
pip3 install -r "$BASEDIR/requirements.txt"
export SQLITE_DB_PATH=./test_db.db

source "$BASEDIR/test.env"
echo "Running tests"
echo "DATABASE_URL: $SQLITE_DB_PATH"

python3 -m pytest -v "$BASEDIR/test/tests"
