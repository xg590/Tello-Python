## Python 3 version of https://github.com/dji-sdk/Tello-Python
### Fly_Tello.ipynb
1. Commands are executed one by another, i.e., the former one will block the latter one.  
2. A command will be retried several time if it fails. 
3. Drone state and command history are stored. A sample Tello_flight_log_20201018_052457.db is provided.
### Tello_Video.ipynb streams the video in a web browser. 
* It <b>ONLY</b> depends on opencv-python !!!
* h264decoder is required by dji-sdk/Tello-Python but it sucks. I tried the installation without success. 
* I came up a bizarre solution so opencv can decode the stream.  
* Video frame is in jpeg format (yeah, computer vision).
### Usage
```shell
pip install opencv-python # that is it. No PIL and libboost-python
```
