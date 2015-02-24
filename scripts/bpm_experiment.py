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

    def __init__(self, broker_endpoint = 'ipc:///tmp/bpm', binpath = './client', debug = False):
        self.broker_endpoint = broker_endpoint
        self.debug = debug
        self.metadata_parser = MetadataParser()
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

    def run(self, data_filename, datapath, board, bpm, rffe_config=True):
        if datapath == 'adc':
            data_rate_decimation_ratio = '1'
            acq_channel = '0'
            acq_npts = '100000'
            data_file_structure = 'bpm_amplitudes_if'
        elif datapath == 'tbt':
            data_rate_decimation_ratio = self.metadata['adc_clock_sampling_harmonic'].split()[0] # FIXME: data_rate_decim_factor should be ideally read from FPGA
            acq_channel = '2'
            acq_npts = '100000'
            data_file_structure = 'bpm_amplitudes_baseband'
        elif datapath == 'fofb':
            data_rate_decimation_ratio = '1000' # FIXME: data_rate_decim_factor should be ideally read from FPGA
            acq_channel = '4'
            acq_npts = '500000'
            data_file_structure = 'bpm_amplitudes_baseband'

        deswitching_phase_offset = str(int(self.metadata['dsp_deswitching_phase'].split()[0]) - int(self.metadata['rffe_switching_phase'].split()[0]))

        # FIXME: should not divide by 2 and subtract 4 to make FPGA counter count right. FPGA must be corrected
        rffe_switching_frequency_ratio = str(int(self.metadata['rffe_switching_frequency_ratio'].split()[0])/2 - 4)

        #Transforms the values 'on' and 'off' into its respectives boolean values 1 and 0
        for item in self.metadata:
            if (self.metadata[item].split()[0] == 'off'):
                self.metadata[item] = '0'
            elif (self.metadata[item].split()[0] == 'on'):
                self.metadata[item] = '1'

        import subprocess

        # Run FPGA configuration commands
        command_argument_list = [self.binpath]
        command_argument_list.extend(['--board', board])
        command_argument_list.extend(['--bpm', bpm])
        command_argument_list.extend(['--setwdwen', self.metadata['dsp_sausaging'].split()[0]])
        command_argument_list.extend(['--setdivclk', rffe_switching_frequency_ratio])
        command_argument_list.extend(['--setkx', self.metadata['bpm_Kx'].split()[0]])
        command_argument_list.extend(['--setky', self.metadata['bpm_Ky'].split()[0]])
        command_argument_list.extend(['--setswdly', deswitching_phase_offset])
        command_argument_list.extend(['--endpoint', self.broker_endpoint])
        command_argument_list.extend(['--setsw', self.metadata['rffe_switching'].split()[0]])
        #command_argument_list.extend(['-v'])

        if not self.debug:
            #Use timeout here to identify if the board is responsive
            try:
                subprocess.call(command_argument_list, timeout=1)
            except subprocess.TimeoutExpired:
            #If the board doesn't respond, abort the call
                print ('Error: Board doesn\'t respond! Aborting routine...')
                return 'Board Timeout'
        else:
            print(' '.join(command_argument_list))

        if rffe_config:
            # Run RFFE configuration commands
            command_argument_list = [self.binpath]
            command_argument_list.extend(['--board', board])
            command_argument_list.extend(['--bpm', bpm])
            command_argument_list.extend(['--endpoint', self.broker_endpoint])
            command_argument_list.extend(['--rffesetsw', self.metadata['rffe_switching'].split()[0]])
            #command_argument_list.extend(['-v'])
            att_items = self.metadata['rffe_attenuators'].split(',')
            i = 1
            for item in att_items:
                item.strip()
                command_argument_list.extend(['--rffesetatt', 'chan=' + str(i) + ',value=' + item.split()[0]])
                i = i+1
            if not self.debug:
            #Use timeout here to identify if the RFFE is responsive
                try:
                    subprocess.call(command_argument_list, timeout=5)
                    sleep(0.2) # FIXME: it seems RFFE controller (mbed) doesn't realize the connection has been closed
                except subprocess.TimeoutExpired:
                #If the RFFE doesn't respond, abort the call
                    print ('Error: RFFE doesn\'t respond! Aborting routine...')
                    return
            else:
                print(' '.join(command_argument_list))

        # TODO: Check if everything was properly set

        # Enable switching signal
        command_argument_list = [self.binpath]
        command_argument_list.extend(['--board', board])
        command_argument_list.extend(['--bpm', bpm])
        command_argument_list.extend(['--endpoint', self.broker_endpoint])
        command_argument_list.extend(['--setswen', self.metadata['rffe_switching'].split()[0]])
        #command_argument_list.extend(['-v'])
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
        command_argument_list.extend(['--setsamples', acq_npts])
        command_argument_list.extend(['--setchan', acq_channel])
        #TODO: See if 10 seconds is enough time to the FOFB module finish its acquisition even with higher samples number
        command_argument_list.extend(['--timeout', '10'])
        command_argument_list.extend(['--fullacq'])
        command_argument_list.extend(['--endpoint', self.broker_endpoint])
        #command_argument_list.extend(['-v'])

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

        # Trhow away absolute path of data filename
        data_filename_basename = os.path.basename(data_filename)

        # Build metadata file based on template metadata file and post-processed metadata
        config_base_metadata_lines = self.get_metadata_lines()

        config_automatic_lines = [];
        config_automatic_lines.append('data_original_filename = ' + data_filename_basename + '\n')
        config_automatic_lines.append('data_signature = ' + filesignature + '\n')
        config_automatic_lines.append('dsp_data_rate_decimation_ratio = ' + data_rate_decimation_ratio + '\n')
        config_automatic_lines.append('timestamp_start = ' + timestamp_start + '\n')
        config_automatic_lines.append('data_file_structure = ' + data_file_structure + '\n')
        config_automatic_lines.append('data_file_format = ascii\n')
        #config_automatic_lines.append('adc_board_temperature = ' + '0' + ' C\n') #TODO: implement ADC temperature read on FPGA
        #config_automatic_lines.append('rffe_board_temperature = ' + '0' + ' C\n') #TODO: implement RFFE temperature read on FPGA

        config_fromfile_lines = []
        config_fromfile_lines.extend(config_base_metadata_lines)
        config_fromfile_lines.extend(config_automatic_lines)

        # Metadata file is placed in the same path and with the same filename as the data file, but with .metadata extension
        output_metadata_filename = os.path.splitext(data_filename)[0] + '.metadata'

        with open(output_metadata_filename, 'x') as f:
            f.writelines(sorted(config_fromfile_lines))
