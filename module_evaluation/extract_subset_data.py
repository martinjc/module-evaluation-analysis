import os
import pandas

from tqdm import tqdm

from module_evaluation.config import *
from module_evaluation.io_utils import *
from module_evaluation.data_transform import *
from module_evaluation.extract_module_data import *
from module_evaluation.extract_lecturer_data import *

def extract_and_write_year_and_subset_data(dataframes, label):

    module_columns = get_module_columns(dataframes)
    lecturer_columns = get_lecturer_columns(dataframes)

    module_comparison_data = pandas.DataFrame(index=module_columns)
    lecturer_comparison_data = pandas.DataFrame(index=lecturer_columns)

    print('\n\nwriting year and subset data')
    # reduce the data for each subset of modules and write out
    data = get_module_data(dataframes, get_module_list(dataframes))
    data_reduced = transform_for_output(data, 'question')

    if not data_reduced.empty:
        module_comparison_data['All Modules'] = data_reduced['Agree']
        with open(os.path.join(OUTPUT_DIRECTORY, 'subsets', 'csv', construct_csv_filename('Year-Data', 'All modules', label=label)), 'w') as output_file:
            data_reduced.to_csv(output_file)

        data_with_lecturers = get_module_data_with_lecturer_data(dataframes, get_module_list(dataframes))
        lecturer_data = combine_lecturer_data([data_with_lecturers], get_lecturer_list(dataframes))
        lecturer_data_reduced = transform_for_output(lecturer_data, 'question')

        if not lecturer_data_reduced.empty:
            lecturer_comparison_data['All Lecturers'] = lecturer_data_reduced['Agree']
            with open(os.path.join(OUTPUT_DIRECTORY, 'subsets', 'csv', construct_csv_filename('Year-Data', 'All lecturers', label=label)), 'w') as output_file:
                lecturer_data_reduced.rename(index = lambda x:  x.replace(': ', ''), inplace=True)
                lecturer_data_reduced.to_csv(output_file)

        for subset in tqdm(SUBSETS):
            subset_data = get_module_data(dataframes, subset['subset'])
            subset_data_reduced = transform_for_output(subset_data, 'question')

            if not subset_data_reduced.empty:
                module_comparison_data[subset['title']] = subset_data_reduced['Agree']
                with open(os.path.join(OUTPUT_DIRECTORY, 'subsets', 'csv', construct_csv_filename(subset['title'], label=label)), 'w') as output_file:
                    subset_data_reduced.to_csv(output_file)

            subset_data_with_lecturers = get_module_data_with_lecturer_data(dataframes, subset['subset'])
            subset_data_with_lecturers = combine_lecturer_data([subset_data_with_lecturers], get_lecturer_list(dataframes))
            subset_data_with_lecturers_reduced = transform_for_output(subset_data_with_lecturers, 'question')

            if not subset_data_with_lecturers_reduced.empty:
                lecturer_comparison_data[subset['title']] = subset_data_with_lecturers_reduced['Agree']
                with open(os.path.join(OUTPUT_DIRECTORY, 'subsets', 'csv', construct_csv_filename(subset['title'], 'All lecturers' , label=label)), 'w') as output_file:
                    subset_data_with_lecturers_reduced.rename(index = lambda x:  x.replace(': ', ''), inplace=True)
                    subset_data_with_lecturers_reduced.to_csv(output_file)

        with open(os.path.join(OUTPUT_DIRECTORY, 'lecturers', 'csv', construct_csv_filename('Lecturer Year and Subset Comparison', label=label)), 'w') as output_file:
            lecturer_comparison_data.rename(index = lambda x:  x.replace(': ', ''), inplace=True)
            lecturer_comparison_data.index.name = 'question'
            lecturer_comparison_data.to_csv(output_file)
        with open(os.path.join(OUTPUT_DIRECTORY, 'modules', 'csv', construct_csv_filename('Module Year and Subset Comparison', label=label)), 'w') as output_file:
            module_comparison_data.index_name = 'question'
            module_comparison_data.to_csv(output_file)
