#!/bin/bash

source venv/bin/activate

# Run server.py in a new terminal
osascript -e 'tell application "Terminal" to do script "cd /Users/devin/sandbox/spring_2024/cryptography/cryptology_final_proj/src && python3 server.py"'

# Wait for the server to start before launching clients
sleep 2

# Run client.py in three new terminals

osascript -e 'tell application "Terminal" to do script "cd /Users/devin/sandbox/spring_2024/cryptography/cryptology_final_proj/src && python3 client.py"' & \
osascript -e 'tell application "Terminal" to do script "cd /Users/devin/sandbox/spring_2024/cryptography/cryptology_final_proj/src && python3 client.py"'

#
#python3 client.py
