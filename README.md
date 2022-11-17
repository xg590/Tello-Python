## Python 3 version of [dji-sdk/Tello-Python](https://github.com/dji-sdk/Tello-Python)
### Summary
* Written in Python 3 with minimum package dependency for video streaming and processing. (opencv-python and Flask)
* Fly Tello and watch the video streaming from on-drone camera in a web browser.
* Flight data is logged for later analysis. 
### Usage
* If you want keep your system python clean, try the virtual environment.
```shell
sudo apt install python3-venv
python3 -m venv testTello
source testTello/bin/activate
```
1. Connect your machine to the Tello via WIFI. (Don't worry about IP. Tello will assign one for your machine)
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
### Computer Vision
* Tello will not setup a video streaming service for you to capture so you cannot use OpenCV directly.
  * If you worked with raspberry pi, you know its camera utility can set up a tcp server then you can use opencv to capture the h264 stream from it directly. 
  * Tello is different. It does not setup a streaming server and you can not program it to do that. 
* You need to setup a video clip collector (a UDP service) then Tello will send video clips to your collector. 
  * Tello is a client who sends out chunks of h264-encoded video stream to a udp server set up on your PC. It is up to you to collect those chunks and deal with it. 
  * I don't know how to work with a locally buffered stream but I am familar with OpenCV.  
  * In see_from_tello.py, I demonstrated a solution by setting up tcp and udp services to <b>rebroadcast</b> the buffered stream. 
  * Tello sends the stream data my udp service then are fed to a tcp service. OpenCV can capture the tcp stream and do the real-time decoding frame by frame.
* Tello --[h264-encoded chunks of frame]--> UDP server on my PC --[h264-encoded frame]--> TCP server on my PC --[h264-encoded stream]--> OpenCV --[image]--> Flask
