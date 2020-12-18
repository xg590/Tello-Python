## Python 3 version of https://github.com/dji-sdk/Tello-Python
### Usage
* If you want keep your system python clean, try the virtual environment.
```shell
sudo apt install python3-venv
python3 -m venv testTello
source testTello/bin/activate
```
* Connect your machine to the Tello via WIFI
* Run the code and fly Tello autonomously (it would take off, fly around and land on its own)
```
python3 fly_tello.py
```
* Install necessary libraries if you need image from Tello (opencv) and show it in your web browser (flask).
```shell
pip install opencv-python Flask # That is it. No other dependent libraries
```  
### Fly_Tello.ipynb
1. Commands are executed one by another, i.e., the former one will block the latter one.  
2. A command will be retried several time if it fails. 
3. Drone state and command history are stored. A sample Tello_flight_log_20201018_052457.db is provided.
### Tello_Video.ipynb streams the video in a web browser. 
* It <b>ONLY</b> depends on opencv-python !!!
* Use Flask to do web broadcasting.
* h264decoder is required by dji-sdk/Tello-Python but it sucks. I tried the installation without success. 
* I came up a bizarre solution so opencv can decode the stream.  
* Video frame is in jpeg format (yeah, computer vision).
### Something might be interesting
* Tello --[h264-encoded chunks of frame]--> UDP server on my PC --[h264-encoded frame]--> TCP server on my PC --[h264-encoded stream]--> OpenCV --[image]--> Flask
* We cannot get a video stream from Tello so we cannot use OpenCV directly. 
  * When I worked with raspberry pi, its camera utility can set up a tcp server then OpenCV can capture the h264 stream from it directly. But Tello is different because tello is not going to setup a streaming server (and it is not programmable to do that). 
* I was searching for a full-proof solution to decode locally buffered h264/H264/H.264 stream and get the image frame by frame. 
  * Tello is a client who sends out chunks of h264-encoded video stream to a udp server set up on my PC. It is up to me to collect those chunks and deal with it. 
  * I am familar with OpenCV but I don't know how to work with a locally buffered stream. 
  * In Tello_Video.ipynb, I demonstrated a solution by setting up a tcp server to <b>rebroadcast</b> the buffered stream. Yes, however we get the raw stream, we can feed it to a tcp server. OpenCV will capture the tcp stream and do the real-time decoding frame by frame.
