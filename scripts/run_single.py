#!/usr/local/bin/python3

def run_single(argv):
    import sys
    import os
    import argparse
    import bpm_experiment
    sys.path.append('../th2e/')
    from TH2E import TH2E
    from time import strftime

    parser = argparse.ArgumentParser()
    parser.add_argument('metadata', help='metadata file path')
    parser.add_argument('output', help='folder where the output data will be saved')
    parser.add_argument('-p','--datapath', help='choose the acquisition datapath (adc, tbt, fofb)', action='append', required=True)
    parser.add_argument('-e','--endpoint', help='broker endpoint', default='tcp://10.0.18.39:8888')
    parser.add_argument('-d','--board', type=int, help='select the target board for the test', action='append')
    parser.add_argument('-b','--bpm', type=int, choices=[0,1], help='select the target bpm for the test', action='append')
    parser.add_argument('-s','--silent', action='store_true', help='run the script without asking for confirmation', default=False)
    parser.add_argument('-r','--rffeconfig', action='store_true', help='enable the rffe configuration process', default=False)
    parser.add_argument('-a','--allboards', action='store_true', help='run the script for all boards and bpms', default=False)
    parser.add_argument('-t','--temperature', action='store_true', help='enable rack temperature reading', default=False)
    parser.add_argument('-c','--fmcconfig', action='store_true', help='perform only the acquisition, not configuring the FMC board', default=False)
    args = parser.parse_args(argv)

    exp = bpm_experiment.BPMExperiment(args.endpoint)
    sensor = TH2E('10.2.117.254')

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

    while True:
        exp.load_from_metadata(args.metadata)
        print('\n====================')
        print('EXPERIMENT SETTINGS:')
        print('====================')

        if args.temperature:
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
            for board_number in board:
                for bpm_number in bpm:
                    # Assure that no file or folder will be overwritten
                    ntries = 1;
                    date = strftime('%d-%m-%Y')
                    board_path = 'board'+str(board_number)
                    bpm_path = 'bpm'+str(bpm_number)

                    #Replace the dot and space in power level string with an underline to avoid problems when creating the folder
                    power_level = exp.metadata['rffe_signal_carrier_inputpower'].replace(".","_")
                    power_level = power_level.replace(" ","_")

                    print('\n        Using Board '+str(board_number)+ ' and BPM '+str(bpm_number)+'...')
                    while True:
                        data_filenames = []
                        for datapath in args.datapath:
                            if exp.metadata['signal_source'] == 'signalgenerator':
                                data_filenames.append(os.path.join(os.path.normpath(args.output), date, board_path, bpm_path, power_level, datapath, 'data_' + str(ntries) + '_' + datapath + '.txt'))
                            else:
                                data_filenames.append(os.path.join(os.path.normpath(args.output), date, board_path, bpm_path, datapath, 'data_' + str(ntries) + '_' + datapath + '.txt'))
                        ntries = ntries+1
                        if all(not os.path.exists(data_filename) for data_filename in data_filenames):
                            break
                    for i in range(0,len(data_filenames)):
                        print('        Running ' + args.datapath[i] + ' datapath...')
                        sys.stdout.flush()
                        try:
                            exp.run(data_filenames[i], args.datapath[i], str(board_number), str(bpm_number), args.fmcconfig, args.rffeconfig)
                        except bpm_experiment.OverPowerError as e:
                            print ('The power level '+str(e.value)+' will damage the RFFE so it\'ll be skipped!')
                            continue
                        except bpm_experiment.BoardTimeout:
                            print ('This Board doesn\'t respond and will be skipped!')
                            continue
                        except bpm_experiment.RFFETimeout:
                            print ('RFFE board doesn\'t respond!')
                            continue
                        else:
                            print(' done. Results in: ' + data_filenames[i])
            break

        elif input_text == 'q':
            break

if __name__ == "__main__":
    import sys
    run_single(sys.argv[1:])
