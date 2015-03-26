#!/usr/bin/python3
# -*- coding: utf-8 -*-


####################################################################################################
#
# Begin of configuration section
#
####################################################################################################

# IP adress of Agilent E5061B vector network analyzer

VNA_IP = "10.0.18.54"

# IP address of RF front-end controller board

RFFE_CONTROLLER_BOARD_IP = "10.0.18.59"

# PC serial port where mbed (in switches board) is connected to (typically "/dev/ttyACM0")

RF_SWITCHES_BOARD_PORT = "/dev/ttyACM0"

# Start and stop frequency for the vector network analyzer frequency sweep. The values must be
# strings of bytes, and must contain a number in a format understandable by the instrument. For more
# information, refer to the equipment manuals. Example values: b"2E6" stands for 2 MHz, while b"2E8"
# is the correct string of bytes for the frequency of 200 MHz.

START_FREQUENCY = b"1E6"
STOP_FREQUENCY = b"1E9"

# Specific frequency for determining gain (S21). This should be a Python floating-point number.

TEST_FREQUENCY = 476E6 #This is not the central frequency, but for some tests, a gain will be determined for this frequency. This frequency is used to test for some parameters


####################################################################################################
#
# End of configuration section
#
####################################################################################################


####################################################################################################
#
#
# This is a preliminary version of the RF front-end final production test routine. The requirements
# are not precisely defined yet, so this code should be treated as a draft.
#
#
# The code stores data about the test at "data/<rffe_id>/<number_of_test>.dat", where <rffe_id> is
# the RF front-end board identification and <number_of_test> is a number which says how many tests
# were made for a board. For example, if a board has the ID "RFFE1" and no test were made on it yet,
# then the data resulting for the first test will be stored at data/RFFE1/001.dat. The second test
# data will be stored at data/RFFE2/002.dat, and so on. If the argument is "REF", than the program
# use the RF front-end connected as a reference for future comparison, always storing data at
# "data/reference.dat".
#
#
# This program has only one argument, which is the RFFE identification. If no argument is give, the
# program exits.
#
#
# All data resulting from the test is stored as text in an unique file. Data files are
# self-descritive. In other words, opening one of them with a simple text editor is sufficient not
# only for visualizing data, but also for understanding what it means.
#
#
# Concerning the hardware interconnections, the following connections must be made:
# 1) Port 1 of VNA to U1 RF common connector (J3);
# 2) U1 RF1 channel (J1) to the "A" ("B") input of the RF front-end;
# 3) U1 RF2 channel (J2) to the "C" ("D") input of the RF front-end;
# 4) Port 2 of VNA to U2 RF common connector (J6);
# 5) U2 RF1 channel (J4) to the "A/C" ("B/D") output of the RF front-end;
# 6) U2 RF2 channel (J5) to the "C/A" ("D/B") output of the RF front-end.
# 7) Interface board RF output must be wired to the SWITCH input of the RF front-end.
#
#
# It's important to note that in some Linux distributions super-user permissions are required for
# communicating to the mbed device in the switches board through the serial interface. To avoid
# permissision issues when running this program, always launch it with as root.
#
#
####################################################################################################


# Importing required libraries

from rffe_test_lib import RFSwitchesBoard, AgilentE5061B, RFFEControllerBoard
import glob
import os
import socket
import sys
import time


# Verifies if one argument is given to the program, as expected. If none or more than one argument
# are given, the program exits.

if (len(sys.argv) == 1):
    sys.stdout.write("\nThis program requires one argument, which corresponds to the RF " +
                     "front-end board identification. None was given. Exiting...\n\n")
    exit()
elif (len(sys.argv) > 2):
    sys.stdout.write("\nThis program requires one argument, which corresponds to the RF " +
                     "front-end board identification. More than one were given. Exiting...\n\n")
    exit()


# Initiates the communication to the three devices used in the test routine: the vector network
# analyzer (Agilent E5061B), the RF front-end controller board and the RF SPDT switches board. If
# establishing one of these connections is not successful, the program exits, indicating an error
# message.

try:
    controller_board = RFFEControllerBoard(RFFE_CONTROLLER_BOARD_IP)
except (socket.timeout):
    sys.stdout.write("\nUnable to reach the RF front-end controller board through the network. " +
                     "Exiting...\n\n")
    exit()

try:
    vna = AgilentE5061B(VNA_IP)
except (socket.timeout):
    sys.stdout.write("\nUnable to reach the vector network analyzer (Agilent E5061B) through the " +
                     "network. Exiting...\n\n")
    exit()

try:
    switches_board = RFSwitchesBoard(RF_SWITCHES_BOARD_PORT)
except (serial.serialutil.SerialException):
    sys.stdout.write("\nThe RF switches module seems not to be connected to the PC. Exiting...\n\n")
    exit()
switches_board.u1_set_none()
switches_board.u2_set_none()
switches_board.set_switch_signal_low()


# Shows an initial message

sys.stdout.write("\nRunning test...\n\n")


# Defines the path to the file that will store the test data

if (sys.argv[1] == "REF"):
    file_name = "./data/reference.dat"
    if (os.path.exists("./data") == False):
        os.makedirs("./data")
else:
    file_name = "./data/" + sys.argv[1] + "/001.dat"
    if (os.path.exists("./data/" + sys.argv[1]) == True):
        list_of_test_files = glob.glob("./data/" + sys.argv[1] + "/*.dat")
        if (list_of_test_files):
            file_name = list_of_test_files[len(list_of_test_files) - 1].split("/")
            file_name = file_name[len(file_name) - 1]
            file_name = file_name[0:len(file_name) - 4]
            file_name = int(file_name) + 1
            file_name = ("%03d" % (file_name)) + ".dat"
            file_name = "./data/" + sys.argv[1] + "/" + file_name
    else:
        os.makedirs("./data/" + sys.argv[1])

# The variable "file_content" contains the text that will be stored in the data file at the end of
# the test.

file_content = "RF front-end board identification: " + sys.argv[1] + "\r\n"
software_version = controller_board.get_software_version()
file_content += "Software version: " + software_version.decode() + "\r\n"
file_content += "Date and time of test: " + time.strftime("%d/%m/%Y, %H:%M") + "\r\n\r\n\r\n"


####################################################################################################
#
# Begin of test routine
#
####################################################################################################


# Sets Agilent E5061B start and stop frequencies and a marker at the desired specific frequency

vna.send_command(b":SENS1:FREQ:STAR " + START_FREQUENCY + b"\n")
vna.send_command(b":SENS1:FREQ:STOP " + STOP_FREQUENCY + b"\n")

vna.send_command(b":CALC1:MARK1 ON\n")
vna.send_command(b":CALC1:MARK1:X " + str(TEST_FREQUENCY).encode() + b"\n")


# Simple procedure to convert a Python list (previously converted to a string) into a MATLAB vector

def python_list_to_matlab_vector(python_list):
    splitted_list = python_list[1:len(python_list) - 1].split(", ")
    matlab_vector = "["
    for value in splitted_list:
        matlab_vector += value + " "
    matlab_vector += matlab_vector[0:len(matlab_vector) - 1]
    matlab_vector += "]"
    return(matlab_vector)


# Defines a procedure for testing each of the RF paths in the board

def path_test():

    # Global variables

    global TEST_FREQUENCY
    global file_content

    # Gets S-parameters data

    controller_board.set_attenuator_value(30.0)
    vna.send_command(b":SOUR1:POW:GPP -10.0\n")
    file_content += ("S-parameters: the following lines represent, respectively, frequency sweep " +
                    "values (MHz), S11, S12, S21 and S22 trace data (logarithmic scale). " +
                    "Attenuator is set to 30.0 dB and input power is -10.0 dBm.\r\n\r\n")
    frequency_data = vna.get_frequency_data()
    file_content += python_list_to_matlab_vector(str([(f / 1E6) for f in frequency_data])) + "\r\n"
    file_content += python_list_to_matlab_vector(str(vna.get_s11_data())) + "\r\n"
    file_content += python_list_to_matlab_vector(str(vna.get_s12_data())) + "\r\n"
    file_content += python_list_to_matlab_vector(str(vna.get_s21_data())) + "\r\n"
    vna.send_command(b":CALC1:MARK1:Y?\n")
    gain_at_specific_frequency = float(vna.get_answer().decode().split(",")[0])
    file_content += python_list_to_matlab_vector(str(vna.get_s22_data())) + "\r\n"
    file_content += ("Gain (S21) at " + ("%.2f" % (TEST_FREQUENCY / 1E6)) + " MHz: " +
                    ("%.2f" % gain_at_specific_frequency) + " dB\r\n\r\n")


    # Attenuation sweep

    vna.send_command(b":SOUR1:POW:GPP -45.0\n")
    file_content += ("Attenuation sweep: the following lines are the attenuation values of the " +
                     "RF front-end and the corresponding gain (S21) for the frequency of " +
                     ("%.2f" % (TEST_FREQUENCY / 1E6)) + " MHz, with input power set to " +
                     "-45.0 dBm. Attenuation is swept from 0 dB to 31.5 dB, with a 0.5 dB step " +
                     "size (total of 64 points).\r\n\r\n")
    attenuation_values = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0,
                          7.5, 8.0, 8.5, 9.0, 9.5, 10.0, 10.5, 11.0, 11.5, 12.0, 12.5, 13.0, 13.5,
                          14.0, 14.5, 15.0, 15.5, 16.0, 16.5, 17.0, 17.5, 18.0, 18.5, 19.0, 19.5,
                          20.0, 20.5, 21.0, 21.5, 22.0, 22.5, 23.0, 23.5, 24.0, 24.5, 25.0, 25.5,
                          26.0, 26.5, 27.0, 27.5, 28.0 , 28.5, 29.0, 29.5, 30.0, 30.5, 31.0, 31.5]
    gain_values = []
    i = 0
    while (i <= 63):
        controller_board.set_attenuator_value(attenuation_values[i])
        temp = vna.get_s21_data()
        vna.send_command(b":CALC1:MARK1:Y?\n")
        gain_at_specific_frequency = float(vna.get_answer().decode().split(",")[0])
        gain_values.append(gain_at_specific_frequency)
        i += 1
    file_content += python_list_to_matlab_vector(str(attenuation_values)) + "\r\n"
    file_content += python_list_to_matlab_vector(str(gain_values)) + "\r\n\r\n"


    # Input power sweep

    controller_board.set_attenuator_value(30.0)
    file_content += ("Input power sweep. Here the input power is swept from -45 dBm to 10 dBm, " +
                    "with a 5 dBm step size. The following lines represent, respectively, the " +
                    "input power and the gain (S21) at " + ("%.2f" % (TEST_FREQUENCY / 1E6)) +
                    " MHz. The attenuation of the front-end is set to 30.0 dB during sweep." +
                    "\r\n\r\n")
    input_powers = [-45.0, -40.0, -35.0, -30.0, -25.0, -20.0, -15.0, -10.0, -5.0, 0.0, 5.0, 10.0]
    gain_values = []
    i = 0
    while (i <= 11):
        vna.send_command(b":SOUR1:POW:GPP " + str(input_powers[i]).encode() + b"\n")
        temp = vna.get_s21_data()
        vna.send_command(b":CALC1:MARK1:Y?\n")
        gain_at_specific_frequency = float(vna.get_answer().decode().split(",")[0])
        gain_values.append(gain_at_specific_frequency)
        i += 1
    file_content += python_list_to_matlab_vector(str(input_powers)) + "\r\n"
    file_content += python_list_to_matlab_vector(str(gain_values)) + "\r\n\r\n\r\n"


# Gets data for the four possible RF paths

controller_board.set_switching_mode(1)

file_content += "*** A (B) to A/C (B/D) path ***\r\n\r\n"
switches_board.u1_set_rf1()
switches_board.u2_set_rf1()
path_test()

file_content += "*** C (D) to C/A (D/B) path ***\r\n\r\n"
switches_board.u1_set_rf2()
switches_board.u2_set_rf2()
path_test()

controller_board.set_switching_mode(2)

file_content += "*** A (B) to C/A (D/B) path ***\r\n\r\n"
switches_board.u1_set_rf1()
switches_board.u2_set_rf2()
path_test()

file_content += "*** C (D) to A/C (B/D) path ***\r\n\r\n"
switches_board.u1_set_rf2()
switches_board.u2_set_rf1()
path_test()


####################################################################################################
#
# End of test routine
#
####################################################################################################


# Writes the content of the file

output_file = open(file_name, "w")
output_file.write(file_content)
output_file.close()
sys.stdout.write("Test was completed sucessfully.\n\n")


# Terminates all connections to external hardware

controller_board.close_connection()
vna.close_connection()
switches_board.close_connection()
