#!/usr/bin/python

import os
import sys
import time
from time import sleep
from TH2E import TH2E
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('output', help='output file where the readings will be written')
parser.add_argument('delay', type=float, help='time between the readings in seconds', default=10)
parser.add_argument('-i','--ip', help='set sensor ip', default='10.2.117.254')
args = parser.parse_args()

sensor = TH2E(args.ip)
abspath = os.path.abspath(args.output)
if os.path.isfile(abspath):
    f = open(abspath+'/', 'a')
else:
    f = open(abspath+'/th2e_readings.txt', 'w')
    f.write('Time\tTemperature\tHumidity\tDew Point\n')

last_read_time = time.time()
print('\n\tThe following sensors are being monitored, press ctrl-c to stop...')
print('Time\tTemperature\tHumidity\tDew Point')
while True:
    resp = sensor.read_all()
    if len(read) == 3:
        temp, hum, dew = resp
        print('\r'+str(last_read_time)+'\t'+str(temp)+'\t'+str(hum)+'\t'+str(dew)),
        with open(abspath+'/th2e_readings.txt', 'a') as f:
            f.write(str(last_read_time)+'\t'+str(temp)+'\t'+str(hum)+'\t'+str(dew)+'\n')
        sys.stdout.flush()
        try:
            while time.time() - last_read_time < args.delay:
                sleep(1)
        except KeyboardInterrupt:
            f.close()
            break

        last_read_time = time.time()
