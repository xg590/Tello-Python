## Python 3 version of https://github.com/dji-sdk/Tello-Python
### Summary
* Tello will fly autonomously
* You can see the streaming video from on-drone camera.
* The project is written in Python3 with minimum package dependency. 
* Flight data is logged for analysis.
### Usage
* If you want keep your system python clean, try the virtual environment.
```shell
sudo apt install python3-venv
python3 -m venv testTello
source testTello/bin/activate
```
1. Connect your machine to the Tello via WIFI
2. Run the code and fly Tello autonomously (it would take off, fly around and land by its own)
```
python3 fly_tello.py
```
* Install necessary libraries if you need image from Tello (opencv) and show it in your web browser (flask).
```shell
pip install opencv-python Flask # That is it. No other dependent libraries
```  
3. Run the code and visit http://127.0.0.1:9999/stream.mjpg by using your browser (keep refresh the page if you have problem)
```shell
python3 see_from_tello.py
```
### Something might be interesting
* Tello --[h264-encoded chunks of frame]--> UDP server on my PC --[h264-encoded frame]--> TCP server on my PC --[h264-encoded stream]--> OpenCV --[image]--> Flask
* We cannot get a video stream from Tello so we cannot use OpenCV directly. 
  * When I worked with raspberry pi, its camera utility can set up a tcp server then OpenCV can capture the h264 stream from it directly. But Tello is different because tello is not going to setup a streaming server (and it is not programmable to do that). 
* I was searching for a full-proof solution to decode locally buffered h264/H264/H.264 stream and get the image frame by frame. 
  * Tello is a client who sends out chunks of h264-encoded video stream to a udp server set up on my PC. It is up to me to collect those chunks and deal with it. 
  * I am familar with OpenCV but I don't know how to work with a locally buffered stream. 
  * In Tello_Video.ipynb, I demonstrated a solution by setting up a tcp server to <b>rebroadcast</b> the buffered stream. Yes, however we get the raw stream, we can feed it to a tcp server. OpenCV will capture the tcp stream and do the real-time decoding frame by frame.
