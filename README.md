### Fly_Tello.ipynb is a better version of https://github.com/dji-sdk/Tello-Python. And it is written in python3.
1. Commands are executed one by another, i.e., the former one will block the latter one.  
2. A command will be retried several time if it fails. 
3. Drone state is stored. A sample Tello_flight_log_20201018_052457.db is provided.
### Tello_Video.ipynb streams the video in a web browser. 
* It only depends on opencv-python !!!
* h264decoder is required by dji-sdk but it sucks. I tried the installation without success. 
* I came up a bizarre solution so opencv can decode the stream.  
* Video frame is in jpeg format (computer vision).
