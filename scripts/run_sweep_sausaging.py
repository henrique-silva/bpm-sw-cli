#!/usr/bin/python3

def run_sweep_sausaging(argv):
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
    parser.add_argument('-i','--start', help='sweep initial phase', type=int,default=20)
    parser.add_argument('-n','--stop', help='sweep final phase', type=int, default=60)
    parser.add_argument('-t','--step', help='sweep power phase', type=int, default=1)
    args = parser.parse_args(argv)

    exp = bpm_experiment.BPMExperiment(args.endpoint)
    sensor = TH2E('10.0.18.210')

    if not args.board:
        args.board = '0'
    if not args.bpm:
        args.bpm = '0'

    if args.allboards:
        board = ['0','1','2','3','4','5']
        bpm = ['0','1']
    else:
        board = args.board
        bpm = args.bpm

    dsp_sausaging_sweep = ['off', 'on']
    dsp_deswitching_phase_sweep = range(args.start,args.stop,args.step)

    while True:
        exp.load_from_metadata(args.metadata)
        exp.metadata['rffe_switching'] = 'on'

        temp, hum, dew = sensor.read_all()
        exp.metadata['rack_temperature'] = str(temp)+' C'
        exp.metadata['rack_humidity'] = str(hum)+' %'
        exp.metadata['rack_dew_point'] = str(dew)+' C'

        print('\n====================')
        print('EXPERIMENT SETTINGS:')
        print('====================')
        print(''.join(sorted(exp.get_metadata_lines())))

        if not args.silent:
            input_text = input('Press ENTER to run the experiment. \nType \'l\' and press ENTER to load new experiment settings from \'' + os.path.abspath(args.metadata) + '\'.\nType \'q\' and press ENTER to quit.\n')
        else:
            input_text = ''

        if not input_text:

            # Find the number of attenuators on the RFFE
            att_items = exp.metadata['rffe_attenuators'].split(',')
            natt = len(att_items)

            nexp = 1
            for board_nmb in board:
                for bpm_nmb in bpm:
                    print('\n        Using Board '+str(board_nmb)+ ' and BPM '+str(bpm_nmb)+'...')
                    # Sweep sausaging (sausaging on or off)
                    for dsp_sausaging in dsp_sausaging_sweep:
                        exp.metadata['dsp_sausaging'] = dsp_sausaging

                        # Sweep deswitching phase
                        for deswitching_value_set in dsp_deswitching_phase_sweep:
                            # Write deswitching values to metadata
                            exp.metadata['dsp_deswitching_phase'] = str(deswitching_value_set);

                            # Assure that no file or folder will be overwritten
                            ntries = 1;
                            while True:
                                data_filenames = []
                                for datapath in args.datapath:
                                    data_filenames.append(os.path.join(os.path.normpath(args.output), 'sausaging_' + exp.metadata['dsp_sausaging'], datapath, 'data_' + str(ntries) + '_' + datapath + '.txt'))

                                ntries = ntries+1

                                if all(not os.path.exists(data_filename) for data_filename in data_filenames):
                                    break

                            print(str.rjust('Run #' + str(nexp), 12) + ': Sausaging ' + exp.metadata['dsp_sausaging'] + '; Deswitching phase: ' + exp.metadata['dsp_deswitching_phase'] + ' ')
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
                                    continue
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
    run_sweep_sausaging(sys.argv[1:])
