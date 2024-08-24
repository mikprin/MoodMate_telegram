#!/usr/bin/env bash



SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

BASEDIR=$(realpath $SCRIPT_DIR/..)

mkdir -p logs
docker logs mood_mate_bot &> "$BASEDIR/logs/mood_mate_bot_$(date +"%Y-%m-%d").log"
mkdir -p db_bkup
cp "$BASEDIR/moodmate_db/mood_mate.db" "$BASEDIR/db_bkup/mood_mate_$(date +"%Y-%m-%d").db"