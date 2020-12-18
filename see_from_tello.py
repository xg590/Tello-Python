#!/usr/bin/env python
# coding: utf-8
import time, queue, socket, sqlite3, datetime, threading
debug = True

class Tello:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('', 8889))
        self.db_queue  = queue.Queue() # cache flight data
        self.cmd_queue = queue.Queue()
        self.cmd_event = threading.Event()
        self.MAX_TIME_OUT = 15         # It must be longer than 10 sec, give time to "take off" command.
        self.MAX_RETRY = 2
        self.state = {}
        threading.Thread(target=self.flight_logger, kwargs={"debug":debug}, daemon=True).start()
        threading.Thread(target=self.receiver     , kwargs={"debug":debug}, daemon=True).start()
        threading.Thread(target=self.sender       , kwargs={"debug":debug}, daemon=True).start()
        threading.Thread(target=self.update_state , daemon=True).start()

    def command(self, cmd):
        self.cmd_queue.put(cmd)

    def save_flight_data(self):
        self.db_queue.put('commit')

    def stop_flight_logger(self):
        self.db_queue.put('close')

    def flight_logger(self, debug=False):
        con = sqlite3.connect(f'Tello_flight_log_{datetime.datetime.fromtimestamp(time.time()).strftime("%Y%m%d_%H%M%S")}.db')
        cur = con.cursor()
        cur.execute('CREATE TABLE commands(timestamp REAL, command TEXT, who TEXT);')
        cur.execute('CREATE TABLE   states(timestamp REAL, log     TEXT          );')
        if debug: print('Flight Data Recording Begins ~\n')
        while 1:
            operation = self.db_queue.get()
            if   operation == 'commit':
                con.commit()
                if debug: print(f'Flight Data Saved @ {datetime.datetime.fromtimestamp(time.time()).strftime("%Y%m%d_%H%M%S")}~')
            elif operation == 'close':
                con.close()
                if debug: print(f'Flight Data Recording Ends @ {datetime.datetime.fromtimestamp(time.time()).strftime("%Y%m%d_%H%M%S")}~')
                break
            else:
                cur.execute(operation)

    def receiver(self, debug=False):
        while True:
            bytes_, address = self.socket.recvfrom(1024)
            if bytes_ == b'ok':
                self.cmd_event.set() # one command has been successfully executed. Begin new execution.
            else:
                if debug: print('[ Station ]:', bytes_)
            try:
                self.db_queue.put('INSERT INTO commands(timestamp, command, who) VALUES({}, "{}", "{}");'.format(time.time(), bytes_.decode(), "Tello"))
            except UnicodeDecodeError as e:
                if debug: print('Decoding Error that could be ignored~')

    def sender(self, debug=False):
        tello_address = ('192.168.10.1', 8889)
        self.cmd_event.set()        # allow the first wait to proceed
        while True:
            self.cmd_event.wait()   # block second queue.get() until an event is set from receiver or failure set
            self.cmd_event.clear()  # block a timeout-enabled waiting
            cmd = self.cmd_queue.get()
            self.db_queue.put(f'INSERT INTO commands(timestamp, command, who) VALUES({time.time()}, "{cmd}", "Station");')
            self.socket.sendto(cmd.encode('utf-8'), tello_address)
            cmd_ok = False
            for i in range(self.MAX_RETRY):
                if self.cmd_event.wait(timeout=self.MAX_TIME_OUT):
                    cmd_ok = True
                    break
                else:
                    if debug: print(f'Failed command: "{cmd}", Failure sequence: {i+1}.')
                    self.socket.sendto(cmd.encode('utf-8'), tello_address)
            if cmd_ok:
                if debug: print(f'Success with "{cmd}".')
            else:
                self.cmd_event.set() # The failure set
                if debug: print(f'Stop retry: "{cmd}", Maximum re-tries: {self.MAX_RETRY}.')

    def update_state(self):
        UDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        UDP.bind(('', 8890))
        while True:
            bytes_, address = UDP.recvfrom(1024)
            str_ = bytes_.decode()
            self.db_queue.put('INSERT INTO states(timestamp, log) VALUES({},"{}");'.format(time.time(), str_))
            state = str_.split(';')
            state.pop()
            self.state.update(dict([s.split(':') for s in state]))

tello = Tello()

import cv2

class VIDEO:
    def __init__(self):
        tello.command('command')
        tello.command('streamon')
        self.void_frame = b''
        self.h264_frame = self.void_frame
        self.jpeg_frame = self.void_frame
        self.frame_event  = threading.Event() # tell transmitter that receiver has a new frame from tello ready
        threading.Thread(target=self.video_receiver   , kwargs={"debug":debug}, daemon=True).start()
        time.sleep(3)
        threading.Thread(target=self.video_transmitter, kwargs={"debug":debug}, daemon=True).start()
        time.sleep(3)
        threading.Thread(target=self.opencv           , kwargs={"debug":debug}, daemon=True).start()
        time.sleep(3)

    def video_receiver(self, debug=False): # receive h264 stream from tello
        _receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # socket for receiving video stream (UDP)
        _receiver.bind(('', 11111)) # the udp port is fixed
        while True:
            frame = b''
            while True:
                byte_, _ = _receiver.recvfrom(2048)
                frame += byte_
                if len(byte_) != 1460:       # end of frame
                    self.h264_frame = frame
                    self.frame_event.set()   # let the reading frame event happen
                    self.frame_event.clear() # prevent it happen until next set
                    break

    def video_transmitter(self, debug=False): # feed h264 stream to opencv
        _transmitter = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # socket for transmitting stream    (TCP)
        _transmitter.bind(('127.0.0.1', 12345)) # tcp port is up to us
        _transmitter.listen(0)
        while True:
            conn, address = _transmitter.accept()
            file_obj = conn.makefile('wb')
            stream_ready_flag = False
            while True:
                self.frame_event.wait()
                try:
                    file_obj.write(self.h264_frame)
                    file_obj.flush()
                except BrokenPipeError:
                    if debug: print('[ Warning ] Tello returned nonsense!')
                    if debug: print('[ Warning ] Please refresh stream after a while~\n')
                    break

    def opencv(self, debug=False):
        while True:
            cap = cv2.VideoCapture("tcp://127.0.0.1:12345")
            while(cap.isOpened()):
                ret, frame = cap.read()
                if not ret:
                    if debug: print('[ Error ] Please check if your tello is off~')
                    break
                ret, jpeg = cv2.imencode('.jpg', frame)
                self.jpeg_frame = jpeg.tobytes()
            cap.release()
            if debug: print('[ Warning ] OpenCV lost connection to transmitter!')
            if debug: print('[ Warning ] Try reconnection in 3 seconds~')
            time.sleep(3)

video = VIDEO()

import flask

app = flask.Flask(__name__)
fps=25
interval = 1/fps
@app.route("/stream.mjpg")
def mjpg():
    def generator():
        while True:
            time.sleep(interval)  # threading.condition is too shitty according to my test. no condition no lag.
            frame = video.jpeg_frame
            yield f'''--FRAME\r\nContent-Type: image/jpeg\r\nContent-Length: {len(frame)}\r\n\r\n'''.encode()
            yield frame
    r = flask.Response(response=generator(), status=200)
    r.headers.extend({'Age':0, 'Content-Type':'multipart/x-mixed-replace; boundary=FRAME',
                      'Pragma':'no-cache', 'Cache-Control':'no-cache, private',})
    return r

@app.route('/')
def hello_world():
    return 'Hello, World!'

def web():
    app.run('127.0.0.1', 9999)

threading.Thread(target=web , daemon=True).start() 
time.sleep(5) 
tello.command('takeoff'   )

tello.command('forward 50')
tello.command('cw 90'     )
tello.command('forward 50')
tello.command('cw 90'     )
tello.command('forward 50')
tello.command('cw 90'     )
tello.command('forward 50')
tello.command('cw 90'     )

tello.command('land'      ) 
time.sleep(43) 
tello.save_flight_data()
tello.stop_flight_logger()
time.sleep(3)