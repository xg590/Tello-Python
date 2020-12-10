## Python 3 version of https://github.com/dji-sdk/Tello-Python
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
### Usage
```shell
pip install opencv-python Flask# That is it. No PIL and libboost-python
```
### Something might be interesting
* When I worked with raspberry pi, its camera utility can set up a tcp sever then OpenCV can capture the h264 stream directly. But Tello is different and it is not programmable! I have to gather h264 stream from Tello via a udp server on my PC and then deal with it. 
  * We don't get video stream from Tello.
  * What we get from Tello is chucks of h264-encoded video stream. We have put chucks togather to form a stream in buffer and decode it on the fly. 
  * I was searching for a full-proof solution to decode locally buffered h264/H264/H.264 stream and get the image frame by frame. 
  * I am familar with OpenCV but I don't know how to work with a locally buffered stream. 
  * In Tello_Video.ipynb, I demonstrated a solution by setting up a tcp server to <b>rebroadcast</b>. Yes, however we get the raw stream, we can feed it to the tcp server. OpenCV will capture stream from tcp server and do the real-time decoding frame by frame.
