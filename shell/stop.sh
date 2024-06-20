#!/usr/bin/bash

BASEDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Get the PID of the Flask app
pid=$(ps aux | grep 'app-comfyui-apigw/main.py' | grep -v grep | awk '{print $2}')

# Check if the Flask app is running
if [ ! -z "$pid" ]
then
    echo "Stopping server ..."
    # Kill the Flask app if it is running
    kill -9 $pid
else
    echo "Server already stopped. Skip."
fi
