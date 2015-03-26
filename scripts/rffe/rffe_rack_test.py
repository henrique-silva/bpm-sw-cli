import socket
import sys
from time import sleep
from rffe_test_lib import RFFEControllerBoard
from binascii import hexlify
from numpy import arange

sw_sweep = [0,1,2,3]
attenuation_values = arange(0,32,0.5)

for rffe_numb in range(33,45,1):
    RFFE_CONTROLLER_BOARD_IP = '10.2.117.'+str(rffe_numb)
    try:
        rffe = RFFEControllerBoard(RFFE_CONTROLLER_BOARD_IP)
    except (socket.error):
        sys.stdout.write("Unable to reach the RF front-end controller board with the IP: "+ RFFE_CONTROLLER_BOARD_IP +" through the network. " +
                        "Skipping it...\n")
        continue

    #Attenuators test
    for att in attenuation_values:
        rffe.set_attenuator_value(att)
        read_att = rffe.get_attenuator_value()
        if not read_att == att:
            print ("Board "+RFFE_CONTROLLER_BOARD_IP+" failed in attenuator test! "+
            "It should return att = "+str(att)+" but got att = "+read_att)
    print ("Board "+RFFE_CONTROLLER_BOARD_IP+" passed attenuator test! ")

    #Temperature reading test
    tmp1 = rffe.get_temp1()
    tmp2 = rffe.get_temp2()
    print ("Temperature -> 1: "+str(tmp1)+", 2: "+str(tmp2))

    #Test Reset
    #rffe.reset()

    #Close connection
    rffe.close_connection()
