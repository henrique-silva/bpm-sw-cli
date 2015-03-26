#ls /dev/tty*
#
#
import socket



ip="10.0.18.53"
rfsw_address = ((ip, 6791))
rfsw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
rfsw_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
rfsw_socket.settimeout(5.0)
rfsw_socket.connect(rfsw_address)
rfsw_socket.send(b":SC11!")
rfsw_socket.close()
rfsw.close_connection()


####remotelly control the Agilent 33521A
import socket
import struct
ip="10.0.18.50"
signal_gen_addr = ((ip, 5025))
signal_gen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
signal_gen.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
signal_gen.settimeout(5.0)
signal_gen.connect(signal_gen_addr)
signal_gen.send("OUTPUT1:LOAD 50\n")
signal_gen.send("SOURCE1:VOLT:UNIT VPP\n")
signal_gen.send("SOURCE1:VOLT:OFFSET 3\n")
signal_gen.close()





"""Get the S12 trace data, returning a sequence of floating point numbers."""
vna.send_command(b":CALC1:PAR1:DEF S12\n")
time.sleep(SLEEP_TIME)
self.vna_socket.send(b":CALC1:DATA:FDAT?\n")
s12_data = b""
while (s12_data[len(s12_data) - 1:] != b"\n"):
    s12_data += self.vna_socket.recv(1024)
s12_data = s12_data[:len(s12_data) - 1].split(b",")
s12_data = s12_data[::2]
s12_data = [float(i) for i in s12_data]
return(s12_data)











signal_gen.send("SYST:COMM:LAN:IPAD?\n")
temp=0
temp = signal_gen.recv(1024)


signal_gen.send("SOURCE1:FREQUENCY 1000\n")
temp=0
temp = signal_gen.recv(1024)


signal_gen.send("*IDN?\n")
temp = signal_gen.recv(1024)

signal_gen.send("SYST:VERS?\n")
temp = signal_gen.recv(1024)



signal_gen.send("SOURCE1:VOLT 1\n")
signal_gen.send("SOURCE1:VOLT:OFFSET 0\n")
signal_gen.send("OUTPUT1:LOAD 50")



 'Send commands to set the desired configuration
.WriteString "SOURCE1:FUNCTION SIN"
.WriteString "SOURCE1:FREQUENCY 1000"
.WriteString "SOURCE1:VOLT:UNIT VPP"
.WriteString "SOURCE1:VOLT 2"
.WriteString "SOURCE1:VOLT:OFFSET 0"
.WriteString "OUTPUT1:LOAD 50"







SYST:COMM:LAN:IPAD?


SYST:VERS?
signal_gen.send("VOLT:VPP\n")
VOLTage {<amplitude>|MINimum|MAXimum}




#signal_gen.send(b"[SOUR1:]VOLT:OFFS{3}")
signal_gen.send(b"OUTP1:LOAD{50}\n")
signal_gen.close()

*IDN?


OUTPut[1|2]:LOAD {<ohms>|INFinity|MINimum|MAXimum}
[SOURce[1|2]:]VOLTage:OFFSet{<offset>|MINimum|MAXimum}
VOLTage:UNIT {VPP|VRMS|DBM}



def set_power(self, power):
self.vna_socket.send(b":SOUR1:POW:GPP " + str(power) + b"\n")
return

OUTPut[1|2]:LOAD {<ohms>|INFinity|MINimum|MAXimum}
VOLTage:UNIT {VPP|VRMS|DBM}
[SOURce[1|2]:]VOLTage:OFFSet{<offset>|MINimum|MAXimum}




self.vna_socket.send(b":CALC1:MARK" + str(marker) + ":Y?\n")
ans=vna.get_answer()
index = ans.find(',')
ans = ans[:index].strip()
return(ans)






#set attenuators
import socket
import struct
ip="10.0.18.59"
value=30
board_address = ((ip, 6791))
board_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
board_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
board_socket.settimeout(5.0)
board_socket.connect(board_address)
board_socket.send(bytearray.fromhex("20 00 09 01") + struct.pack("<d", value))
temp = board_socket.recv(1024)
board_socket.close()


#set RF switches
import socket
import struct














ip="10.0.18.59"
mode=2
board_address = ((ip, 6791))
board_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
board_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
board_socket.settimeout(5.0)
board_socket.connect(board_address)
board_socket.send(bytearray.fromhex("20 00 02 00 0" + str(mode)))
temp = board_socket.recv(1024)
print resp
board_socket.close()

#test script
rffe=RFFEControllerBoard(metadata_param['ip_rffe'])
att=20
rffe.set_attenuator_value(str(att))
rffe.close_connection()





board_address = ((ip, 6791))
self.board_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
self.board_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
self.board_socket.settimeout(5.0)
self.board_socket.connect(board_address)
resp=self.board_socket.send(bytearray.fromhex("20 00 09 01") + struct.pack("<d", value))
temp = self.board_socket.recv(1024)
