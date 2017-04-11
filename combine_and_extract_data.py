import os
import pandas


from module_evaluation.data_transform import read_input_dataframes
from module_evaluation.extract_lecturer_data import get_lecturer_list, extract_lecturer_data
from module_evaluation.extract_module_data import get_module_occurence_dict


INPUT_DIRECTORY = 'input'
YEARS = ['1516', '1617']

dataframes = []

for year in YEARS:
    input_folder = os.path.join(os.getcwd(), INPUT_DIRECTORY, year)
    print(input_folder)
    dataframes.extend(read_input_dataframes(input_folder))

print(len(dataframes))

# figure out which modules we have, and which occurences of each modules
modules = get_module_occurence_dict(dataframes)
print(modules)

# figure out which lecturer data we have
lecturers = get_lecturer_list(dataframes)
print(lecturers)

# figure out which lecturer goes with which module data
for lecturer in lecturers:
    lecturer_data = extract_lecturer_data(dataframes, lecturer)
    lecturer_modules = get_module_occurence_dict([lecturer_data])

    print(lecturer)
    print(lecturer_modules)



# create per-year averages
# create per-semester averages
# create per-module averages
#
# school report - per year (lecturers)
# school report - per year (modules)
# school report - overall (yoy comparison)
#
# lecturer report
# module teaching data (overall and per module)
# yoy comparison
#
# module report (overall and per year)
# yoy comparison
#
# programme/year report (all lecturers)
# programme/year report (all modules)
