import os
import pandas

from module_evaluation.analysis import MODULE_COLUMNS, LIKERT

"""

Takes a list of dataframes containing the results of module evaluation tasks
and pulls out the results for each module as a set of csvs.

Produces:

module_count.csv
        the number of responses for each module in the supplied dataframes

module_percent_agreement_comparison.csv
        the percentage agreement for each question for each module, along
        with the average over all modules in the supplied dataframes

<module>_percent_scores.csv
        the percentage scores for each Likert value for each question
        generated for each module in the supplied dataframes

<module>_percent_agreement_comparison.csv
        the percentage agreement for each question, along with the average
        over all modules in the supplied dataframes, generated per module

"""


def combine_module_evaluation_data(dataframes):

    # combine the data frames into one, dropping any NaNs
    all_module_data_frames = []
    for df in dataframes:
        ad_f = df[MODULE_COLUMNS].dropna()
        all_module_data_frames.append(ad_f)
    all_module_data = pandas.concat(all_module_data_frames)

    return all_module_data


def convert_to_likert_and_reduce(module_data):
    # don't need 'Module' column
    if 'Module' in module_data.columns:
        del module_data['Module']

    module_data_counts = module_data.apply(lambda x: x.value_counts(normalize=True))
    new_index = [LIKERT[value] for value in LIKERT.keys() if value in module_data_counts.index]
    module_data_counts.index = new_index
    module_data_counts.fillna(0, inplace=True)
    module_data_counts = module_data_counts.reset_index().replace({'index': {'Disagree Strongly':'Disagree', 'Agree Strongly': 'Agree'}}).groupby('index', sort=False).sum()

    return module_data_counts


def get_module_count(all_module_data):

    data_by_module = all_module_data.groupby('Module')
    module_count = pandas.Series(index=data_by_module.groups.keys())

    for module in data_by_module.groups:
        module_data = data_by_module.get_group(module).dropna(axis=1, how='all')
        module_count[module] = len(module_data.index)

    return module_count


def transpose_and_name_index(module_data, index_name):

    module_data_T = module_data.T
    module_data_T.index.name = index_name
    return module_data_T


def generate_module_mean_comparison(all_module_data):

    module_comparison = pandas.DataFrame(index=MODULE_COLUMNS)
    data_by_module = all_module_data.groupby('Module')
    module_comparison['AllModules'] = all_module_data.mean()

    for module in data_by_module.groups():
        module_data = data_by_module.get_group(module)
        del module_data['Module']
        module_comparison[module] = module_data.mean()

    return module_comparison
