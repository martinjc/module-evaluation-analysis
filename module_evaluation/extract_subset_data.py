import os
import pandas

from tqdm import tqdm

from module_evaluation.config import *
from module_evaluation.io_utils import *
from module_evaluation.data_transform import *
from module_evaluation.extract_module_data import *
from module_evaluation.extract_lecturer_data import *

def extract_and_write_year_and_subset_data(dataframes):

    module_columns = get_module_columns(dataframes)
    lecturer_columns = get_lecturer_columns(dataframes)

    module_comparison_data = {}
    lecturer_comparison_data = {}
    for year in YEARS2OCCURENCES.keys():
        module_comparison_data[year] = pandas.DataFrame(index=module_columns)
        lecturer_comparison_data[year] = pandas.DataFrame(index=lecturer_columns)

    print('\n\nwriting year and subset data')
    # reduce the data for each subset of modules and write out
    for year in tqdm(YEARS2OCCURENCES.keys()):
        year_data = get_module_and_occurence_data(dataframes, get_module_list(dataframes), YEARS2OCCURENCES[year])
        year_data_reduced = convert_to_likert_and_reduce(year_data)
        year_data_reduced = transpose_and_name_index(year_data_reduced, 'question')

        if not year_data_reduced.empty:
            module_comparison_data[year]['All Modules'] = year_data_reduced['Agree']
            with open(os.path.join(OUTPUT_DIRECTORY, 'subsets', 'csv', construct_filename_identifier_and_occurence('Year-Data - All modules', year)), 'w') as output_file:
                year_data_reduced.to_csv(output_file)

        year_data_with_lecturers = get_module_and_occurence_data_with_lecturer(dataframes, get_module_list(dataframes), YEARS2OCCURENCES[year])
        lecturer_year_data = combine_lecturer_data([year_data_with_lecturers], get_lecturer_list(dataframes))
        lecturer_year_data_reduced = transform_for_output(lecturer_year_data, 'question')

        if not lecturer_year_data_reduced.empty:
            lecturer_comparison_data[year]['All Lecturers'] = lecturer_year_data_reduced['Agree']
            with open(os.path.join(OUTPUT_DIRECTORY, 'subsets', 'csv', construct_filename_identifier_and_occurence('Year-Data - All lecturers', year)), 'w') as output_file:
                lecturer_year_data_reduced.rename(index = lambda x:  x.replace(': ', ''), inplace=True)
                lecturer_year_data_reduced.to_csv(output_file)

        for subset in tqdm(SUBSETS):
            subset_data = get_module_and_occurence_data(dataframes, subset['subset'], YEARS2OCCURENCES[year])
            subset_data_reduced = transform_for_output(subset_data, 'question')

            if not subset_data_reduced.empty:
                module_comparison_data[year][subset['title']] = subset_data_reduced['Agree']
                with open(os.path.join(OUTPUT_DIRECTORY, 'subsets', 'csv', construct_filename_identifier_and_occurence(subset['title'], year)), 'w') as output_file:
                    subset_data_reduced.to_csv(output_file)

            subset_data_with_lecturers = get_module_and_occurence_data_with_lecturer(dataframes, subset['subset'], YEARS2OCCURENCES[year])
            subset_data_with_lecturers = combine_lecturer_data([subset_data_with_lecturers], get_lecturer_list(dataframes))
            subset_data_with_lecturers_reduced = transform_for_output(subset_data_with_lecturers, 'question')

            if not subset_data_with_lecturers_reduced.empty:
                lecturer_comparison_data[year][subset['title']] = subset_data_with_lecturers_reduced['Agree']
                with open(os.path.join(OUTPUT_DIRECTORY, 'subsets', 'csv', construct_filename_identifier_and_occurence('%s - All lecturers' % subset['title'], year)), 'w') as output_file:
                    subset_data_with_lecturers_reduced.rename(index = lambda x:  x.replace(': ', ''), inplace=True)
                    subset_data_with_lecturers_reduced.to_csv(output_file)

        with open(os.path.join(OUTPUT_DIRECTORY, 'lecturers', 'csv', construct_filename_identifier_and_occurence('Lecturer Year and Subset Comparison', year)), 'w') as output_file:
            lecturer_comparison_data[year].rename(index = lambda x:  x.replace(': ', ''), inplace=True)
            lecturer_comparison_data[year].index.name = 'question'
            lecturer_comparison_data[year].to_csv(output_file)
        with open(os.path.join(OUTPUT_DIRECTORY, 'modules', 'csv', construct_filename_identifier_and_occurence('Module Year and Subset Comparison', year)), 'w') as output_file:
            module_comparison_data[year].index_name = 'question'
            module_comparison_data[year].to_csv(output_file)
