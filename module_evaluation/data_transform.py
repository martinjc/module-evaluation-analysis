import os
import pandas

from module_evaluation.analysis import LIKERT

def convert_to_likert_and_reduce(data):
    # don't need 'Module' column
    if 'Module' in data.columns:
        del data['Module']

    data_counts = data.apply(lambda x: x.value_counts(normalize=True))
    new_index = [LIKERT[value] for value in LIKERT.keys() if value in data_counts.index]
    data_counts.index = new_index
    data_counts.fillna(0, inplace=True)
    data_counts = data_counts.reset_index().replace({'index': {'Disagree Strongly':'Disagree', 'Agree Strongly': 'Agree'}}).groupby('index', sort=False).sum()
    return data_counts


def transpose_and_name_index(data, index_name):
    data_T = data.T
    data_T.index.name = index_name
    return data_T


def read_input_dataframes(input_dir):
    input_files = [f for f in os.listdir(input_dir) if f.endswith('.xlsx')]
    dataframes = [pandas.read_excel(os.path.join(input_dir, f)) for f in input_files]
    return dataframes


def get_module_count(all_data):

    data_by_module = all_data.groupby('Module')
    module_count = pandas.Series(index=data_by_module.groups.keys())

    for module in data_by_module.groups:
        module_data = data_by_module.get_group(module).dropna(axis=1, how='all')
        module_count[module] = len(module_data.index)

    return module_count