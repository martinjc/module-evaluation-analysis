import os
import pandas

from module_evaluation.analysis import MODULE_COLUMNS, LIKERT


def combine_module_evaluation_data(dataframes):

    # combine the data frames into one, dropping any NaNs
    all_module_data_frames = []
    for df in dataframes:
        ad_f = df[MODULE_COLUMNS].dropna()
        all_module_data_frames.append(ad_f)
    all_module_data = pandas.concat(all_module_data_frames)

    return all_module_data



def generate_module_mean_comparison(all_module_data):

    module_comparison = pandas.DataFrame(index=MODULE_COLUMNS)
    data_by_module = all_module_data.groupby('Module')
    module_comparison['AllModules'] = all_module_data.mean()

    for module in data_by_module.groups():
        module_data = data_by_module.get_group(module)
        del module_data['Module']
        module_comparison[module] = module_data.mean()

    return module_comparison
