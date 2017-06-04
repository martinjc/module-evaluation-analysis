import os
import pandas

from tqdm import tqdm

from module_evaluation.config import *
from module_evaluation.io_utils import *
from module_evaluation.extract_module_data import *
from module_evaluation.extract_lecturer_data import get_lecturer_list, extract_lecturer_data
from module_evaluation.data_transform import read_input_dataframes, convert_to_likert_and_reduce


INPUT_DIRECTORY = 'input'
YEARS = ['1516', '1617']

OUTPUT_DIRECTORY = os.path.join(os.getcwd(), 'output')

dataframes = []

for year in YEARS:
    input_folder = os.path.join(os.getcwd(), INPUT_DIRECTORY, year)
    print(input_folder)
    dataframes.extend(read_input_dataframes(input_folder))

modules = get_module_list(dataframes)
print(modules)

# figure out which modules we have, and which occurences of each modules
modules2occurences = get_module_occurence_dict(dataframes)
print(modules2occurences)

# figure out which lecturer data we have
lecturers = get_lecturer_list(dataframes)
print(lecturers)

lecturers2modules = {}
# figure out which lecturer goes with which module data
for lecturer in lecturers:
    lecturer_data = extract_lecturer_data(dataframes, lecturer)
    lecturer_modules = get_module_occurence_dict([lecturer_data])

    lecturers2modules[lecturer] = lecturer_modules

print(lecturers2modules)


#
# for dataset, modules in datasets.items():
#     mean_comparison = get_module_and_occurence_data(dataframes, modules, '16A')
#     print(mean_comparison)




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
