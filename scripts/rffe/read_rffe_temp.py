#!/usr/bin/python

import os
import sys
import time
from time import sleep
import argparse
import socket
from rffe_test_lib import RFFEControllerBoard

parser = argparse.ArgumentParser()
parser.add_argument('output', help='output file where the readings will be written')
parser.add_argument('delay', type=float, help='time between the readings in seconds', default=10)
args = parser.parse_args()

rffe_range = range(33,45,1)

abspath = os.path.abspath(args.output)
if not os.path.isfile(abspath+'/rffe_temp.txt'):
    with open(abspath+'/rffe_temp.txt', 'w') as f:
        f.write('Timestamp        ')
        for rffe_numb in rffe_range:
            f.write('RFFE'+str(rffe_numb)+'CH1    RFFE'+str(rffe_numb)+'CH2    ')
        f.write('\n')

last_read_time = time.time()
while True:
    format_ts = "{0:.2f}".format(last_read_time)
    with open(abspath+'/rffe_temp.txt', 'a') as f:
        f.write('\n'+str(format_ts))
        for rffe_numb in rffe_range:
            RFFE_CONTROLLER_BOARD_IP = '10.2.117.'+str(rffe_numb)
            try:
                rffe = RFFEControllerBoard(RFFE_CONTROLLER_BOARD_IP)
            except (socket.error):
                sys.stdout.write("Unable to reach the RF front-end controller board with the IP: "+ RFFE_CONTROLLER_BOARD_IP +" through the network. " +
                                "Skipping it...\n")
                continue

            tmp1 = "{0:.6f}".format(rffe.get_temp1())
            tmp2 = "{0:.6f}".format(rffe.get_temp2())

            f.write('    '+str(tmp1)+'    '+str(tmp2))
            print ('RFFE'+str(rffe_numb)+' temp -> CH1 ='+str(tmp1)+' CH2='+str(tmp2))
    try:
        while time.time() - last_read_time < args.delay:
            sleep(1)
    except KeyboardInterrupt:
        f.close()
        break

    last_read_time = time.time()
