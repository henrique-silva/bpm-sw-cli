from rffe_test_lib import AgilentE5061B

def list_to_file(self, data, filename):
    length=len(data)
    file = open(str(filename), "w")
    for i in range (0,length):
        str1 = ''.join(str(data[i]))
        str1=str1.replace("]], ","");
        str1=str1.replace("[","");
        str1=str1.replace("]","");
        str1=str1.replace(",","");
        str1=str1.replace(")","");
        str1=str1.replace("(","");
        str1=str1.replace("'","");
        str1=str1.replace("\n"," ");
        file.write(str1+"\n")
    file.close()

def marker_value(self, frequency, s_param, interface):
    vna=interface
    if s_param=="s11":
        s11=vna.get_s11_data()
    elif s_param=="s12":
        s12=vna.get_s12_data()
    elif s_param=="s21":
        s21=vna.get_s21_data()
    elif s_param=="s22":
        s22=vna.get_s22_data()
    vna.send_command(b":CALC1:MARK1:X " + str(frequency) + b"\n")
    vna.send_command(b":CALC1:MARK1:Y?\n")
    response=vna.get_answer()
    index = response.find(',')
    response = response[:index].strip()
    return(response)

def set_vna(self, freq_center, freq_span, autoscale, interface):
    ##frequency in MHz, Span in MHz, and autoscale =0 or autoscale =1.
    vna=interface
    vna.send_command(b":SENS1:FREQ:CENT " + str(freq_center) + b"\n")
    vna.send_command(b":SENS1:FREQ:SPAN " + str(freq_span) + b"\n")
    if autoscale == 1:
        vna.send_command(b":DISP:WIND1:TRAC1:Y:AUTO\n")
    return
