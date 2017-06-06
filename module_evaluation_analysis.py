import os
import json
import pandas

from tqdm import tqdm
from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader

from module_evaluation.config import *
from module_evaluation.io_utils import *
from module_evaluation.data_transform import *
from module_evaluation.extract_module_data import *
from module_evaluation.extract_lecturer_data import *


TEMPLATE_PATH = os.path.join(os.getcwd(), 'templates')
TEMPLATE_ENVIRONMENT = Environment(autoescape=False, loader=FileSystemLoader(TEMPLATE_PATH), trim_blocks=False)
TEMPLATE_FILES = ['style.css', 'evaluation_pie.js', 'against_average.js']

INPUT_DIRECTORY = 'input'
BUILD_DIR = os.path.join(os.getcwd(), 'build')
OUTPUT_DIRECTORY = os.path.join(os.getcwd(), 'output')

def render_template(template_filename, context):
    return TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)

def initialise_directories():
    # Create all the directories we'll need for output
    for directory in ['lecturers', 'modules', 'subsets']:
        for datatype in ['csv', 'pdf', 'json']:
            to_create = os.path.join(OUTPUT_DIRECTORY, directory, datatype)
            if not os.path.exists(to_create):
                os.makedirs(to_create)

def read_input_files():
    # Read in all the data we have
    dataframes = []

    print('\nreading input data')

    for year in YEARS2OCCURENCES.keys():
        input_folder = os.path.join(os.getcwd(), INPUT_DIRECTORY, year)
        print(input_folder)
        dataframes.extend(read_input_dataframes(input_folder))
    return dataframes


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

    print('\n\nwriting reduced data for modules')
    # reduce the data for each module and write out
    for module in tqdm(modules2occurences.keys()):
        for year in tqdm(YEARS2OCCURENCES.keys()):
            module_data = get_module_and_occurence_data(dataframes, [module], YEARS2OCCURENCES[year])
            module_data_reduced = convert_to_likert_reduce_transpose_and_name_index_with_count(module_data, 'question')
            if not module_data_reduced.empty:
                if 'Agree' in module_data_reduced.columns:
                    module_comparison_data[year][module] = module_data_reduced['Agree']
                with open(os.path.join(OUTPUT_DIRECTORY, 'modules', 'csv', construct_filename_identifier_and_occurence(module, YEARS2OCCURENCES[year])), 'w') as output_file:
                    module_data_reduced.to_csv(output_file)

    for year in YEARS2OCCURENCES.keys():
        with open(os.path.join(OUTPUT_DIRECTORY, 'modules', 'csv', construct_filename_identifier_and_occurence('Module Comparison', year)), 'w') as output_file:
            module_comparison_data[year].index_name = 'question'
            module_comparison_data[year].to_csv(output_file)

    return modules2occurences


def extract_and_write_lecturer_data(dataframes):

    print('\nfound data for these lecturers:')
    # figure out which lecturer data we have
    lecturers = get_lecturer_list(dataframes)
    print(lecturers)
    with open(os.path.join(OUTPUT_DIRECTORY, 'lecturers', 'json', 'lecturers.json'), 'w') as output_file:
        json.dump(lecturers, output_file)

    lecturers2modules = {}
    # figure out which lecturer goes with which module data
    for lecturer in lecturers:
        lecturer_data = extract_lecturer_data(dataframes, lecturer)
        lecturer_modules = get_module_occurence_dict([lecturer_data])
        lecturers2modules[lecturer] = lecturer_modules
    with open(os.path.join(OUTPUT_DIRECTORY, 'lecturers', 'json', 'lecturers-modules.json'), 'w') as output_file:
        json.dump(lecturers2modules, output_file)

    lecturer_columns = get_lecturer_columns(dataframes)

    lecturer_comparison_data = {}
    for year in YEARS2OCCURENCES.keys():
        lecturer_comparison_data[year] = pandas.DataFrame(index=lecturer_columns)

    print('\n\nwriting reduced lecturer data')
    # reduce the data for each lecturer, and each module for each lecturer, and write out
    for lecturer in tqdm(lecturers2modules.keys()):
        lecturer_data = extract_lecturer_data(dataframes, lecturer)
        lecturer_data_reduced = convert_to_likert_reduce_transpose_and_name_index_with_count(lecturer_data, 'question')

        for year in tqdm(YEARS2OCCURENCES.keys()):
            lecturer_year_data = extract_lecturer_data_for_modules_occurence(dataframes, lecturer, lecturers2modules[lecturer].keys(), YEARS2OCCURENCES[year])
            lecturer_year_data_reduced = convert_to_likert_reduce_transpose_and_name_index_with_count(lecturer_year_data, 'question')
            if not lecturer_year_data_reduced.empty:
                if 'Agree' in lecturer_year_data_reduced.columns:
                    lecturer_comparison_data[year][lecturer] = lecturer_year_data_reduced['Agree']
                with open(os.path.join(OUTPUT_DIRECTORY, 'lecturers', 'csv', construct_filename_identifier_and_occurence(lecturer, year)), 'w') as output_file:
                    lecturer_year_data_reduced.rename(index = lambda x:  x.replace(': ', ''), inplace=True)
                    lecturer_year_data_reduced.to_csv(output_file)

        for module in lecturers2modules[lecturer].keys():
            for occurence in lecturers2modules[lecturer][module]:
                lecturer_module_data = extract_lecturer_data_for_modules_occurence(dataframes, lecturer, [module], occurence)
                lecturer_module_data_reduced = convert_to_likert_reduce_transpose_and_name_index_with_count(lecturer_module_data, 'question')
                if not lecturer_module_data_reduced.empty:
                    with open(os.path.join(OUTPUT_DIRECTORY, 'lecturers', 'csv', construct_filename_lecturer_module_occurence(lecturer, module, occurence)), 'w') as output_file:
                        lecturer_module_data_reduced.rename(index = lambda x:  x.replace(': ', ''), inplace=True)
                        lecturer_module_data_reduced.to_csv(output_file)

    for year in YEARS2OCCURENCES.keys():
        with open(os.path.join(OUTPUT_DIRECTORY, 'lecturers', 'csv', construct_filename_identifier_and_occurence('Lecturer Comparison', year)), 'w') as output_file:
            lecturer_comparison_data[year].index_name = 'question'
            lecturer_comparison_data[year].rename(index = lambda x:  x.replace(': ', ''), inplace=True)
            lecturer_comparison_data[year].to_csv(output_file)

    return lecturers2modules


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
        year_data_reduced = convert_to_likert_reduce_transpose_and_name_index_with_count(year_data, 'question')

        if not year_data_reduced.empty:
            module_comparison_data[year]['All Modules'] = year_data_reduced['Agree']
            with open(os.path.join(OUTPUT_DIRECTORY, 'subsets', 'csv', construct_filename_identifier_and_occurence('Year-Data - All modules', year)), 'w') as output_file:
                year_data_reduced.to_csv(output_file)

        year_data_with_lecturers = get_module_and_occurence_data_with_lecturer(dataframes, get_module_list(dataframes), YEARS2OCCURENCES[year])
        lecturer_year_data = combine_lecturer_data([year_data_with_lecturers], get_lecturer_list(dataframes))
        lecturer_year_data_reduced = convert_to_likert_reduce_transpose_and_name_index_with_count(lecturer_year_data, 'question')

        if not lecturer_year_data_reduced.empty:
            lecturer_comparison_data[year]['All Lecturers'] = lecturer_year_data_reduced['Agree']
            with open(os.path.join(OUTPUT_DIRECTORY, 'subsets', 'csv', construct_filename_identifier_and_occurence('Year-Data - All lecturers', year)), 'w') as output_file:
                lecturer_year_data_reduced.to_csv(output_file)

        for subset in tqdm(SUBSETS):
            subset_data = get_module_and_occurence_data(dataframes, subset['subset'], YEARS2OCCURENCES[year])
            subset_data_reduced = convert_to_likert_reduce_transpose_and_name_index_with_count(subset_data, 'question')

            if not subset_data_reduced.empty:
                module_comparison_data[year][subset['title']] = subset_data_reduced['Agree']
                with open(os.path.join(OUTPUT_DIRECTORY, 'subsets', 'csv', construct_filename_identifier_and_occurence(subset['title'], year)), 'w') as output_file:
                    subset_data_reduced.to_csv(output_file)

            subset_data_with_lecturers = get_module_and_occurence_data_with_lecturer(dataframes, subset['subset'], YEARS2OCCURENCES[year])
            subset_data_with_lecturers = combine_lecturer_data([subset_data_with_lecturers], get_lecturer_list(dataframes))
            subset_data_with_lecturers_reduced = convert_to_likert_reduce_transpose_and_name_index_with_count(subset_data_with_lecturers, 'question')

            if not subset_data_with_lecturers_reduced.empty:
                lecturer_comparison_data[year][subset['title']] = subset_data_with_lecturers_reduced['Agree']
                with open(os.path.join(OUTPUT_DIRECTORY, 'subsets', 'csv', construct_filename_identifier_and_occurence('%s - All lecturers' % subset['title'], year)), 'w') as output_file:
                    subset_data_with_lecturers_reduced.to_csv(output_file)

        with open(os.path.join(OUTPUT_DIRECTORY, 'lecturers', 'csv', construct_filename_identifier_and_occurence('Lecturer Year and Subset Comparison', year)), 'w') as output_file:
            lecturer_comparison_data[year].index_name = 'question'
            lecturer_comparison_data[year].rename(index = lambda x:  x.replace(': ', ''), inplace=True)
            lecturer_comparison_data[year].to_csv(output_file)
        with open(os.path.join(OUTPUT_DIRECTORY, 'modules', 'csv', construct_filename_identifier_and_occurence('Module Year and Subset Comparison', year)), 'w') as output_file:
            module_comparison_data[year].index_name = 'question'
            module_comparison_data[year].to_csv(output_file)

def construct_templates(dataframes):

    # figure out which lecturer data we have
    lecturers = get_lecturer_list(dataframes)

    lecturers2modules = {}
    # figure out which lecturer goes with which module data
    for lecturer in lecturers:
        lecturer_data = extract_lecturer_data(dataframes, lecturer)
        lecturer_modules = get_module_occurence_dict([lecturer_data])
        lecturers2modules[lecturer] = lecturer_modules

    print(lecturers2modules)
    for year in YEARS2OCCURENCES.keys():
        for lecturer, modules in lecturers2modules.items():

            context = {}
            context['data'] = {}
            context['year'] = year

            if os.path.exists(os.path.join(OUTPUT_DIRECTORY, 'lecturers', 'csv', construct_filename_identifier_and_occurence(lecturer, year))):
                with open(os.path.join(OUTPUT_DIRECTORY, 'lecturers', 'csv', construct_filename_identifier_and_occurence(lecturer, year))) as input_file:
                    df = pandas.read_csv(input_file, index_col=0)
                    context['data']['overall'] = df.to_csv()
            if len(modules) > 1:
                for module in modules:
                    if os.path.exists(os.path.join(OUTPUT_DIRECTORY, 'lecturers', 'csv', construct_filename_lecturer_module_occurence(lecturer, module, YEARS2OCCURENCES[year]))):
                        with open(os.path.join(OUTPUT_DIRECTORY, 'lecturers', 'csv', construct_filename_lecturer_module_occurence(lecturer, module, YEARS2OCCURENCES[year]))) as input_file:
                            df = pandas.read_csv(input_file, index_col=0)
                            context['data'][module] = df.to_csv()
            if os.path.exists(os.path.join(OUTPUT_DIRECTORY, 'lecturers', 'csv', construct_filename_identifier_and_occurence('Lecturer Year and Subset Comparison', year))):
                with open(os.path.join(OUTPUT_DIRECTORY, 'lecturers', 'csv', construct_filename_identifier_and_occurence('Lecturer Year and Subset Comparison', year))) as input_file:
                    df = pandas.read_csv(input_file, index_col=0)
                    context['data']['subsets'] = df.to_csv()

            print(context)

            fpath = os.path.join(BUILD_DIR, '%s_report_lecturer.html' % (lecturer))

            with open(fpath, 'w') as f:
                html = render_template('lecturer_evaluation_analysis.html', context)
                f.write(html)


if __name__ == '__main__':
    initialise_directories()
    dataframes = read_input_files()
    modules2occurences = extract_and_write_module_data(dataframes)
    lecturers2modules = extract_and_write_lecturer_data(dataframes)
    extract_and_write_year_and_subset_data(dataframes)
    construct_templates(dataframes)
