import os
import json
import pandas

from tqdm import tqdm

from collections import defaultdict

from module_evaluation.config import *
from module_evaluation.io_utils import *
from module_evaluation.data_transform import *

def get_module_list(dataframes):

    modules = []
    for df in dataframes:
        if 'Module' in df.columns:
            df_modules = df['Module'].unique()
            modules.extend(df_modules)
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
    all_module_data = pandas.concat(all_module_data_frames, sort=False)
    return all_module_data


def get_module_data_with_lecturer_data(dataframes, modules):

    all_module_data_frames = []
    for df in dataframes:
        all_module_data_frames.append(df.loc[df['Module'].isin(modules)])
    all_module_data = pandas.concat(all_module_data_frames, sort=False)
    return all_module_data



def get_module_data(dataframes, modules):

    all_module_data_frames = []
    for df in dataframes:
        # lecturer specific columns contain ':'
        non_lecturer_columns = [c for c in df.columns if c.find(':') == -1]
        ad_f = df[non_lecturer_columns].dropna()
        all_module_data_frames.append(ad_f.loc[ad_f['Module'].isin(modules)])

    all_module_data = pandas.concat(all_module_data_frames, sort=False)
    all_module_data.dropna(axis=1, inplace=True)
    return all_module_data


def extract_and_write_module_data(dataframes, label):

    # get the list of modules we have data for
    modules = get_module_list(dataframes)

    # work out which columns we have
    module_columns = get_module_columns(dataframes)

    # store a comparison of the percentage agreement for each module
    module_comparison_data = pandas.DataFrame(index=module_columns)

    # store a count of the number of responses for each module
    module_counts = pandas.DataFrame()


    print('\n\nwriting data for modules')
    # reduce the data for each module and write out
    for module in tqdm(modules):
        module_data = get_module_data(dataframes, [module])

        module_data_reduced = transform_for_output(module_data, 'question')

        module_counts.at[module, 'Count'] = len(module_data.index)

        if not module_data_reduced.empty:
            if 'Agree' in module_data_reduced.columns:
                module_comparison_data[module] = module_data_reduced['Agree']
            with open(os.path.join(OUTPUT_DIRECTORY, 'modules', 'csv', construct_csv_filename(module, label=label)), 'w') as output_file:
                module_data_reduced.to_csv(output_file)

    with open(os.path.join(OUTPUT_DIRECTORY, 'modules', 'csv', construct_csv_filename('Module Count', label=label)),'w') as output_file:
        module_counts.to_csv(output_file)
    with open(os.path.join(OUTPUT_DIRECTORY, 'modules', 'csv', construct_csv_filename('Module Comparison', label=label)), 'w') as output_file:
        module_comparison_data.index_name = 'question'
        module_comparison_data.to_csv(output_file)
