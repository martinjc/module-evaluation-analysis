import os
import pandas

from module_evaluation.config import LIKERT, EXCLUDE_COLUMNS, COLUMN_MAPPINGS

def transform_for_output(data, index_title):
    data = convert_to_likert_and_reduce(data)
    return transpose_and_name_index(data, index_title)

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


def transpose_and_name_index(data, index_title):
    data_T = data.T
    data_T.index.name = index_title
    return data_T


def read_input_dataframes(input_dir):
    input_files = [f for f in os.listdir(input_dir) if f.endswith('.xlsx')]
    dataframes = [pandas.read_excel(os.path.join(input_dir, f)) for f in input_files]
    # remove columns we don't care about
    for df in dataframes:
        for column in EXCLUDE_COLUMNS:
            if column in df.columns:
                del df[column]
        # remove any unneccesary punctuation in column names
        df.rename(columns = lambda x:  x.replace('.', ''), inplace=True)
        # replace any questions with their proper labels
        df.rename(columns=COLUMN_MAPPINGS, inplace=True)
        # remove the occurence data from the module value
        df['Module'] = df['Module'].apply(lambda x : x.split('/')[0])
    return dataframes


def get_module_count(all_data):

    data_by_module = all_data.groupby('Module')
    module_count = pandas.Series(index=data_by_module.groups.keys())

    for module in data_by_module.groups:
        module_data = data_by_module.get_group(module).dropna(axis=1, how='all')
        module_count[module] = len(module_data.index)

    return module_count
