#rffe_run_test
from rffe_test_lib import RF_switch_board, AgilentE5061B, RFFEControllerBoard, Agilent33521A
import sys
import read_metadata
import numpy as np
import test_lib
import shutil
import time
import os

print("\n- Loading parameters\n- Instruments configuration\n...\n")

######################################
#inserir programa de leitura da camera
serial_number=str(sys.argv[1])
#serial_number="123456798"

#################################
metadata_path=str(sys.argv[2])
#metadata_path="/home/lnls-bpm/Desktop/test_report_bpm_hardware/rffe/rffe_test_metadata.txt"

datapath_save=str(sys.argv[3])
#datapath_save="/home/lnls-bpm/Desktop/test_report_bpm_hardware/rffe/test_result/"
######################################

##get current date and time
current_time=str(time.strftime("%c"))
current_day=str(time.strftime("%d-%m-%Y"))

try:
    os.makedirs(datapath_save + "sn_" + str(serial_number)+"/"+current_day)
except:
  pass

datapath_save=datapath_save + "sn_" + str(serial_number)+"/"+current_day+"/"

metadata_param=read_metadata.read_vars(metadata_path)

#test configuration
vna=AgilentE5061B(metadata_param['ip_vna'])
rffe=RFFEControllerBoard(metadata_param['ip_rffe'])
rfsw=RF_switch_board(metadata_param['ip_rfsw'])
sgen=Agilent33521A(metadata_param['ip_sgen'])
################################################
print("Network/LAN configuration - ok!\n...\n")

#################################
#get frequency data from the VNA
#setar frequencia central, span e qde de pontos
#get values from metadata
##################################

att_value=float(metadata_param['att_value'])
pow_value=float(metadata_param['pow_value'])
n_points=int(float(metadata_param['n_points']))
xtalk_ref=float(metadata_param['xtalk_ref'])
xtalk_tol=float(metadata_param['xtalk_tolerance'])
center_freq=int(metadata_param['freq_center'])
freq_span=int(metadata_param['freq_span'])
att_step=float(metadata_param['att_sweep_step'])
pow_sweep_ini=float(metadata_param['pow_sweep_ini'])
pow_sweep_end=float(metadata_param['pow_sweep_end'])
pow_sweep_att=float(metadata_param['pow_sweep_att'])
pow_sweep_step=float(metadata_param['pow_sweep_step'])
att_sweep_low=float(metadata_param['att_sweep_low'])
att_sweep_high=float(metadata_param['att_sweep_high'])
att_step_tol=float(metadata_param['att_step_tol'])
temp_min=float(metadata_param['temp_min'])
temp_max=float(metadata_param['temp_max'])

s11_ref=float(metadata_param['s11_ref'])
s12_ref=float(metadata_param['s12_ref'])
s21_ref=float(metadata_param['s21_ref'])
s22_ref=float(metadata_param['s22_ref'])
s11_tol=float(metadata_param['s11_tolerance'])
s12_tol=float(metadata_param['s12_tolerance'])
s21_tol=float(metadata_param['s21_tolerance'])
s22_tol=float(metadata_param['s22_tolerance'])
linearity_tol=float(metadata_param['linearity_tol'])
print("Test parameters loaded from metadata - ok!\n...\n")

#Data  measurement from the Network Analyzer for different switches positions

sgen.set_pos("direct")
vna.send_command(b":SOUR1:POW:GPP "+format(pow_value).encode('utf-8')+b"\n") #-->for python3

print("Starting tests. Measuring S-parameters ...\n")

test_lib.set_vna(0, center_freq, freq_span, 0, vna)

rfsw.sw1_pos(1)
rfsw.sw2_pos(1)
s11_pos1=vna.get_s11_data()
s12_pos1=vna.get_s12_data()
s21_pos1=vna.get_s21_data()
s22_pos1=vna.get_s22_data()

s11_pos1=np.array([[s11_pos1]]).T
s12_pos1=np.array([[s12_pos1]]).T
s21_pos1=np.array([[s21_pos1]]).T
s22_pos1=np.array([[s22_pos1]]).T
sparam_pos1 = np.c_[s11_pos1, s12_pos1, s21_pos1, s22_pos1]

print("...\n")

rfsw.sw1_pos(1)
rfsw.sw2_pos(2)
s11_pos2=vna.get_s11_data()
s12_pos2=vna.get_s12_data()
s21_pos2=vna.get_s21_data()
s22_pos2=vna.get_s22_data()

s11_pos2=np.array([[s11_pos2]]).T
s12_pos2=np.array([[s12_pos2]]).T
s21_pos2=np.array([[s21_pos2]]).T
s22_pos2=np.array([[s22_pos2]]).T
sparam_pos2 = np.c_[s11_pos2, s12_pos2, s21_pos2, s22_pos2]

print("...\n")

rfsw.sw1_pos(2)
rfsw.sw2_pos(1)
s11_pos3=vna.get_s11_data()
s12_pos3=vna.get_s12_data()
s21_pos3=vna.get_s21_data()
s22_pos3=vna.get_s22_data()

s11_pos3=np.array([[s11_pos3]]).T
s12_pos3=np.array([[s12_pos3]]).T
s21_pos3=np.array([[s21_pos3]]).T
s22_pos3=np.array([[s22_pos3]]).T
sparam_pos3 = np.c_[s11_pos3, s12_pos3, s21_pos3, s22_pos3]

print("...\n")

rfsw.sw1_pos(2)
rfsw.sw2_pos(2)
s11_pos4=vna.get_s11_data()
s12_pos4=vna.get_s12_data()
s21_pos4=vna.get_s21_data()
s22_pos4=vna.get_s22_data()

s11_pos4=np.array([[s11_pos4]]).T
s12_pos4=np.array([[s12_pos4]]).T
s21_pos4=np.array([[s21_pos4]]).T
s22_pos4=np.array([[s22_pos4]]).T
sparam_pos4 = np.c_[s11_pos4, s12_pos4, s21_pos4, s22_pos4]

print("Saving test data\n")
freq_data=vna.get_frequency_data()
freq_data_file=np.array([[freq_data]]).T
sparam=np.c_[freq_data_file, sparam_pos1, sparam_pos2, sparam_pos3, sparam_pos4]
test_lib.list_to_file(0,sparam,datapath_save + serial_number + "_data.txt")
#imprimir arquivo de texto

#Attenuators sweep test
s21_testA=list()
step_sizeA=list()
s21_testB=list()
step_sizeB=list()
if metadata_param['att_sweep_test']=="run":
    print("Running attenuators sweep test ... \n")
    test_lib.set_vna(0, center_freq, freq_span, 0, vna)
    sgen.set_pos("direct")
    s21=vna.get_s21_data() #Select the S21 measurement in theNetwork Analyzer
    vna.send_command(b":SOUR1:POW:GPP "+format(pow_value).encode('utf-8')+b"\n")
    rfsw.sw1_pos(1)
    rfsw.sw2_pos(1)
    print("Running attenuators sweep test, Channel A ... \n")
    for att in range (int(att_sweep_low), int(att_sweep_high+1)*2, int(att_step*2)):
        rffe.set_attenuator_value(att/2)
        s21=test_lib.marker_value(0,center_freq,"s21", vna)
        s21=float(test_lib.marker_value(0,center_freq,"s21", vna))
        s21_testA.append(round(s21,2))
    fail=0
    for i in range(0,len(s21_testA)-1):
        step_sizeA.append(round(s21_testA[i+1]-s21_testA[i],2))
        if abs(float(step_sizeA[i]))>abs(att_step+att_step_tol) or abs(float(step_sizeA[i]))<abs(att_step-att_step_tol):
            fail=1
    if fail==1:
        att_sweep_resultA="Attenuator Sweep Test Channel A --> FAILED"
    else:
        att_sweep_resultA="Attenuator Sweep Test Channel A --> Ok"
    #Data aquisition for channel B
    test_lib.set_vna(0, center_freq, freq_span, 0, vna)
    rfsw.sw1_pos(2)
    rfsw.sw2_pos(2)
    print("Running attenuators sweep test, Channel B ... \n")
    for att in range (int(att_sweep_low), int(att_sweep_high+1)*2, int(att_step*2)):
        rffe.set_attenuator_value(att/2)
        s21=float(test_lib.marker_value(0,center_freq,"s21", vna))
        s21_testB.append(round(s21,2))
    for i in range(0,len(s21_testB)-1):
        step_sizeB.append(round(s21_testB[i+1]-s21_testB[i],2))
        if abs(float(step_sizeB[i]))>abs(att_step+att_step_tol) or abs(float(step_sizeB[i]))<abs(att_step-att_step_tol):
            fail=1
    if fail==1:
        att_sweep_resultB="Attenuator Sweep Test Channel B --> FAILED"
    else:
        att_sweep_resultB="Attenuator Sweep Test Channel B --> Ok"
else:
    att_sweep_resultA="Attenuator Sweep Test Channel A --> Test not Performed"
    att_sweep_resultB="Attenuator Sweep Test Channel B --> Test not Performed"

#RF switches test
s21_sw_result=list()
if metadata_param['sw_test']=="run":
    print("Running RF switches test ... \n")
    test_lib.set_vna(0, center_freq, freq_span, 0, vna)
    rffe.set_attenuator_value(att_value)
    #setar potencia do sinal no VNA
    rfsw.sw1_pos(1)
    rfsw.sw2_pos(1)
    sgen.set_pos("direct")
    s21_testA=float(test_lib.marker_value(0,center_freq, "s21", vna))
    sgen.set_pos("inverted")
    s21_sw_result.append(round(s21_testA,2))
    s21_testB=float(test_lib.marker_value(0,center_freq, "s21", vna))
    s21_sw_result.append(round(s21_testB,2))
    if abs(float(s21_testA)-float(s21_testB))<abs(xtalk_ref):
        rf_sw_result="RF Switches Test                --> FAILED"
    else:
        rf_sw_result="RF Switches Test                --> Ok"
else:
    rf_sw_result="RF Switches Test                --> Test not Performed"

#Frequency Response
s21_freq_resp=list()
if metadata_param['freq_response']=="run":
    print("Running Frequency response test ... \n")
    test_lib.set_vna(0, center_freq, freq_span, 0, vna)
    sgen.set_pos("direct")
    rffe.set_attenuator_value(att_value)
    vna.send_command(b":SOUR1:POW:GPP "+format(pow_value).encode('utf-8')+b"\n")
    rfsw.sw1_pos(1)
    rfsw.sw2_pos(1)
    s21_testA=float(test_lib.marker_value(0,center_freq, "s21", vna))
    s21_freq_resp.append(round(s21_testA,2))
    rfsw.sw1_pos(2)
    rfsw.sw2_pos(2)
    sgen.set_pos("direct")
    s21_testB=float(test_lib.marker_value(0,center_freq, "s21", vna))
    s21_freq_resp.append(round(s21_testB,2))
    if abs(float(s21_testA)-s21_ref)>s21_tol:
        freq_resp_resultA="Frequency Response Channel A    --> FAILED"
    else:
        freq_resp_resultA="Frequency Response Channel A    --> Ok"
    if abs(float(s21_testB)-s21_ref)>s21_tol:
        freq_resp_resultB="Frequency Response Channel B    --> FAILED"
    else:
        freq_resp_resultB="Frequency Response Channel B    --> Ok"
else:
    freq_resp_resultA="Frequency Response Channel A    --> Test not Performed"
    freq_resp_resultB="Frequency Response Channel B    --> Test not Performed"

#Return Loss
s11_freq_resp=list()
if metadata_param['return_loss']=="run":
    print("Running return loss test ... \n")
    test_lib.set_vna(0, center_freq, freq_span, 0, vna)
    sgen.set_pos("direct")
    rffe.set_attenuator_value(att_value)
    vna.send_command(b":SOUR1:POW:GPP "+format(pow_value).encode('utf-8')+b"\n")
    rfsw.sw1_pos(1)
    rfsw.sw2_pos(1)
    s11_testA=float(test_lib.marker_value(0,center_freq, "s11", vna))
    s11_freq_resp.append(round(s11_testA,2))
    rfsw.sw1_pos(2)
    rfsw.sw2_pos(2)
    sgen.set_pos("direct")
    s11_testB=float(test_lib.marker_value(0,center_freq, "s11", vna))
    s11_freq_resp.append(round(s11_testB,2))
    if abs(float(s11_testA))<abs(s11_ref+s11_tol):
        return_loss_resultA="Return Loss Channel A           --> FAILED"
    else:
        return_loss_resultA="Return Loss Channel A           --> Ok"
    if abs(float(s11_testB))<abs(s11_ref+s11_tol):
        return_loss_resultB="Return Loss Channel B           --> FAILED"
    else:
        return_loss_resultB="Return Loss Channel B           --> Ok"
else:
    return_loss_resultA="Return Loss Channel A           --> Test not Performed"
    return_loss_resultB="Return Loss Channel B           --> Test not Performed"

#Power sweep
pow_sweep_resultA=list()
pow_sweep_resultB=list()
if metadata_param['power_sweep']=="run":
    print("Running power sweep and linearity test ... \n")
    rffe.set_attenuator_value(pow_sweep_att)
    test_lib.set_vna(0, center_freq, freq_span, 0, vna)
    sgen.set_pos("direct")
    power_values=np.arange(float(pow_sweep_ini),float(pow_sweep_end),float(pow_sweep_step))
    rfsw.sw1_pos(1)
    rfsw.sw2_pos(1)
    s21_testA=0
    s21_testA=list()
    for i in range (0,len(power_values)):
        vna.send_command(b":SOUR1:POW:GPP "+format(power_values[i]).encode('utf-8')+b"\n")
        s21=float(test_lib.marker_value(0,center_freq,"s21", vna))
        s21_testA.append(round(s21,2))
    #initialize the test routine for channel B
    rfsw.sw1_pos(2)
    rfsw.sw2_pos(2)
    pow_sweep_resultA=s21_testA
    s21_testB=0
    s21_testB=list()
    for i in range (0,len(power_values)):
        vna.send_command(b":SOUR1:POW:GPP "+format(power_values[i]).encode('utf-8')+b"\n")
        s21=float(test_lib.marker_value(0,center_freq,"s21", vna))
        s21_testB.append(round(s21,2))
 #Test analysis: verify if the linearity is inside the limits
    pow_sweep_resultB=s21_testB
    test_lib.set_vna(0, center_freq, freq_span, 0, vna)
    fail=0
    for i in range(0,len(s21_testA)-1):
        if abs(float(s21_testA[i+1])-float(s21_testA[i]))>abs(float(linearity_tol)):
            fail=1
    if fail==1:
        lin_resultA="Linearity Test Channel A        --> FAILED"
    else:
        lin_resultA="Linearity Test Channel A        --> Ok"
    fail=0
    for i in range(0,len(s21_testB)-1):
        if abs(float(s21_testB[i+1])-float(s21_testB[i]))>abs(float(linearity_tol)):
            fail=1
    if fail==1:
        lin_resultB="Linearity Test Channel B        --> FAILED"
    else:
        lin_resultB="Linearity Test Channel B        --> Ok"
else:
    lin_resultA="Linearity Test Channel A        --> Test not Performed"
    lin_resultB="Linearity Test Channel B        --> Test not Performed"

vna.send_command(b":SOUR1:POW:GPP "+str(pow_value)+b"\n")

#Script for Crosstalk tests
xtalk_result=list()
if metadata_param['xtalk']=="run":
    print("Running Crosstalk test ... \n")
    test_lib.set_vna(0, center_freq, freq_span, 0, vna)
    sgen.set_pos("direct")
    rffe.set_attenuator_value(att_value)
    vna.send_command(b":SOUR1:POW:GPP "+format(pow_value).encode('utf-8')+b"\n")
    rfsw.sw1_pos(1)
    rfsw.sw2_pos(2)
    s21_testA=float(test_lib.marker_value(0,center_freq, "s21", vna))
    xtalk_result.append(round(s21_testA-xtalk_tol,2))
    rfsw.sw1_pos(2)
    rfsw.sw2_pos(1)
    sgen.set_pos("direct")
    s21_testB=float(test_lib.marker_value(0,center_freq, "s21", vna))
    xtalk_result.append(round(s21_testB-xtalk_tol,2))
    if abs(s21_testA)<abs(xtalk_ref+xtalk_tol):
        xtalk_resp_resultA="Crosstalk Channel A             --> FAILED"
    else:
        xtalk_resp_resultA="Crosstalk Channel A             --> Ok"
    if abs(s21_testB)<abs(xtalk_ref+xtalk_tol):
        xtalk_resp_resultB="Crosstalk Channel B             --> FAILED"
    else:
        xtalk_resp_resultB="Crosstalk Channel B             --> Ok"
else:
    xtalk_resp_resultA="Crosstalk Channel A             --> Test not Performed"
    xtalk_resp_resultB="Crosstalk Channel B             --> Test not Performed"

#Temperature Measurement
if metadata_param['temp']=="run":
    temperature=rffe.get_temp1()
    fail=0
    if (temperature < 5 or temperature >100):
        temperature = rffe.get_temp2()
        if (temperature < 5 or temperature > 100):
            fail=1
    temperature=round(temperature,2)
    if (temperature<temp_min or temperature>temp_max):
        fail=1
    if (fail==1):
        temp_test="Temperature Measurement         --> FAILED"
    elif (fail==0):
        temp_test="Temperature Measurement         --> Ok"
else:
    temp_test="Temperature Measurement         --> Not Performed"

sw_version="RFFE Software Version: " +str(rffe.get_software_version())

#Print the test result in the txt file
test_result=([current_time],[att_sweep_resultA],[att_sweep_resultB],[rf_sw_result],[freq_resp_resultA],[freq_resp_resultB],[return_loss_resultA],[return_loss_resultB],[xtalk_resp_resultA],[xtalk_resp_resultB],[lin_resultA],[lin_resultB],[temp_test])
test_lib.list_to_file(0,test_result,datapath_save + serial_number + "_result.txt")

#print metadata with the correct filename
shutil.copy2(metadata_path,datapath_save+serial_number+"_metadata.txt")

#print test result values with the correct filename
test_result_values=([current_time],[sw_version],[att_sweep_resultA],[step_sizeA],[att_sweep_resultB],[step_sizeB],[rf_sw_result],[s21_sw_result],[freq_resp_resultA],[freq_resp_resultB],[s21_freq_resp],[return_loss_resultA],[return_loss_resultB],[s11_freq_resp],[lin_resultA],[pow_sweep_resultA],[lin_resultB],[pow_sweep_resultB],[xtalk_resp_resultA],[xtalk_resp_resultB],[xtalk_result],[temp_test],[temperature])
test_lib.list_to_file(0,test_result_values,datapath_save + serial_number + "_result_values.txt")

print("Test finished!")

##Close ethernet connection
vna.close_connection()
rffe.close_connection()
rfsw.close_connection()
sgen.close_connection()
