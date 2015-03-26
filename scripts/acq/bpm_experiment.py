import os
from os.path import basename
from time import time
import hashlib
from time import strftime, gmtime
from time import sleep
from math import floor
import subprocess

from metadata_parser import MetadataParser

class BPMExperiment():

    def __init__(self, broker_endpoint = 'ipc:///tmp/bpm', binpath = '../client', debug = False):
        self.broker_endpoint = broker_endpoint
        self.debug = debug
        self.metadata_parser = MetadataParser()
        if not os.path.isfile(binpath):
            raise FileNotFoundError("\n\tBPM-SW Command Line Interface not found!")
        else:
            self.binpath = binpath

    def load_from_metadata(self, input_metadata_filename):
        # Parse metadata file into a dictionary
        self.metadata_parser.parse(input_metadata_filename)
        self.metadata = self.metadata_parser.options

    def get_metadata_lines(self):
        experiment_parameters = list(self.metadata.keys())
        lines = []
        for key in experiment_parameters:
            lines.append(key + ' = ' + self.metadata[key] + '\n')
        return lines

    def run(self, data_filename, datapath, board, bpm, fmc_config=False, rffe_config=False):

        acq = {'adc': {'chan': '0', 'samples': '1000000'}, 
            'adcswap': {'chan': '1', 'samples': '1000000'},
            'mixiq120':{'chan': '2', 'samples': '1000000'},
            'mixiq340':{'chan': '3', 'samples': '1000000'},
            'tbtdecimiq120':{'chan': '4', 'samples': '1000000'},
            'tbtdecimiq340':{'chan': '5', 'samples': '1000000'},
            'tbtamp':{'chan': '6', 'samples': '1000000'},
            'tbtpha':{'chan': '7', 'samples': '1000000'},
            'tbtpos':{'chan': '8', 'samples': '1000000'},
            'fofbdecimiq120':{'chan': '9', 'samples': '1000000'},
            'fofbdecimiq340':{'chan': '10', 'samples': '1000000'},
            'fofbamp':{'chan': '11', 'samples': '1000000'},
            'fofbpha':{'chan': '12', 'samples': '1000000'},
            'fofbpos':{'chan': '13', 'samples': '1000000'},
            'monitamp':{'chan': '14', 'samples': '1000000'},
            'monitpos':{'chan': '15', 'samples': '1000000'},
            'monit1pos':{'chan': '16', 'samples': '1000000'}}

        rffe_switching_frequency_ratio = str(int(self.metadata['rffe_switching_frequency_ratio'].split()[0])/2)
        deswitching_phase_offset = str(int(self.metadata['dsp_deswitching_phase'].split()[0]) - int(self.metadata['rffe_switching_phase'].split()[0]))

        import subprocess

        if fmc_config:
            # Run FPGA configuration commands
            command_argument_list = [self.binpath]
            command_argument_list.extend(['--board', board])
            command_argument_list.extend(['--bpm', bpm])
            command_argument_list.extend(['--setdivclk', rffe_switching_frequency_ratio])
            command_argument_list.extend(['--setswdly', deswitching_phase_offset])
            command_argument_list.extend(['--setgainaa', self.metadata['gain_aa'].split()[0]])
            command_argument_list.extend(['--setgainac', self.metadata['gain_ac'].split()[0]])
            command_argument_list.extend(['--setgaincc', self.metadata['gain_cc'].split()[0]])
            command_argument_list.extend(['--setgainca', self.metadata['gain_ca'].split()[0]])
            command_argument_list.extend(['--setgainbb', self.metadata['gain_bb'].split()[0]])
            command_argument_list.extend(['--setgainbd', self.metadata['gain_bd'].split()[0]])
            command_argument_list.extend(['--setgaindd', self.metadata['gain_dd'].split()[0]])
            command_argument_list.extend(['--setgaindb', self.metadata['gain_db'].split()[0]])
            command_argument_list.extend(['--endpoint', self.broker_endpoint])

            if self.metadata['bpm_Kx']:
                command_argument_list.extend(['--setkx', self.metadata['bpm_Kx'].split()[0]])

            if self.metadata['bpm_Ky']:
                command_argument_list.extend(['--setky', self.metadata['bpm_Ky'].split()[0]])

            if self.metadata['dsp_sausaging'].split()[0] == 'on':
                dsp_sausaging = '1'
            else:
                dsp_sausaging = '0'
            command_argument_list.extend(['--setwdwen', dsp_sausaging])

            if not self.debug:
                #Use timeout here to identify if the board is responsive
                try:
                    subprocess.call(command_argument_list, timeout=5)
                except subprocess.TimeoutExpired:
                #If the board doesn't respond, abort the call
                    raise BoardTimeout
            else:
                print(' '.join(command_argument_list))

            if rffe_config:
                # Run RFFE configuration commands
                command_argument_list = [self.binpath]
                command_argument_list.extend(['--board', board])
                command_argument_list.extend(['--bpm', bpm])
                command_argument_list.extend(['--endpoint', self.broker_endpoint])
                command_argument_list.extend(['--rffesetsw', self.metadata['rffe_switching'].split()[0]])
    
                if self.metadata['signal_source'].split()[0] == 'signalgenerator':
                    att_items = self.metadata['rffe_attenuators'].split(',')
                    natt = len(att_items)
                    rffe_gain = float(self.metadata['rffe_gain'].split()[0])
                    rffe_input_power = float(self.metadata['rffe_signal_carrier_inputpower'].split()[0])
                    rffe_power_threshold = float(self.metadata['rffe_power_threshold'].split()[0])
                    i = 1
                    for att_value in att_items:
                        att_value = float(att_value.strip()[0])
                        power_level = rffe_input_power + rffe_gain - att_value
                        if power_level > rffe_power_threshold:
                            raise OverPowerError(power_level)
                        command_argument_list.extend(['--rffesetatt', 'chan=' + str(i) + ',value=' + str(att_value)])
                        i = i+1
    
                if not self.debug:
                #Use timeout here to identify if the RFFE is responsive
                    try:
                        subprocess.call(command_argument_list, timeout=5)
                        sleep(0.2) # FIXME: it seems RFFE controller (mbed) doesn't realize the connection has been closed
                    except subprocess.TimeoutExpired:
                    #If the RFFE doesn't respond, abort the call
                        raise RFFETimeout
                else:
                    print(' '.join(command_argument_list))
    
                # Read RFFE temperature
                command_argument_list = [self.binpath]
                command_argument_list.extend(['--board', board])
                command_argument_list.extend(['--bpm', bpm])
                command_argument_list.extend(['--endpoint', self.broker_endpoint])
    
                rffe_temp = [0] * 4
                for chan in range(1,5):
                    command_argument_list.extend(['--rffegettemp', '-chan='+str(chan)])
                    if not self.debug:
                        try:
                            subprocess.call(command_argument_list, timeout=5)
                            sleep(0.2) # FIXME: it seems RFFE controller (mbed) doesn't realize the connection has been closed
                        except subprocess.TimeoutExpired:
                            raise RFFETimeout
                    else:
                        print(' '.join(command_argument_list))

            # TODO: Check if everything was properly set

            # Configure Switching options
            command_argument_list = [self.binpath]
            command_argument_list.extend(['--board', board])
            command_argument_list.extend(['--bpm', bpm])
            command_argument_list.extend(['--endpoint', self.broker_endpoint])

            if self.metadata['rffe_switching'].split()[0] == 'on':
                rffe_switching = '1'
                command_argument_list.extend(['--setsw', '3'])
            else:
                rffe_switching = '0'
                command_argument_list.extend(['--setsw', '1'])

            if not self.debug:
                subprocess.call(command_argument_list)
            else:
                print(' '.join(command_argument_list))

            #Enable switching signal
            command_argument_list = [self.binpath]
            command_argument_list.extend(['--board', board])
            command_argument_list.extend(['--bpm', bpm])
            command_argument_list.extend(['--endpoint', self.broker_endpoint])
            command_argument_list.extend(['--setswen', self.metadata['rffe_switching'].split()[0]])
            if not self.debug:
                subprocess.call(command_argument_list)
            else:
                print(' '.join(command_argument_list))

        # Timestamp the start of data acquisition
        # FIXME: timestamp should ideally come together with data.
        t = time()

        # Run acquisition
        # Get the result of data acquisition and write it to data file
        command_argument_list = [self.binpath]
        command_argument_list.extend(['--board', board])
        command_argument_list.extend(['--bpm', bpm])
        command_argument_list.extend(['--setsamples', acq[datapath]['samples']])
        command_argument_list.extend(['--setchan', acq[datapath]['chan']])
        #TODO: Check if 15 seconds is enough time to the FOFB module finish its acquisition even with higher samples number
        command_argument_list.extend(['--timeout', '15'])
        command_argument_list.extend(['--fullacq'])
        command_argument_list.extend(['--endpoint', self.broker_endpoint])

        # Ensure file path exists
        path = os.path.dirname(data_filename)
        try:
            os.makedirs(path)
        except OSError as exception:
            if not os.path.isdir(path):
                raise

        with open(data_filename, 'x') as f:
            if not self.debug:
                p = subprocess.call(command_argument_list, stdout=f)
            else:
                f.writelines(['10 11 -9 80\n54 5 6 98\n']);
                print(' '.join(command_argument_list))

        # Compute data file signature
        with open(data_filename, 'r') as f:
            text = f.read()

        if self.metadata['data_signature_method'].split()[0] == 'md5':
            md = hashlib.md5()
        elif self.metadata['data_signature_method'].split()[0] == 'sha-1':
            md = hashlib.sha1()
        elif self.metadata['data_signature_method'].split()[0] == 'sha-256':
            md = hashlib.sha256()
        md.update(text.encode(f.encoding))
        filesignature = md.hexdigest()

        # Format date and hour as an standard UTC timestamp (ISO 8601)
        ns = int(floor((t * 1e9) % 1e9))
        timestamp_start = '%s.%09dZ' % (strftime('%Y-%m-%dT%H:%M:%S', gmtime(t)), ns)

        # Throw away absolute path of data filename
        data_filename_basename = os.path.basename(data_filename)

        # Build metadata file based on template metadata file and post-processed metadata
        config_base_metadata_lines = self.get_metadata_lines()

        config_automatic_lines = [];
        config_automatic_lines.append('data_original_filename = ' + data_filename_basename + '\n')
        config_automatic_lines.append('data_signature = ' + filesignature + '\n')
        #config_automatic_lines.append('dsp_data_rate_decimation_ratio = ' + data_rate_decimation_ratio + '\n')
        config_automatic_lines.append('timestamp_start = ' + timestamp_start + '\n')
        #config_automatic_lines.append('data_file_structure = ' + data_file_structure + '\n')
        config_automatic_lines.append('data_file_format = ascii\n')
        if rffe_config:
            config_automatic_lines.append('rffe_board_temperature = '+rffe_temp[0]+' C, '+rffe_temp[1]+' C, '+rffe_temp[2]+' C, '+rffe_temp[3]+'\n')

        config_fromfile_lines = []
        config_fromfile_lines.extend(config_base_metadata_lines)
        config_fromfile_lines.extend(config_automatic_lines)

        # Metadata file is placed in the same path and with the same filename as the data file, but with .metadata extension
        output_metadata_filename = os.path.splitext(data_filename)[0] + '.metadata'

        with open(output_metadata_filename, 'x') as f:
            f.writelines(sorted(config_fromfile_lines))

class BPMError(Exception):
    pass

class OverPowerError(BPMError):
    def __init__(self,value):
        self.value = value

class BoardTimeout(BPMError):
    pass

class RFFETimeout(BPMError):
    pass
