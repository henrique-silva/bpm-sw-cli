#!/usr/bin/python3
# -*- coding: utf-8 -*-


# This library requires pySerial and other modules.

from scipy.interpolate import interp1d
import numpy
import serial
import socket
import struct
import time


####################################################################################################
#
# Begin of configuration section
#
####################################################################################################

# Interval time for waiting between changing the vector network analyzer setup and reading data from
# it. Ideally, this sould be close to the network analyzer sweep time.

SLEEP_TIME = 2.0

####################################################################################################
#
# End of configuration section
#
####################################################################################################


####################################################################################################
#
#
# This comment block contains notes about the development process of this library.
#
#
# Regarding class RFFEControllerBoard, methods listed below seems coded correctly, but none of them
# works. The RF front-end controller board always returns only one value of temperature: 0.0 °C.
# Tests revealed that the board has some hardware problem which makes the temperature read always
# equal to zero.
#
# get_temp1()
# get_temp2()
#
#
####################################################################################################


class RFSwitchesBoard:
    """Class used to control the RF SPDT switches board and the switch signal to the RF front-end
    controller board."""

    def __init__(self, port):
        """Class constructor. Here the serial communication to the mbed device in the board is
        initialized. The argument required (a string) is the PC serial port where mbed (in switches
        board) is connected to (typically "/dev/ttyACM0")."""
        self.serial_interface = serial.Serial(port, 9600, bytesize = serial.EIGHTBITS,
                                              parity = serial.PARITY_NONE,
                                              stopbits = serial.STOPBITS_ONE)

    def u1_set_rf1(self):
        """Set the RF1 channel of switch U1 as active, turning RF2 off."""
        self.serial_interface.write(bytes.fromhex("62"))

    def u1_set_rf2(self):
        """Set the RF2 channel of switch U1 as active, turning RF1 off."""
        self.serial_interface.write(bytes.fromhex("63"))

    def u1_set_none(self):
        """Turns both channels of U1 switch off."""
        self.serial_interface.write(bytes.fromhex("61"))

    def u2_set_rf1(self):
        """Set the RF1 channel of switch U2 as active, turning RF2 off."""
        self.serial_interface.write(bytes.fromhex("65"))

    def u2_set_rf2(self):
        """Set the RF2 channel of switch U2 as active, turning RF1 off."""
        self.serial_interface.write(bytes.fromhex("66"))

    def u2_set_none(self):
        """Turns both channels of U2 switch off."""
        self.serial_interface.write(bytes.fromhex("64"))

    def set_switch_signal_low(self):
        """Set the switch signal to the RF front-end controller board to the LOW state."""
        self.serial_interface.write(bytes.fromhex("67"))

    def set_switch_signal_high(self):
        """Set the switch signal to the RF front-end controller board to the HIGH state."""
        self.serial_interface.write(bytes.fromhex("68"))

    def close_connection(self):
        """Close the serial connection to the mbed device."""
        self.serial_interface.close()


class AgilentE5061B:
    """Class used to send commands and acquire data from the Agilent E5061B vector network analyzer.
    """

    def __init__(self, ip):
        """Class constructor. Here the socket connection to the instrument is initialized. The
        argument required, a string, is the IP adress of the instrument."""
        vna_address = ((ip, 5025))
        self.vna_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.vna_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.vna_socket.settimeout(5.0)
        self.vna_socket.connect(vna_address)
        self.vna_socket.send(b":SYST:PRES\n")
        self.vna_socket.send(b":DISP:WIND1:TRAC1:Y:RLEV -75\n")
        self.vna_socket.send(b":DISP:WIND1:TRAC1:Y:PDIV 25\n")
        self.vna_socket.send(b":SENS1:SWE:TIME:AUTO ON\n")
        self.vna_socket.send(b":SENS1:SWE:POIN 1601\n")
        self.vna_socket.send(b":SENS1:SWE:TYPE LIN\n")
        self.vna_socket.send(b":SOUR1:POW:GPP 0.0\n")
        time.sleep(SLEEP_TIME)

    def get_answer(self):
        """Get the instrument's answer after sending a command. It is returned as a string of bytes.
        """
        data = b""
        while (data[len(data) - 1:] != b"\n"):
            data += self.vna_socket.recv(1024)
        return(data)

    def get_frequency_data(self):
        """Get the list of frequencies of the instrument sweep, returning a sequence of floating
           point numbers."""
        self.vna_socket.send(b":SENS1:FREQ:DATA?\n")
        frequency_data = b""
        while (frequency_data[len(frequency_data) - 1:] != b"\n"):
            frequency_data += self.vna_socket.recv(1024)
        frequency_data = frequency_data[:len(frequency_data) - 1].split(b",")
        frequency_data = [float(i) for i in frequency_data]
        return(frequency_data)

    def get_s11_data(self):
        """Get the S11 trace data, returning a sequence of floating point numbers."""
        self.vna_socket.send(b":CALC1:PAR1:DEF S11\n")
        time.sleep(SLEEP_TIME)
        self.vna_socket.send(b":CALC1:DATA:FDAT?\n")
        s11_data = b""
        while (s11_data[len(s11_data) - 1:] != b"\n"):
            s11_data += self.vna_socket.recv(1024)
        s11_data = s11_data[:len(s11_data) - 1].split(b",")
        s11_data = s11_data[::2]
        s11_data = [float(i) for i in s11_data]
        return(s11_data)

    def get_s12_data(self):
        """Get the S12 trace data, returning a sequence of floating point numbers."""
        self.vna_socket.send(b":CALC1:PAR1:DEF S12\n")
        time.sleep(SLEEP_TIME)
        self.vna_socket.send(b":CALC1:DATA:FDAT?\n")
        s12_data = b""
        while (s12_data[len(s12_data) - 1:] != b"\n"):
            s12_data += self.vna_socket.recv(1024)
        s12_data = s12_data[:len(s12_data) - 1].split(b",")
        s12_data = s12_data[::2]
        s12_data = [float(i) for i in s12_data]
        return(s12_data)

    def get_s21_data(self):
        """Get the S21 trace data, returning a sequence of floating point numbers."""
        self.vna_socket.send(b":CALC1:PAR1:DEF S21\n")
        time.sleep(SLEEP_TIME)
        self.vna_socket.send(b":CALC1:DATA:FDAT?\n")
        s21_data = b""
        while (s21_data[len(s21_data) - 1:] != b"\n"):
            s21_data += self.vna_socket.recv(1024)
        s21_data = s21_data[:len(s21_data) - 1].split(b",")
        s21_data = s21_data[::2]
        s21_data = [float(i) for i in s21_data]
        return(s21_data)

    def get_s22_data(self):
        """Get the S22 trace data, returning a sequence of floating point numbers."""
        self.vna_socket.send(b":CALC1:PAR1:DEF S22\n")
        time.sleep(SLEEP_TIME)
        self.vna_socket.send(b":CALC1:DATA:FDAT?\n")
        s22_data = b""
        while (s22_data[len(s22_data) - 1:] != b"\n"):
            s22_data += self.vna_socket.recv(1024)
        s22_data = s22_data[:len(s22_data) - 1].split(b",")
        s22_data = s22_data[::2]
        s22_data = [float(i) for i in s22_data]
        return(s22_data)

    def set_marker_frequency(self,value)
        """set the center frequency of the VNA"""
        self.vna.send_command(b":CALC1:MARK1:X " + str(value) + b"\n")
        return

    def get_marker_value(self)
        self.vna.send_command(b":CALC1:MARK1:Y?\n")
        ans=vna.get_answer()
        return(ans)

    def send_command(self, text):
        """Sends a command to the instrument. The "text" argument must be a string of bytes."""
        self.vna_socket.send(text)
        time.sleep(SLEEP_TIME)
        return

    def close_connection(self):
        """Close the socket connection to the instrument."""
        self.vna_socket.close()


class RFFEControllerBoard:
    """Class used to send commands and acquire data from the RF front-end controller board."""

    def __init__(self, ip):
        """Class constructor. Here the socket connection to the board is initialized. The argument
        required is the IP adress of the instrument (string)."""
        board_address = ((ip, 6791))
        self.board_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.board_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self.board_socket.settimeout(5.0)
        self.board_socket.connect(board_address)

    def get_switching_mode(self):
        """This method returns the current switching mode. Its answers are one of the following
        integers:
        0: matched
        1: direct
        2: inverted
        3: switching"""
        self.board_socket.send(bytes.fromhex("10 00 01 00"))
        temp = self.board_socket.recv(1024)
        return(temp[3])

    def set_switching_mode(self, mode):
        """Sets the switching mode of operation. The accepted arguments are the following integers:
        0: matched
        1: direct
        2: inverted
        3: switching
        Other arguments will be disconsidered."""
        if (mode in (0, 1, 2, 3)):
            self.board_socket.send(bytes.fromhex("20 00 02 00 0" + str(mode)))
            temp = self.board_socket.recv(1024)

    def get_attenuator_value(self):
        """This method returns the current attenuation value (in dB) as a floating-point number.
           The attenuation value will be between 0 dB and 31.5 dB, with a 0.5 dB step size."""
        self.board_socket.send(bytes.fromhex("10 00 01 01"))
        temp = self.board_socket.recv(1024)
        return(struct.unpack("<d", temp[3:])[0])

    def set_attenuator_value(self, value):
        """Sets the attenuation value of both front-ends. The agrument should be a
        floating-point number representing the attenuation (in dB) between 0 dB and 31.5 dB, with a
        0.5 dB step size. Argument values other than these will be disconsidered."""
        if (value in tuple(numpy.linspace(0, 31.5, 64))):
            self.board_socket.send(bytes.fromhex("20 00 09 01") + struct.pack("<d", value))
            temp = self.board_socket.recv(1024)

    def get_temp1(self):
        """This method returns the temperature measured by the sensor present in the A/C
        front-end. The value returned is a floating-point number."""
        self.board_socket.send(bytes.fromhex("10 00 01 03"))
        temp = self.board_socket.recv(1024)
        return(struct.unpack("<d", temp[3:])[0])

    def get_temp2(self):
        """This method returns the temperature measured by the sensor present in the B/D
        front-end. The value returned is a floating-point number."""
        self.board_socket.send(bytes.fromhex("10 00 01 04"))
        temp = self.board_socket.recv(1024)
        return(struct.unpack("<d", temp[3:])[0])

    def get_temp1_setpoint(self):
        """This method returns the temperature set-point for the A/C front-end temperature
        controller. The returned value is a floating-point number in the Celsius degrees scale."""
        self.board_socket.send(bytes.fromhex("10 00 01 07"))
        temp = self.board_socket.recv(1024)
        return(struct.unpack("<d", temp[3:])[0])

    def set_temp1_setpoint(self, value):
        """Sets the temperature set-point for the A/C front-end temperature controller. The value
        passed as the argument is a floating-point number."""
        self.board_socket.send(bytes.fromhex("20 00 09 07") + struct.pack("<d", value))
        temp = self.board_socket.recv(1024)

    def get_temp2_setpoint(self):
        """This method returns the temperature set-point for the B/D front-end temperature
        controller. The returned value is a floating-point number in the Celsius degrees scale."""
        self.board_socket.send(bytes.fromhex("10 00 01 08"))
        temp = self.board_socket.recv(1024)
        return(struct.unpack("<d", temp[3:])[0])

    def set_temp2_setpoint(self, value):
        """Sets the temperature set-point for the B/D front-end temperature controller. The value
        passed as the argument is a floating-point number."""
        self.board_socket.send(bytes.fromhex("20 00 09 08") + struct.pack("<d", value))
        temp = self.board_socket.recv(1024)

    def get_temperature_control_status(self):
        """This method returns the temperature controller status as an integer. If this integer
        equals 0, it's because the temperature controller is off. Otherwise, if the value returned
        equals 1, this means the temperature controller is on."""
        self.board_socket.send(bytes.fromhex("10 00 01 09"))
        temp = self.board_socket.recv(1024)
        return(temp[3])

    def set_temperature_control_status(self, status):
        """Method used to turn on/off the temperature controller. For turning the controller on, the
        argument should be the integer 1. To turn the controller off, the argument should be 0."""
        if (status in (0, 1)):
            self.board_socket.send(bytes.fromhex("20 00 02 09 0" + str(status)))
            temp = self.board_socket.recv(1024)

    def get_software_version(self):
        """This method returns the RF front-end controller software version as a binary
    string of characters."""
        self.board_socket.send(bytes.fromhex("10 00 01 0F"))
        temp = self.board_socket.recv(1024)
        return(temp[3:10])

    def get_output1_value(self):
        """This method returns the voltage signal to the heater in the A/C front-end as a
        floating-point number."""
        self.board_socket.send(bytes.fromhex("10 00 01 0A"))
        temp = self.board_socket.recv(1024)
        return(struct.unpack("<d", temp[3:])[0])

    def set_output1_value(self, value):
        """Sets the voltage level to the heater in the A/C front-end. The value passed as the
        argument, a floating-point number, is the intended voltage for the heater."""
        self.board_socket.send(bytes.fromhex("20 00 09 0A") + struct.pack("<d", value))
        temp = self.board_socket.recv(1024)

    def get_output2_value(self):
        """This method returns the voltage signal to the heater in the B/D front-end as a
        floating-point number."""
        self.board_socket.send(bytes.fromhex("10 00 01 0B"))
        temp = self.board_socket.recv(1024)
        return(struct.unpack("<d", temp[3:])[0])

    def set_output2_value(self, value):
        """Sets the voltage level to the heater in the B/D front-end. The value passed as the
        argument, a floating-point number, is the intended voltage for the heater."""
        self.board_socket.send(bytes.fromhex("20 00 09 0B") + struct.pack("<d", value))
        temp = self.board_socket.recv(1024)

    def reprogram(self, file_path):
        """This method reprograms the mbed device on the RF front-end controller board. The
        argument, a string, is the path to the binary file which corresponds to the mbed program
        that will be loaded in the device."""
        file = open(file_path, "rb")
        self.board_socket.send(bytes.fromhex("20 00 02 0D 01"))
        temp = self.board_socket.recv(1024)
        while True:
            data = file.read(127)
            if (not data):
                break
            elif (len(data) < 127):
                data = data + (b"\n" * (127 - len(data)))
            self.board_socket.send(bytes.fromhex("20 00 80 0E") + data)
            temp = self.board_socket.recv(1024)
        self.board_socket.send(bytes.fromhex("20 00 02 0D 02"))
        temp = self.board_socket.recv(1024)
        file.close()

    def reset(self):
        """This method resets the board software."""
        self.board_socket.send(bytes.fromhex("20 00 02 0C 01"))
        temp = self.board_socket.recv(1024)

    def close_connection(self):
        """Close the socket connection to the board."""
        self.board_socket.close()
