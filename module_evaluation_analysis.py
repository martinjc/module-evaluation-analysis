import os
import json
import pandas
import argparse

from tqdm import tqdm
from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader

from module_evaluation.config import *
from module_evaluation.io_utils import *
from module_evaluation.data_transform import *
from module_evaluation.extract_subset_data import *
from module_evaluation.extract_module_data import *
from module_evaluation.extract_lecturer_data import *


TEMPLATE_PATH = os.path.join(os.getcwd(), 'templates')
TEMPLATE_ENVIRONMENT = Environment(autoescape=False, loader=FileSystemLoader(TEMPLATE_PATH), trim_blocks=False)
TEMPLATE_FILES = ['style.css', 'evaluation_pie.js', 'against_average.js']

def render_template(template_filename, context):
    return TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)


def initialise_directories():
    # Create all the directories we'll need for output
    for directory in ['lecturers', 'modules', 'subsets']:
        for datatype in ['csv', 'pdf']:
            to_create = os.path.join(OUTPUT_DIRECTORY, directory, datatype)
            if not os.path.exists(to_create):
                os.makedirs(to_create)


def read_input_files(input_directory):
    # Read in all the data we have
    dataframes = []

    print('\nreading input data')
    dataframes.extend(read_input_dataframes(input_directory))
    return dataframes


def construct_templates(dataframes):

    # figure out which lecturer data we have
    lecturers = get_lecturer_list(dataframes)

    lecturers2modules = {}
    # figure out which lecturer goes with which module data
    for lecturer in lecturers:
        lecturer_data = extract_lecturer_data(dataframes, lecturer)
        lecturer_modules = get_module_occurence_dict([lecturer_data])
        lecturers2modules[lecturer] = lecturer_modules

    for year in YEARS2OCCURENCES.keys():
        for lecturer, modules2occurences in lecturers2modules.items():

            this_years_modules = []

            for module, occurences in modules2occurences.items():
                if YEARS2OCCURENCES[year] in occurences:
                    this_years_modules.append(module)

            context = {}
            context['data'] = {}
            context['lecturer'] = lecturer
            context['year'] = year
            context['modules'] = this_years_modules

            subsets = pandas.DataFrame()
            overall = pandas.DataFrame()
            counts = pandas.DataFrame()

            if os.path.exists(os.path.join(OUTPUT_DIRECTORY, 'lecturers', 'csv', construct_filename_identifier_and_occurence(lecturer, year))):
                with open(os.path.join(OUTPUT_DIRECTORY, 'lecturers', 'csv', construct_filename_identifier_and_occurence(lecturer, year))) as input_file:
                    overall = pandas.read_csv(input_file, index_col=0)
            if os.path.exists(os.path.join(OUTPUT_DIRECTORY, 'lecturers', 'csv', construct_filename_identifier_and_occurence('%s Counts' % lecturer, year))):
                with open(os.path.join(OUTPUT_DIRECTORY, 'lecturers', 'csv', construct_filename_identifier_and_occurence('%s Counts' % lecturer, year))) as input_file:
                    counts = pandas.read_csv(input_file, index_col=0)
            if os.path.exists(os.path.join(OUTPUT_DIRECTORY, 'lecturers', 'csv', construct_filename_identifier_and_occurence('Lecturer Year and Subset Comparison', year))):
                with open(os.path.join(OUTPUT_DIRECTORY, 'lecturers', 'csv', construct_filename_identifier_and_occurence('Lecturer Year and Subset Comparison', year))) as input_file:
                    subsets = pandas.read_csv(input_file, index_col=0)

            context['total'] = float(counts.ix['All'])
            context['data']['overall'] = overall.to_csv()
            context['data']['counts'] = counts.to_csv()
            all_subsets = set()
            all_subsets.add('All Lecturers')

            context['data']['modules'] = []
            if len(this_years_modules) > 1:
                for module in this_years_modules:
                    subsets_needed = ['All Lecturers']
                    for subset in SUBSETS:
                        if module in subset['subset']:
                            subsets_needed.append(subset['title'])
                            all_subsets.add(subset['title'])

                    if os.path.exists(os.path.join(OUTPUT_DIRECTORY, 'lecturers', 'csv', construct_filename_lecturer_module_occurence(lecturer, module, year))):
                        with open(os.path.join(OUTPUT_DIRECTORY, 'lecturers', 'csv', construct_filename_lecturer_module_occurence(lecturer, module, year))) as input_file:
                            df = pandas.read_csv(input_file, index_col=0)
                            module_data = {}
                            module_data['meta'] = {}
                            module_data['meta']['code'] = module
                            module_data['data'] = df.to_csv()
                            module_data['meta']['count'] = float(counts.ix[module])
                            module_data['meta']['subsets'] = subsets_needed
                            module_data['meta_json'] = json.dumps(module_data['meta'])
                            context['data']['modules'].append(module_data)

            context['data']['subsets'] = subsets[list(all_subsets)].to_csv()

            fpath = os.path.join(BUILD_DIR, '%s_lecturer_report - (%s).html' % (lecturer, year))

            with open(fpath, 'w') as f:
                html = render_template('lecturer_evaluation_analysis.html', context)
                f.write(html)
    # get the list of modules we have data for
    modules = get_module_list(dataframes)
    # figure out which modules we have, and which occurences of each module
    modules2occurences = get_module_occurence_dict(dataframes)
    for year in YEARS2OCCURENCES.keys():
        for module in modules:
            if YEARS2OCCURENCES[year] in modules2occurences[module]:

                module_data = pandas.DataFrame()
                counts = pandas.DataFrame()
                subsets = pandas.DataFrame()

                if os.path.exists(os.path.join(OUTPUT_DIRECTORY, 'modules', 'csv', construct_filename_identifier_and_occurence(module, year))):
                    with open(os.path.join(OUTPUT_DIRECTORY, 'modules', 'csv', construct_filename_identifier_and_occurence(module, year))) as input_file:
                        module_data = pandas.read_csv(input_file, index_col=0)
                if os.path.exists(os.path.join(OUTPUT_DIRECTORY, 'modules', 'csv', construct_filename_identifier_and_occurence('Module Count', year))):
                    with open(os.path.join(OUTPUT_DIRECTORY, 'modules', 'csv', construct_filename_identifier_and_occurence('Module Count', year))) as input_file:
                        counts = pandas.read_csv(input_file, index_col=0)
                if os.path.exists(os.path.join(OUTPUT_DIRECTORY, 'modules', 'csv', construct_filename_identifier_and_occurence('Module Year and Subset Comparison', year))):
                    with open(os.path.join(OUTPUT_DIRECTORY, 'modules', 'csv', construct_filename_identifier_and_occurence('Module Year and Subset Comparison', year))) as input_file:
                        subsets = pandas.read_csv(input_file, index_col=0)

                context = {}
                context['module'] = module
                context['data'] = {}
                context['data']['overall'] = module_data.to_csv()
                context['year'] = year
                context['count'] = float(counts.ix[module])

                if 'Agree' in module_data.columns:
                    highlights = module_data.nlargest(3, 'Agree')[0:3]
                    context['data']['highlights'] = highlights.to_csv()

                    lowlights = module_data.nsmallest(3, 'Agree')[0:3]
                    context['data']['lowlights'] = lowlights.to_csv()

                subsets_needed = set()
                subsets_needed.add('All Modules')

                for subset in SUBSETS:
                    if module in subset['subset']:
                        subsets_needed.add(subset['title'])

                meta_data = {}
                meta_data['year'] = year
                meta_data['subsets'] = list(subsets_needed)
                meta_data['count'] = float(counts.ix[module])
                context['meta_json'] = json.dumps(meta_data)
                context['data']['subsets'] = subsets[list(subsets_needed)].to_csv()

                fpath = os.path.join(BUILD_DIR, '%s_module_report - (%s).html' % (module, year))

                with open(fpath, 'w') as f:
                    html = render_template('module_evaluation_analysis.html', context)
                    f.write(html)

    for subset in SUBSETS:
        for year in YEARS2OCCURENCES.keys():

            subset_data = pandas.DataFrame()
            counts = pandas.DataFrame()
            comparison_data = pandas.DataFrame()

            if os.path.exists(os.path.join(OUTPUT_DIRECTORY, 'subsets', 'csv', construct_filename_identifier_and_occurence(subset['title'], year))):
                with open(os.path.join(OUTPUT_DIRECTORY, 'subsets', 'csv', construct_filename_identifier_and_occurence(subset['title'], year))) as input_file:
                    subset_data = pandas.read_csv(input_file, index_col=0)

            if os.path.exists(os.path.join(OUTPUT_DIRECTORY, 'modules', 'csv', construct_filename_identifier_and_occurence('Module Year and Subset Comparison', year))):
                with open(os.path.join(OUTPUT_DIRECTORY, 'modules', 'csv', construct_filename_identifier_and_occurence('Module Year and Subset Comparison', year))) as input_file:
                    comparison_data = pandas.read_csv(input_file, index_col=0)

            if os.path.exists(os.path.join(OUTPUT_DIRECTORY, 'modules', 'csv', construct_filename_identifier_and_occurence('Module Count', year))):
                with open(os.path.join(OUTPUT_DIRECTORY, 'modules', 'csv', construct_filename_identifier_and_occurence('Module Count', year))) as input_file:
                    counts = pandas.read_csv(input_file, index_col=0)

            context['title'] = subset['title']
            context['modules'] = subset['subset']
            context['year'] = year


            context['data'] = {}
            context['data']['overall'] = subset_data.to_csv()

            context['data']['agreements'] = comparison_data['All Modules'].to_csv()
            context['data']['modules'] = []

            for module in subset['subset']:

                if os.path.exists(os.path.join(OUTPUT_DIRECTORY, 'modules', 'csv', construct_filename_identifier_and_occurence(module, year))):
                    with open(os.path.join(OUTPUT_DIRECTORY, 'modules', 'csv', construct_filename_identifier_and_occurence(module, year))) as input_file:
                        df = pandas.read_csv(input_file, index_col=0)

                        module_data = {}
                        module_data['meta'] = {}
                        module_data['meta']['code'] = module
                        module_data['data'] = df.to_csv()
                        module_data['meta']['count'] = float(counts.ix[module])
                        module_data['meta_json'] = json.dumps(module_data['meta'])

                        if 'Agree' in df.columns:
                            highlights = df.nlargest(3, 'Agree')[0:3]
                            module_data['highlights'] = highlights.to_csv()

                            lowlights = df.nsmallest(3, 'Agree')[0:3]
                            module_data['lowlights'] = lowlights.to_csv()

                        context['data']['modules'].append(module_data)


            fpath = os.path.join(BUILD_DIR, '%s_subset_evaluation_analysis_report - (%s).html' % (subset['title'], year))

            with open(fpath, 'w') as f:
                html = render_template('module_subset_evaluation_analysis.html', context)
                f.write(html)






if __name__ == '__main__':


    parser = argparse.ArgumentParser(description='Analysing Module Evaluation Feedback')
    parser.add_argument('-i', '--input', help='Input directory with evaluation data', required=True, action='store')
    parser.add_argument('-l', '--label', help='Label to add to output filenames', required=False, action='store', default='')
    args = parser.parse_args()

    initialise_directories()

    input_directory = os.path.join(os.getcwd(), args.input)
    label = args.label

    dataframes = read_input_files(input_directory)

    extract_and_write_module_data(dataframes, label)
    extract_and_write_lecturer_data(dataframes, label)
    extract_and_write_year_and_subset_data(dataframes, label)

    construct_templates(dataframes)
