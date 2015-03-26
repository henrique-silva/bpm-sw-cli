import socket
import sys
from time import sleep
from rffe_test_lib import RFFEControllerBoard
from binascii import hexlify
from numpy import arange
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('rffe', help='rffe ip (final part)')
parser.add_argument('-a', '--att', type=float, help='rffe ip (final part)')
args = parser.parse_args()

RFFE_CONTROLLER_BOARD_IP = '10.2.117.'+str(args.rffe)
try:
    rffe = RFFEControllerBoard(RFFE_CONTROLLER_BOARD_IP)
except (socket.error):
    sys.stdout.write("Unable to reach the RF front-end controller board with the IP: "+ RFFE_CONTROLLER_BOARD_IP +" through the network. ")

if args.att:
    rffe.set_attenuator_value(args.att)
read_att = rffe.get_attenuator_value()
print (str(read_att))

#~ 
#~ while True:
    #~ for sw in sw_sweep:
            #~ rffe.set_switching_mode(sw)
            #~ read_sw = rffe.get_switching_mode()
            #~ if not int(hexlify(str(read_sw))) == sw:
                #~ print ("Board "+RFFE_CONTROLLER_BOARD_IP+" failed in switch test! "+
                #~ "It should return sw = "+str(sw)+" but got sw = "+read_sw)
            #~ sleep(1)
#~ 
