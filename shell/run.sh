#!/usr/bin/bash

BASEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if the Flask app is running
if ! ps aux | grep -v grep | grep 'main.py' > /dev/null
then
    # Start the Flask app if it is not running
    echo "Starting server..."
    #nohup python3 $BASEDIR/../main.py >> $BASEDIR/../logs/$(date "+%Y-%m-%d").log 2>&1 &
    python3 $BASEDIR/../main.py >> $BASEDIR/../logs/$(date "+%Y-%m-%d").log 2>&1
    sleep 1
	sudo systemctl reload nginx
else
    echo "Server already started. Skip."
fi
