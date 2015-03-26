#Metadata reader file
#open file - argumento da funcao de rodar o script deve ser o caminho do arquivo do metadata template
def read_vars(filename):
   vars = dict()

   with open(filename) as f:
       for line in f:
           eq_index1 = line.find('=')
           var_name = line[:eq_index1].strip()
           eq_index2 = line.find('#')
           var_value = line[eq_index1 + 1:eq_index2].strip()
           vars[var_name] = var_value
       return vars
