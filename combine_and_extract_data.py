import os
import json
import pandas

from tqdm import tqdm

from module_evaluation.config import *
from module_evaluation.io_utils import *
from module_evaluation.data_transform import *
from module_evaluation.extract_module_data import *
from module_evaluation.extract_lecturer_data import *


INPUT_DIRECTORY = 'input'

# Create all the directories we'll need for output
OUTPUT_DIRECTORY = os.path.join(os.getcwd(), 'output')

for directory in ['lecturers', 'modules', 'subsets']:
    for datatype in ['csv', 'pdf', 'json']:
        to_create = os.path.join(OUTPUT_DIRECTORY, directory, datatype)
        if not os.path.exists(to_create):
            os.makedirs(to_create)

# Read in all the data we have
dataframes = []

print('\nreading input data')

for year in YEARS2OCCURENCES.keys():
    input_folder = os.path.join(os.getcwd(), INPUT_DIRECTORY, year)
    print(input_folder)
    dataframes.extend(read_input_dataframes(input_folder))

print('\nfound feedback data for these modules:')
# get the list of modules we have data for
modules = get_module_list(dataframes)
print(modules)
with open(os.path.join(OUTPUT_DIRECTORY, 'modules', 'json', 'modules.json'), 'w') as output_file:
    json.dump(modules, output_file)

print('\nfound occurences for these modules:')
# figure out which modules we have, and which occurences of each module
modules2occurences = get_module_occurence_dict(dataframes)
print(modules2occurences)
with open(os.path.join(OUTPUT_DIRECTORY, 'modules', 'json', 'module-occurences.json'), 'w') as output_file:
    json.dump(modules2occurences, output_file)

print('\n\nwriting reduced data for modules')
# reduce the data for each module and write out
for module in tqdm(modules2occurences.keys()):
    for occurence in tqdm(modules2occurences[module]):
        module_data = get_module_and_occurence_data(dataframes, [module], occurence)
        module_data_reduced = convert_to_likert_reduce_transpose_and_name_index_with_count(module_data, 'question')
        with open(os.path.join(OUTPUT_DIRECTORY, 'modules', 'csv', construct_filename_identifier_and_occurence(module, occurence)), 'w') as output_file:
            module_data_reduced.to_csv(output_file)


print('\nfound data for these lecturers:')
# figure out which lecturer data we have
lecturers = get_lecturer_list(dataframes)
print(lecturers)
with open(os.path.join(OUTPUT_DIRECTORY, 'lecturers', 'json', 'lecturers.json'), 'w') as output_file:
    json.dump(lecturers, output_file)

print('\nfound data for these lecturers, modules and occurences')
lecturers2modules = {}
# figure out which lecturer goes with which module data
for lecturer in lecturers:
    lecturer_data = extract_lecturer_data(dataframes, lecturer)
    lecturer_modules = get_module_occurence_dict([lecturer_data])
    lecturers2modules[lecturer] = lecturer_modules
print(lecturers2modules)
with open(os.path.join(OUTPUT_DIRECTORY, 'lecturers', 'json', 'lecturers-modules.json'), 'w') as output_file:
    json.dump(lecturers2modules, output_file)

print('\n\nwriting reduced lecturer data')
# reduce the data for each lecturer, and each module for each lecturer, and write out
for lecturer in tqdm(lecturers2modules.keys()):
    lecturer_data = extract_lecturer_data(dataframes, lecturer)
    lecturer_data_reduced = convert_to_likert_reduce_transpose_and_name_index_with_count(lecturer_data, 'question')

    for year in tqdm(YEARS2OCCURENCES.keys()):
        lecturer_year_data = extract_lecturer_data_for_modules_occurence(dataframes, lecturer, lecturers2modules[lecturer].keys(), YEARS2OCCURENCES[year])
        lecturer_year_data_reduced = convert_to_likert_reduce_transpose_and_name_index_with_count(lecturer_year_data, 'question')

        with open(os.path.join(OUTPUT_DIRECTORY, 'lecturers', 'csv', construct_filename_identifier_and_occurence(lecturer, year)), 'w') as output_file:
            lecturer_year_data_reduced.to_csv(output_file)

    for module in lecturers2modules[lecturer].keys():
        for occurence in lecturers2modules[lecturer][module]:
            lecturer_module_data = extract_lecturer_data_for_modules_occurence(dataframes, lecturer, [module], occurence)
            lecturer_module_data_reduced = convert_to_likert_reduce_transpose_and_name_index_with_count(lecturer_module_data, 'question')
            with open(os.path.join(OUTPUT_DIRECTORY, 'lecturers', 'csv', construct_filename_lecturer_module_occurence(lecturer, module, occurence)), 'w') as output_file:
                lecturer_module_data_reduced.to_csv(output_file)


print('\n\nwriting year and subset data')
# reduce the data for each subset of modules and write out
for year in tqdm(YEARS2OCCURENCES.keys()):
    year_data = get_module_and_occurence_data(dataframes, modules, YEARS2OCCURENCES[year])
    year_data_reduced = convert_to_likert_reduce_transpose_and_name_index_with_count(year_data, 'question')

    with open(os.path.join(OUTPUT_DIRECTORY, 'subsets', 'csv', construct_filename_identifier_and_occurence('Year-Data - All modules', year)), 'w') as output_file:
        year_data_reduced.to_csv(output_file)

    year_data_with_lecturers = get_module_and_occurence_data_with_lecturer(dataframes, modules, YEARS2OCCURENCES[year])
    lecturer_year_data = combine_lecturer_data([year_data_with_lecturers], lecturers)
    lecturer_year_data_reduced = convert_to_likert_reduce_transpose_and_name_index_with_count(lecturer_year_data, 'question')

    with open(os.path.join(OUTPUT_DIRECTORY, 'subsets', 'csv', construct_filename_identifier_and_occurence('Year-Data - All lecturers', year)), 'w') as output_file:
        lecturer_year_data_reduced.to_csv(output_file)

    for subset in tqdm(SUBSETS):
        subset_data = get_module_and_occurence_data(dataframes, subset['subset'], YEARS2OCCURENCES[year])
        subset_data_reduced = convert_to_likert_reduce_transpose_and_name_index_with_count(subset_data, 'question')

        with open(os.path.join(OUTPUT_DIRECTORY, 'subsets', 'csv', construct_filename_identifier_and_occurence(subset['title'], year)), 'w') as output_file:
            subset_data_reduced.to_csv(output_file)

        subset_data_with_lecturers = get_module_and_occurence_data_with_lecturer(dataframes, subset['subset'], YEARS2OCCURENCES[year])
        subset_data_with_lecturers = combine_lecturer_data([subset_data_with_lecturers], lecturers)
        subset_data_with_lecturers_reduced = convert_to_likert_reduce_transpose_and_name_index_with_count(subset_data_with_lecturers, 'question')

        with open(os.path.join(OUTPUT_DIRECTORY, 'subsets', 'csv', construct_filename_identifier_and_occurence('%s - All lecturers' % subset['title'], year)), 'w') as output_file:
            subset_data_with_lecturers_reduced.to_csv(output_file)
