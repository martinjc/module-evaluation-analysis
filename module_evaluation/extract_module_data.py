import os
import pandas

from collections import defaultdict

from module_evaluation.config import LIKERT


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




def generate_module_mean_comparison(all_module_data):

    module_comparison = pandas.DataFrame(index=all_module_data.columns)
    data_by_module = all_module_data.groupby('Module')
    module_comparison['AllModules'] = all_module_data.mean()

    for module in data_by_module.groups:
        module_data = data_by_module.get_group(module)
        del module_data['Module']
        module_comparison[module] = module_data.mean()

    module_comparison.drop('Module', inplace=True)
    return module_comparison
