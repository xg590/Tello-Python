import time, queue, socket, sqlite3, datetime, threading  

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
        threading.Thread(target=self.flight_logger, kwargs={"debug":True}, daemon=True).start() 
        threading.Thread(target=self.receiver     , kwargs={"debug":True}, daemon=True).start()
        threading.Thread(target=self.sender       , kwargs={"debug":True}, daemon=True).start()   
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
tello.command('command') 
time.sleep(0.1)
input("\nIt may take 10 seconds for Tello to take off. \nPress any key to continue~\n")
input("Please press any key after the landing... \nNow press any key to take off~\n") 
tello.command('takeoff'   )  
tello.command('forward 50')
tello.command('left 50'   )
tello.command('back 50'   )
tello.command('right 50'  ) 
tello.command('land'      )  
input()
print("Give Tello 3 seconds to save flight data")
tello.save_flight_data() 
tello.stop_flight_logger()
time.sleep(3)