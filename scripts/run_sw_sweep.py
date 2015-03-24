#!/usr/local/bin/python3

def run_sweep(argv):
    import sys
    import os
    import itertools
    import argparse
    sys.path.append('../th2e/')
    from TH2E import TH2E
    import bpm_experiment

    parser = argparse.ArgumentParser()
    parser.add_argument('metadata', help='metadata file path')
    parser.add_argument('output', help='folder where the output data will be saved')
    parser.add_argument('-e','--endpoint', help='broker endpoint', default='tcp://10.0.18.39:8888')
    parser.add_argument('-d','--board', type=int, help='select the target board for the test', action='append')
    parser.add_argument('-b','--bpm', type=int, choices=[0,1], help='select the target bpm for the test', action='append')
    parser.add_argument('-s','--silent', action='store_true', help='run the script without asking for confirmation', default=False)
    parser.add_argument('-p','--datapath', help='choose the acquisition datapath (adc, tbt, fofb)', action='append', required=True)
    parser.add_argument('-a','--allboards', action='store_true', help='run the script for all boards and bpms', default=False)
    parser.add_argument('-w','--dspsweep', action='store_true', help='sweep the dsp switching', default=False)
    parser.add_argument('-f','--rffesweep', action='store_true', help='sweep the rffe switching', default=False)
    parser.add_argument('-t','--temperature', action='store_true', help='enable rack temperature reading', default=False)

    args = parser.parse_args(argv)

    exp = bpm_experiment.BPMExperiment(args.endpoint)

    if not args.board:
        args.board = '0'
    if not args.bpm:
        args.bpm = '0'

    if args.allboards:
        board = range(0,12)
        bpm = range(0,2)
    else:
        board = args.board
        bpm = args.bpm

    if args.rffesweep:
        rffe_switching_sweep = ['off', 'on']
    else:
        rffe_switching_sweep = ['off']
    
    if args.dspsweep:
        dsp_sausaging_sweep = ['off', 'on']
    else:
        dsp_sausaging_sweep = ['off']

    while True:
        exp.load_from_metadata(args.metadata)
        print('\n====================')
        print('EXPERIMENT SETTINGS:')
        print('====================')

        if args.temperature:
            sensor = TH2E('10.2.117.254')
            temp, hum, dew = sensor.read_all()
            exp.metadata['rack_temperature'] = str(temp)+' C'
            exp.metadata['rack_humidity'] = str(hum)+' %'
            exp.metadata['rack_dew_point'] = str(dew)+' C'
        
        print(''.join(sorted(exp.get_metadata_lines())))

        if not args.silent:
            input_text = input('Press ENTER to run the experiment. \nType \'l\' and press ENTER to load new experiment settings from \'' + os.path.abspath(args.metadata) + '\'.\nType \'q\' and press ENTER to quit.\n')
        else:
            input_text = ''

        if not input_text:
            nexp = 1
            for board_nmb in board:
                for bpm_nmb in bpm:
                    print('\n        Using Board '+str(board_nmb)+ ' and BPM '+str(bpm_nmb)+'...')
                    # Sweep RFFE channels switching (switching on or off)
                    for rffe_switching in rffe_switching_sweep:
                        exp.metadata['rffe_switching'] = rffe_switching
                        # Sweep sausaging (sausaging on or off) when RFFE channels switching is on
                        for dsp_sausaging in dsp_sausaging_sweep:
                            if rffe_switching == 'off' and dsp_sausaging == 'on':
                                break
                            else:
                                exp.metadata['dsp_sausaging'] = dsp_sausaging
                                # Assure that no file or folder will be overwritten
                                ntries = 1;
                                while True:
                                    data_filenames = []
                                    for datapath in args.datapath:
                                        data_filenames.append(os.path.join(os.path.normpath(args.output), 'switching_' + exp.metadata['rffe_switching'] + '_sausaging_' + exp.metadata['dsp_sausaging'], datapath, 'data_' + str(ntries) + '_' + datapath + '.txt'))

                                    ntries = ntries+1
                                    if all(not os.path.exists(data_filename) for data_filename in data_filenames):
                                        break

                                print(str.rjust('Run #' + str(nexp), 12) + ': RFFE switching ' + exp.metadata['rffe_switching'] + '; DSP sausaging ' + exp.metadata['dsp_sausaging'] + ' ')
                                nexp = nexp+1

                                for i in range(0,len(data_filenames)):
                                    print('        Running ' + args.datapath[i] + ' datapath...')
                                    sys.stdout.flush()
                                    try:
                                        exp.run(data_filenames[i], args.datapath[i], str(board_nmb), str(bpm_nmb), True)
                                    except bpm_experiment.OverPowerError as e:
                                        print ('The power level '+str(e.value)+' will damage the RFFE so it\'ll be skipped!')
                                        continue
                                    except bpm_experiment.BoardTimeout:
                                        print ('This Board doesn\'t respond and will be skipped!')
                                        break
                                    except bpm_experiment.RFFETimeout:
                                        print ('RFFE board doesn\'t respond!')
                                        break
                                    else:
                                        print(' done. Results in: ' + data_filenames[i])
                                 print('')
        print('The experiment has run successfully!\n');
            if not args.silent:
                input_text = input('Press ENTER to load a new experiment setting from \'' + os.path.abspath(args.metadata) + '\'.\nType \'q\' and press ENTER to quit.\n')
            else:
                input_text = 'q'

        if input_text == 'q':
            break

if __name__ == "__main__":
    import sys
    run_sweep(sys.argv[1:])
