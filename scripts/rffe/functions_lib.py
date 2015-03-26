

from rffe_test_lib import AgilentE5061B

def list_to_file(self, data, filename, separator):
    length=len(data)
    file = open(str(filename), "w")
    for i in range (0,length)
        str1 = ''.join(str(data[i]))
        str1=str1.replace("]], ","\n");
        str1=str1.replace("[","");
        str1=str1.replace("]","\n");
        str1=str1.replace(",","");
        str1=str1.replace(")","");
        str1=str1.replace("(","");
        str1=str1.replace("'","");
        file.write(str1+"\n")
    file.close()

def marker_value(frequency,s_param)
    if s_param=="s11":
        s11=vna.get_s11_data()
    else s_param=="s12":
        s12=vna.get_s12_data()
    else s_param=="s21":
        s21=vna.get_s21_data()
    else s_param=="s22":
        s22=vna.get_s22_data()
    vna.send_command(b":CALC1:MARK1:X " + str(frequency) + b"\n")
    vna.send_command(b":CALC1:MARK1:Y?\n")
    response=vna.get_answer()
    index = response.find(',')
    s21_testB = response[:index].strip()
    return(response)
