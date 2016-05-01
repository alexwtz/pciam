#!/bin/sh

mkdir /tmp/stream
# -t 0 -> forver
raspistill --nopreview -w 640 -h 480 -q 5 -o /tmp/stream/pic.jpg -tl 50 -t 0 -th 0:0:0 &
cd /home/pi/picam/
cd mjpg-streamer-code-182/mjpg-streamer
./mjpg_streamer  -i "./input_file.so -f /tmp/stream -n pic.jpg" -o "./output_http.so -w ./www -c admin:secret" &
#cd ../../PiCam
#python picam.py
