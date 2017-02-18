import os
import pandas

from tqdm import tqdm

from module_evaluation.analysis import *
from module_evaluation.extract_module_data import *

INPUT_DIR = os.path.join(os.getcwd(), 'input')
OUTPUT_DIR = os.path.join(os.getcwd(), 'output')

def read_input_dataframes():
    input_files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.xlsx')]
    dataframes = [pandas.read_excel(os.path.join(INPUT_DIR, f)) for f in input_files]
    return dataframes

def generate_module_data():

    print('Reading input')
    dataframes = read_input_dataframes()

    print('Calculating scores over all modules')
    all_module_data = combine_module_evaluation_data(dataframes)
    all_module_data_counts = convert_to_likert_and_reduce(all_module_data)
    with open(os.path.join(OUTPUT_DIR, 'all_module_percent_scores.csv'), 'w') as output_file:
        all_module_data_counts.T.to_csv(output_file)

    print('Calculating number of responses per module')
    all_module_data = combine_module_evaluation_data(dataframes)
    module_counts = get_module_count(all_module_data)
    with open(os.path.join(OUTPUT_DIR, 'all_module_counts.csv'), 'w') as output_file:
        module_counts.to_csv(output_file)

    all_module_data = combine_module_evaluation_data(dataframes)
    module_comparison = pandas.DataFrame(index=[m for m in MODULE_COLUMNS if m != 'Module'])
    data_by_module = all_module_data.groupby('Module')

    module_comparison['AllModules'] = all_module_data_counts.ix['Agree']

    print('Calculating and writing per module data')
    for module in tqdm(data_by_module.groups):

            module_agreement_comparison = pandas.DataFrame(index=[m for m in MODULE_COLUMNS if m != 'Module'])

            module_data = data_by_module.get_group(module).dropna(axis=1, how='all')

            module_data_counts = convert_to_likert_and_reduce(module_data)
            module_data_counts_T = transpose_and_name_index(module_data_counts, 'question')

            module_agreement_comparison[module] = module_data_counts.ix['Agree']
            module_agreement_comparison['AllModules'] = module_comparison['AllModules']
            module_agreement_comparison.index.name = "question"

            with open(os.path.join(OUTPUT_DIR, '%s_percent_agreement_comparison.csv' % (module.replace('/', '-'))), 'w') as output_file:
                module_agreement_comparison.to_csv(output_file)

            with open(os.path.join(OUTPUT_DIR, '%s_percent_scores.csv' % (module.replace('/', '-'))), 'w') as output_file:
                module_data_counts_T.to_csv(output_file)

            module_comparison[module] = module_data_counts.ix['Agree']

    print('Writing module comparison data')
    module_comparison.index.name = 'question'
    with open(os.path.join(OUTPUT_DIR, 'all_module_percent_agreement_comparison.csv'), 'w') as output_file:
        module_comparison.to_csv(output_file)



if __name__ == '__main__':
    generate_module_data()
