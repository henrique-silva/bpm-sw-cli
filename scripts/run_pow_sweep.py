#!/usr/bin/python3

def run_pow_sweep(argv):
    import sys
    import os
    import argparse
    from time import strftime
    from run_single import run_single
    from bpm_experiment import BPMExperiment
    from RS_SMB100A import RS_gen
    
    parser = argparse.ArgumentParser()
    parser.add_argument('metadata', help='metadata file path')
    parser.add_argument('output', help='folder where the output data will be saved')
    parser.add_argument('start', help='sweep initial power', type=int,default=-60)
    parser.add_argument('stop', help='sweep final power', type=int, default=0)
    parser.add_argument('step', help='sweep power step', type=int, default=10)
    parser.add_argument('-g','--genip', help='generator ip address', default='10.0.17.44')
    parser.add_argument('-e','--endpoint', help='broker endpoint', default='tcp://10.0.18.39:8888')
    parser.add_argument('-d','--board', type=int, help='select the target board for the test', action='append')
    parser.add_argument('-b','--bpm', type=int, choices=[0,1], help='select the target bpm for the test', action='append')
    parser.add_argument('-r','--rffeconfig', action='store_true', help='enable the rffe configuration process', default=False)
    parser.add_argument('-a','--allboards', action='store_true', help='run the script for all boards and bpms', default=False)
    parser.add_argument('-f','--frequency', type=float, help='set generator frequency', default=477999596)
    args = parser.parse_args(argv)

    exp = BPMExperiment(args.endpoint)

    if not args.board:
        args.board = '0'
    if not args.bpm:
        args.bpm = '0'

    #Configure the RF Generator
    gen = RS_gen(args.genip)
    gen.set_freq(args.frequency)

    loss = exp.metada['signal_power_loss'].split()[0]

    for Pout in range(args.start,args.stop,args.step):
        gen.rf_on()
        Pout = Pout + loss
        print('\n\n\n======================================================')
        print('New test initiated at ' + strftime('%Y-%m-%d %H:%M:%S'))
        print('======================================================')

        gen.set_pow(Pout)
        print('Current Power (RFFE input) = '+str(Pout-loss)+' dBm')

        #Use a temporary metadata to pass the input power to the called functions
        exp.load_from_metadata(args.metadata)
        exp.metadata['rffe_signal_carrier_inputpower'] = str(Pout-loss) + ' dBm'
        with open(args.metadata+'.temp','w') as temp:
            temp.writelines(''.join(sorted(exp.get_metadata_lines())))
            temp.append('circuit_power_loss = '+str(loss)+' dB')
            temp_path = os.path.abspath(temp.name)

        single_args = [temp_path, args.output, '-e' ,args.endpoint, '-p', 'fofb', '-s']
        if args.rffeconfig:
            single_args.extend(['-r'])
        if args.allboards:
            single_args.extend(['-a'])
        else:
            for board_nmb in args.board:
                for bpm_nmb in args.bpm:
                    single_args.extend(['-d', str(board_nmb),'-b', str(bpm_nmb)])
        run_single(single_args)
        os.remove(temp_path)

    gen.set_pow(-80)
    gen.rf_off()

if __name__ == "__main__":
    import sys
    run_pow_sweep(sys.argv[1:])
