#!/bin/bash
#!/usr/bin/env python3

# export DISPLAY=:0 #needed if you are running a simple gui app.

cd "$(dirname "$0")"

process=script__masking_ntp

python3 masking.py  --rtsp 'rtsp://admin:qwerty123!@50.60.70.11:554/Streaming/Channels/102' --masking "" --input_titik 3 

sleep 10