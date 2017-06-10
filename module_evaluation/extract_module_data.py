import os
import json
import pandas

from tqdm import tqdm

from collections import defaultdict

from module_evaluation.config import *
from module_evaluation.io_utils import *
from module_evaluation.data_transform import *


def get_module_occurence_dict(dataframes):

    modules = defaultdict(list)
    for df in dataframes:
        if 'Module' in df.columns:
            df_modules = df['Module'].unique()
            for m in df_modules:
                m, o = m.split('/')
                modules[m].append(o)
    return modules


def get_module_list(dataframes):

    modules = []
    for df in dataframes:
        if 'Module' in df.columns:
            df_modules = df['Module'].unique()
            for m in df_modules:
                m, o = m.split('/')
                modules.append(m)
    return modules

def get_module_columns(dataframes):

    all_module_data = combine_module_evaluation_data(dataframes)
    if 'Module' in all_module_data.columns:
        del all_module_data['Module']
    return all_module_data.columns

def combine_module_evaluation_data(dataframes):

    # combine the data frames into one, dropping any NaNs
    all_module_data_frames = []
    for df in dataframes:
        # lecturer specific columns contain ':'
        non_lecturer_columns = [c for c in df.columns if c.find(':') == -1]
        ad_f = df[non_lecturer_columns].dropna()
        all_module_data_frames.append(ad_f)
    all_module_data = pandas.concat(all_module_data_frames)
    return all_module_data


def get_module_and_occurence_data_with_lecturer(dataframes, modules, occurence):

    all_module_data_frames = []
    for df in dataframes:

        all_module_data_frames.append(df.loc[df['Module'].isin(['%s/%s' % (module, occurence) for module in modules])])

    all_module_data = pandas.concat(all_module_data_frames)

    return all_module_data



def get_module_and_occurence_data(dataframes, modules, occurence):

    all_module_data_frames = []
    for df in dataframes:
        # lecturer specific columns contain ':'
        non_lecturer_columns = [c for c in df.columns if c.find(':') == -1]
        ad_f = df[non_lecturer_columns].dropna()
        all_module_data_frames.append(ad_f.loc[ad_f['Module'].isin(['%s/%s' % (module, occurence) for module in modules])])

    all_module_data = pandas.concat(all_module_data_frames)
    all_module_data.dropna(axis=1, inplace=True)
    return all_module_data


def extract_and_write_module_data(dataframes):

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

    module_columns = get_module_columns(dataframes)
    module_comparison_data = {}
    for year in YEARS2OCCURENCES.keys():
        module_comparison_data[year] = pandas.DataFrame(index=module_columns)

    module_counts = {}
    for year in YEARS2OCCURENCES.keys():
        module_counts[year] = pandas.DataFrame()

    print('\n\nwriting reduced data for modules')
    # reduce the data for each module and write out
    for module in tqdm(modules2occurences.keys()):

        for year in tqdm(YEARS2OCCURENCES.keys()):
            module_data = get_module_and_occurence_data(dataframes, [module], YEARS2OCCURENCES[year])
            module_data_reduced = transform_for_output(module_data, 'question')

            module_counts[year].set_value(module, 'Count', len(module_data.index))

            if not module_data_reduced.empty:
                if 'Agree' in module_data_reduced.columns:
                    module_comparison_data[year][module] = module_data_reduced['Agree']
                with open(os.path.join(OUTPUT_DIRECTORY, 'modules', 'csv', construct_filename_identifier_and_occurence(module, year)), 'w') as output_file:
                    module_data_reduced.to_csv(output_file)

    for year in YEARS2OCCURENCES.keys():
        with open(os.path.join(OUTPUT_DIRECTORY, 'modules', 'csv', construct_filename_identifier_and_occurence('Module Count', year)),'w') as output_file:
            module_counts[year].to_csv(output_file)
        with open(os.path.join(OUTPUT_DIRECTORY, 'modules', 'csv', construct_filename_identifier_and_occurence('Module Comparison', year)), 'w') as output_file:
            module_comparison_data[year].index_name = 'question'
            module_comparison_data[year].to_csv(output_file)

    return modules2occurences
