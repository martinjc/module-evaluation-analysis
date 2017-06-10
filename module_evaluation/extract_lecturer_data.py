import os
import json
import pandas

from tqdm import tqdm

from module_evaluation.config import *
from module_evaluation.io_utils import *
from module_evaluation.data_transform import *
from module_evaluation.extract_module_data import get_module_list


def get_lecturer_list(dataframes):

    # find out which lecturers we have
    lecturers = set()
    for df in dataframes:
        lecturer_columns = [c[:c.find(':')] for c in df.columns if c.find(':') != -1]
        lecturers |= set(lecturer_columns)
    return list(lecturers)



def get_lecturer_columns(dataframes):

    lecturers = get_lecturer_list(dataframes)
    combined_data = combine_lecturer_data(dataframes, lecturers)
    if 'Module' in combined_data.columns:
        del combined_data['Module']

    return combined_data.columns



def combine_lecturer_data(dataframes, lecturers):

    all_lecturer_frames = []

    for lecturer in lecturers:

        lecturer_frames = []

        for df in dataframes:
            this_lecturer_columns = [c for c in df.columns if c.find(':') != -1 and c.find(lecturer) != -1]
            if(len(this_lecturer_columns) > 0):
                ld_f = df[['Module'] + this_lecturer_columns].dropna()
                lecturer_frames.append(ld_f)

        lecturer_data = pandas.concat(lecturer_frames)
        lecturer_data.rename(columns = lambda x:  x.replace(lecturer, ''), inplace=True)
        all_lecturer_frames.append(lecturer_data)

    all_lecturer_data = pandas.concat(all_lecturer_frames)
    return all_lecturer_data


def extract_lecturer_data_for_module(dataframes, lecturer, module):
    return extract_lecturer_data_for_modules(dataframes, lecturer, [module])

def extract_lecturer_data_for_modules(dataframes, lecturer, modules):
    lecturer_frames = []

    for df in dataframes:
        this_lecturer_columns = [c for c in df.columns if c.find(':') != -1 and c.find(lecturer) != -1]

        if(len(this_lecturer_columns) > 0):
            ld_f = df[['Module'] + this_lecturer_columns].dropna()
            lecturer_frames.append(ld_f.loc[ld_f['Module'].isin(modules)])

    lecturer_data = pandas.concat(lecturer_frames)
    lecturer_data.rename(columns = lambda x:  x.replace(lecturer, ''), inplace=True)

    return lecturer_data


def extract_lecturer_data(dataframes, lecturer):

    lecturer_frames = []

    for df in dataframes:
        this_lecturer_columns = [c for c in df.columns if c.find(':') != -1 and c.find(lecturer) != -1]

        if(len(this_lecturer_columns) > 0):
            ld_f = df[['Module'] + this_lecturer_columns].dropna()
            lecturer_frames.append(ld_f)

    lecturer_data = pandas.concat(lecturer_frames)
    lecturer_data.rename(columns = lambda x:  x.replace(lecturer, ''), inplace=True)

    return lecturer_data


def extract_and_write_lecturer_data(dataframes, label):

    # figure out which lecturer data we have
    lecturers = get_lecturer_list(dataframes)

    lecturer2modules = {}

    # figure out which lecturer goes with which module data
    for lecturer in lecturers:
        lecturer_data = extract_lecturer_data(dataframes, lecturer)
        lecturer_modules = get_module_list([lecturer_data])
        lecturer2modules[lecturer] = lecturer_modules

    lecturer_columns = get_lecturer_columns(dataframes)

    lecturer_comparison_data = pandas.DataFrame(index=lecturer_columns)

    print('\n\nwriting lecturer data')
    # reduce the data for each lecturer, and each module for each lecturer, and write out
    for lecturer, modules in tqdm(lecturer2modules.items()):

        lecturer_count = pandas.DataFrame()
        lecturer_count.index.name = 'Module'

        lecturer_data = extract_lecturer_data(dataframes, lecturer)
        lecturer_data_reduced = transform_for_output(lecturer_data, 'question')

        lecturer_count.set_value('All', 'Count', len(lecturer_data.index))

        if not lecturer_data_reduced.empty:
            if 'Agree' in lecturer_data_reduced.columns:
                lecturer_comparison_data[lecturer] = lecturer_data_reduced['Agree']
            with open(os.path.join(OUTPUT_DIRECTORY, 'lecturers', 'csv', construct_csv_filename(lecturer, label=label)), 'w') as output_file:
                lecturer_data_reduced.rename(index = lambda x:  x.replace(': ', ''), inplace=True)
                lecturer_data_reduced.to_csv(output_file)

        for module in modules:
            lecturer_module_data = extract_lecturer_data_for_module(dataframes, lecturer, module)
            lecturer_module_data_reduced = transform_for_output(lecturer_module_data, 'question')

            lecturer_count.set_value(module, 'Count', len(lecturer_module_data.index))

            if not lecturer_module_data_reduced.empty:
                with open(os.path.join(OUTPUT_DIRECTORY, 'lecturers', 'csv', construct_csv_filename(lecturer, module, label=label)), 'w') as output_file:
                    lecturer_module_data_reduced.rename(index = lambda x:  x.replace(': ', ''), inplace=True)
                    lecturer_module_data_reduced.to_csv(output_file)

        with open(os.path.join(OUTPUT_DIRECTORY, 'lecturers', 'csv', construct_csv_filename('%s Counts' % lecturer, label=label)), 'w') as output_file:
            lecturer_count.to_csv(output_file)

    with open(os.path.join(OUTPUT_DIRECTORY, 'lecturers', 'csv', construct_csv_filename('Lecturer Comparison', label=label)), 'w') as output_file:
        lecturer_comparison_data.rename(index = lambda x:  x.replace(': ', ''), inplace=True)
        lecturer_comparison_data.index.name = 'question'
        lecturer_comparison_data.to_csv(output_file)
