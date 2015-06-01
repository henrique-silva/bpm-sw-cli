#!/usr/local/bin/python3

import sys
import os
import time
import argparse
from time import sleep, strftime
import threading
from threading import Thread
sys.path.append('../../th2e/')
from TH2E import TH2E
from run_single import run_single

class TemperatureThread(Thread):
    def __init__ (self,delay, output_path, socket):
        Thread.__init__(self)
        self.delay = delay
        self.output_path = output_path
        self.th2e_socket = socket
        print ('Starting Temperature Thread!')

    def run(self):
        while(1):
            temp=hum=dew=0
            sync.wait()
            temp_time = sync_time
            try:
                temp, hum, dew = self.th2e_socket.read_all()
            except:
                while time.time() - temp_time < self.delay:
                    continue
                continue
            abspath = os.path.abspath(self.output_path)
            abspath = abspath+'/temp_log.txt'
            if not os.path.isfile(abspath):
                with open(abspath, 'w') as f:
                    f.write('Time\tTemperature\tHumidity\tDew Point\n')
            with open(abspath, 'a') as f:
                f.write(str(temp_time)+'\t'+str(temp)+'\t'+str(hum)+'\t'+str(dew)+'\n')
            while time.time() - temp_time < self.delay:
                continue

class OnDemandThread(Thread):
    def __init__ (self, delay, args):
        Thread.__init__(self)
        self.delay = delay
        self.args = args
        print ('Starting On Demand Data Thread!')

    def run(self):
        while(1):
            sync.wait()
            ondemand_time = sync_time
            try:
                run_single(self.args)
            except:
                print('Error while running the On Demand acquisition!')
                raise
            while time.time() - ondemand_time < self.delay:
                continue

class MonitThread(Thread):
    def __init__ (self, delay, args):
        Thread.__init__(self)
        self.delay = delay
        self.args = args

    def run(self):
        while(1):
            sync.wait()
            monit_time = sync_time
            #print ('Monit starting at '+str(monit_time)+'! ')
            try:
                run_single(self.args)
            except:
                print('Error while running the Monitoring acquisition!')
            while time.time() - monit_time < self.delay:
                continue

class TimeThread(Thread):
    def __init__ (self, tick):
        Thread.__init__(self)
        self.tick = tick

    def run(self):
        global sync_time
        sync.clear()
        while(1):
            sync_time = time.time()
            sync.set()
            sync.clear()
            while time.time() - sync_time < self.tick:
                continue

parser = argparse.ArgumentParser()
parser.add_argument('metadata', help='metadata file path')
parser.add_argument('output', help='folder where the output data will be saved')
parser.add_argument('-e','--endpoint', help='broker endpoint', default='tcp://10.2.117.47:9999')
parser.add_argument('-r','--rffeconfig', action='store_true', help='enable the rffe configuration process', default=False)
parser.add_argument('-c','--fmcconfig', action='store_true', help='enable the FMC configuration process', default=False)
parser.add_argument('-a','--allboards', action='store_true', help='run the script for all boards and bpms', default=False)
parser.add_argument('-g','--group', help='specify board and bpm number in the format -> [BOARD, BPM, BPM]', action='append', type=str)
parser.add_argument('-m','--monitdelay', help='interval between monitoring acquisitions (in seconds)', type=float, default=0.5)
parser.add_argument('-t','--tempdelay', help='interval between temperature acquisitions (in seconds)', type=float, default=60)
parser.add_argument('-d','--ondemanddelay', help='interval between on demand acquisitions (in seconds)', type=float, default=1800)
args = parser.parse_args()

burst_group = []
if args.group:
    burst_group.extend(args.group)

single_args = [args.metadata, args.output, '-e' ,args.endpoint, '-s'] 
if args.rffeconfig:
    single_args.extend(['-r'])
if args.fmcconfig:
    single_args.extend(['-c'])
if args.allboards:
    single_args.extend(['-a'])
else:
    for group in burst_group:
        single_args.extend(['-g', group])

ondemand_args = single_args
ondemand_args.extend(['-p', 'fofbamp', '-p', 'tbtamp', '-p', 'adc'])

monit_args = single_args
monit_args.extend(['-p', 'monitamp'])

try:
   socket = TH2E('10.2.117.254')
except:
   raise

#Threads Config
Temp_th = TemperatureThread(args.tempdelay, args.output)
Temp_th.daemon = True
Monit_th = MonitThread(args.monitdelay, monit_args)
Monit_th.daemon = True
OnDemand_th = OnDemandThread(args.ondemanddelay, ondemand_args)
OnDemand_th.daemon = True
Time_th = TimeThread(0.1)
Time_th.daemon = True

#Synchronization event
sync = threading.Event()
sync.clear()

#Threads Start
Time_th.start()
sleep(1)
Temp_th.start()
OnDemand_th.start()
Monit_th.start()

try:  
    while (1):
        pass
except KeyboardInterrupt:
    print('Ctrl-C received! Closing sensor socket!')
    socket.close()
    sys.exit()
