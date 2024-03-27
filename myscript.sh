

#!/bin/bash
#!/usr/bin/env python3

export DISPLAY=:0 #needed if you are running a simple gui app.

cd "$(dirname "$0")"

process=script_ntp
while true
do

    if ! ps aux | grep -v grep | grep 'python3 main1_new.py --rtsp rtsp://admin:qwerty123!@50.60.70.11:554/Streaming/Channels/102' > /dev/null
    then #--nocctv 1
        python3 main1_new.py --rtsp 'rtsp://admin:qwerty123!@50.60.70.11:554/Streaming/Channels/102' --delay 20 --nocctv "03" --masking "" --input_titik 3 --endpoint http://127.0.0.1:8200/status_auto &
        sleep 30 #--nocctv 1
    fi #--nocctv 1

sleep 10
done
exit
        