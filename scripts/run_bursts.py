#!/usr/bin/python3

import sys
import time
from time import sleep, strftime
import argparse
from run_single import run_single
from run_pow_sweep import run_pow_sweep
from bpm_experiment import BPMExperiment

parser = argparse.ArgumentParser()
parser.add_argument('metadata', help='metadata file path')
parser.add_argument('datapath', help='folder where the output data will be saved')
parser.add_argument('-e','--endpoint', help='broker endpoint', default='tcp://10.0.18.39:8888')
parser.add_argument('-d','--board', type=int, help='select the target board for the test', action='append')
parser.add_argument('-b','--bpm', type=int, choices=[0,1], help='select the target bpm for the test', action='append')
parser.add_argument('-r','--rffeconfig', action='store_true', help='enable the rffe configuration process', default=False)
parser.add_argument('-a','--allboards', action='store_true', help='run the script for all boards and bpms', default=False)
parser.add_argument('-m','--minutes', type=float, help='amount of minutes between each test', default=1)
parser.add_argument('-t','--runtype', help='desired type of test', default='single', choices=['single','pow_sweep'])
parser.add_argument('-i','--start', help='sweep initial power', type=int,default=-60)
parser.add_argument('-f','--stop', help='sweep final power', type=int, default=0)
parser.add_argument('-s','--step', help='sweep power step', type=int, default=10)
args = parser.parse_args()

if not args.board:
    args.board = '0'
if not args.bpm:
    args.bpm = '0'

last_experiment_time = time.time()

while True:
    print('\n\n\n======================================================')
    print('New experiment burst. Initiated at ' + strftime('%Y-%m-%d %H:%M:%S'))
    print('======================================================')

    if args.runtype == 'single':
        single_args = [args.metadata, args.datapath, '-e' ,args.endpoint, '-s']
        if args.allboards:
            single_args.extend(['-a'])
        else:
            single_args.extend(['-d', str(args.board),'-b', str(args.bpm)])
        if args.rffeconfig:
            single_args.extend(['-r'])
        run_single(single_args)

    elif args.runtype == 'pow_sweep':
        if not (args.start and args.stop and args.step):
            print ("Power sweep arguments not provided! Aborting operation...")
            break
        pow_sweep_args = [args.metadata, args.datapath, str(args.start), str(args.stop), str(args.step), '-e' ,args.endpoint]
        if args.allboards:
            pow_sweep_args.extend(['-a'])
        else:
            pow_sweep_args.extend(['-d', str(args.board),'-b', str(args.bpm)])
        if args.rffeconfig:
            pow_sweep_args.extend(['-r'])
        run_pow_sweep(pow_sweep_args)

    else:
        print('Unknown experiment type: '+args.runtype)
        break

    try:
        print('Waiting for next experiment burst... (press ctrl-c to stop)')

        while time.time() - last_experiment_time < args.minutes*60:
            sleep(1)

        last_experiment_time = time.time()

    except KeyboardInterrupt:
        print('\nThe bursts experiment has ended.\n')
        break

    except:
        raise