import socket

class RS_gen():

    def __init__(self, ip = '10.2.117.45', port = 5025, buffer_size = 1024, timeout = 5):
        self.ip = ip
        self.port = port
        self.buffer_size = buffer_size
        try:
            self.socket = socket.create_connection((self.ip,self.port), timeout)
            self.set_pow()
        except socket.error:
            raise

    def send_msg(self, msg):
        msg = str.encode(str(msg))
        self.socket.send(msg)

    def read_msg(self, read_buffer_size = 0):
        read_buffer_size = self.buffer_size
        data = self.socket.recv(read_buffer_size)
        return data

    def ask(self, msg):
        self.send_msg(msg)
        data = self.read_msg()
        return data

    def set_pow(self, pout = -80):
        self.send_msg('POW '+str(pout)+'\n')

    def set_freq(self, freq = 100e6):
        self.send_msg('FREQ '+str(freq)+'\n')

    def rf_on(self):
        self.send_msg('OUTP ON\n')

    def rf_off(self):
        self.send_msg('OUTP OFF\n')

    def serial(self):
        data = self.ask(b'*IDN?\n')
        print (data)
        return data
