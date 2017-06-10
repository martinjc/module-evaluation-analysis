import os
import json
import pandas
import shutil
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


def construct_module_templates(dataframes, label):
    # get the list of modules we have data for
    modules = get_module_list(dataframes)

    print('\n\nWriting Module templates')
    for module in tqdm(modules):

        module_data = pandas.DataFrame()
        counts = pandas.DataFrame()
        subsets = pandas.DataFrame()

        if os.path.exists(os.path.join(OUTPUT_DIRECTORY, 'modules', 'csv', construct_csv_filename(module, label=label))):
            with open(os.path.join(OUTPUT_DIRECTORY, 'modules', 'csv', construct_csv_filename(module, label=label))) as input_file:
                module_data = pandas.read_csv(input_file, index_col=0)
        if os.path.exists(os.path.join(OUTPUT_DIRECTORY, 'modules', 'csv', construct_csv_filename('Module Count', label=label))):
            with open(os.path.join(OUTPUT_DIRECTORY, 'modules', 'csv', construct_csv_filename('Module Count', label=label))) as input_file:
                counts = pandas.read_csv(input_file, index_col=0)
        if os.path.exists(os.path.join(OUTPUT_DIRECTORY, 'modules', 'csv', construct_csv_filename('Module Year and Subset Comparison', label=label))):
            with open(os.path.join(OUTPUT_DIRECTORY, 'modules', 'csv', construct_csv_filename('Module Year and Subset Comparison', label=label))) as input_file:
                subsets = pandas.read_csv(input_file, index_col=0)

        context = {}
        context['module'] = module
        context['data'] = {}
        context['data']['overall'] = module_data.to_csv()
        context['label'] = label
        context['count'] = float(counts.ix[module])

        if 'Agree' in module_data.columns:
            highlights = module_data.nlargest(3, 'Agree')[0:3]
            context['data']['highlights'] = highlights.to_csv()

            lowlights = module_data.nsmallest(3, 'Agree')[0:3]
            lowlights.sort_values('Agree', inplace=True, ascending=False)
            context['data']['lowlights'] = lowlights.to_csv()

        subsets_needed = set()
        subsets_needed.add('All Modules')

        for subset in SUBSETS:
            if module in subset['subset']:
                subsets_needed.add(subset['title'])

        meta_data = {}
        meta_data['label'] = label
        meta_data['subsets'] = list(subsets_needed)
        meta_data['count'] = float(counts.ix[module])
        context['meta_json'] = json.dumps(meta_data)
        context['data']['subsets'] = subsets[list(subsets_needed)].to_csv()

        fpath = os.path.join(BUILD_DIR, '%s Module Report - (%s).html' % (module, label))

        with open(fpath, 'w') as f:
            html = render_template('module_evaluation_analysis.html', context)
            f.write(html)

def construct_lecturer_templates(dataframes, label):
    # figure out which lecturer data we have
    lecturers = get_lecturer_list(dataframes)

    lecturer2modules = {}
    # figure out which lecturer goes with which module data
    for lecturer in lecturers:
        lecturer_data = extract_lecturer_data(dataframes, lecturer)
        lecturer_modules = get_module_list([lecturer_data])
        lecturer2modules[lecturer] = lecturer_modules

    print('\n\nWriting Lecturer templates')
    for lecturer, modules in tqdm(lecturer2modules.items()):

        context = {}
        context['data'] = {}
        context['lecturer'] = lecturer
        context['label'] = label
        context['modules'] = modules

        subsets = pandas.DataFrame()
        overall = pandas.DataFrame()
        counts = pandas.DataFrame()

        if os.path.exists(os.path.join(OUTPUT_DIRECTORY, 'lecturers', 'csv', construct_csv_filename(lecturer, label=label))):
            with open(os.path.join(OUTPUT_DIRECTORY, 'lecturers', 'csv', construct_csv_filename(lecturer, label=label))) as input_file:
                overall = pandas.read_csv(input_file, index_col=0)
        if os.path.exists(os.path.join(OUTPUT_DIRECTORY, 'lecturers', 'csv', construct_csv_filename('%s Counts' % lecturer, label=label))):
            with open(os.path.join(OUTPUT_DIRECTORY, 'lecturers', 'csv', construct_csv_filename('%s Counts' % lecturer, label=label))) as input_file:
                counts = pandas.read_csv(input_file, index_col=0)
        if os.path.exists(os.path.join(OUTPUT_DIRECTORY, 'lecturers', 'csv', construct_csv_filename('Lecturer Year and Subset Comparison', label=label))):
            with open(os.path.join(OUTPUT_DIRECTORY, 'lecturers', 'csv', construct_csv_filename('Lecturer Year and Subset Comparison', label=label))) as input_file:
                subsets = pandas.read_csv(input_file, index_col=0)

        context['total'] = float(counts.ix['All'])
        context['data']['overall'] = overall.to_csv()
        context['data']['counts'] = counts.to_csv()
        all_subsets = set()
        all_subsets.add('All Lecturers')

        context['data']['modules'] = []
        for module in modules:
            module_subsets = ['All Lecturers']
            for subset in SUBSETS:
                if module in subset['subset']:
                    module_subsets.append(subset['title'])
                    all_subsets.add(subset['title'])

            if os.path.exists(os.path.join(OUTPUT_DIRECTORY, 'lecturers', 'csv', construct_csv_filename(lecturer, module, label=label))):
                with open(os.path.join(OUTPUT_DIRECTORY, 'lecturers', 'csv', construct_csv_filename(lecturer, module, label=label))) as input_file:
                    df = pandas.read_csv(input_file, index_col=0)
                    module_data = {}
                    module_data['meta'] = {}
                    module_data['meta']['code'] = module
                    module_data['data'] = df.to_csv()
                    module_data['meta']['count'] = float(counts.ix[module])
                    module_data['meta']['subsets'] = module_subsets
                    module_data['meta_json'] = json.dumps(module_data['meta'])
                    context['data']['modules'].append(module_data)

        context['data']['subsets'] = subsets[list(all_subsets)].to_csv()

        fpath = os.path.join(BUILD_DIR, '%s Lecturer Report - (%s).html' % (lecturer, label))

        with open(fpath, 'w') as f:
            html = render_template('lecturer_evaluation_analysis.html', context)
            f.write(html)


def construct_subset_comparison_templates(dataframes, label):
    print('\n\nWriting Subset templates')
    for subset in tqdm(SUBSETS):

        context = {}
        subset_data = pandas.DataFrame()
        counts = pandas.DataFrame()
        comparison_data = pandas.DataFrame()

        if os.path.exists(os.path.join(OUTPUT_DIRECTORY, 'subsets', 'csv', construct_csv_filename(subset['title'], label=label))):
            with open(os.path.join(OUTPUT_DIRECTORY, 'subsets', 'csv', construct_csv_filename(subset['title'], label=label))) as input_file:
                subset_data = pandas.read_csv(input_file, index_col=0)

        if os.path.exists(os.path.join(OUTPUT_DIRECTORY, 'modules', 'csv', construct_csv_filename('Module Year and Subset Comparison', label=label))):
            with open(os.path.join(OUTPUT_DIRECTORY, 'modules', 'csv', construct_csv_filename('Module Year and Subset Comparison', label=label))) as input_file:
                comparison_data = pandas.read_csv(input_file, index_col=0)

        if os.path.exists(os.path.join(OUTPUT_DIRECTORY, 'modules', 'csv', construct_csv_filename('Module Count', label=label))):
            with open(os.path.join(OUTPUT_DIRECTORY, 'modules', 'csv', construct_csv_filename('Module Count', label=label))) as input_file:
                counts = pandas.read_csv(input_file, index_col=0)

        context['title'] = subset['title']
        context['modules'] = []
        context['label'] = label


        context['data'] = {}
        context['data']['overall'] = subset_data.to_csv()

        context['data']['average'] = comparison_data['All Modules'].to_csv(header=['Agree'], index_label='question')

        if 'Agree' in subset_data.columns:
            highlights = subset_data.nlargest(3, 'Agree')[0:3]
            context['data']['highlights'] = highlights.to_csv()

            lowlights = subset_data.nsmallest(3, 'Agree')[0:3]
            lowlights.sort_values('Agree', inplace=True, ascending=False)
            context['data']['lowlights'] = lowlights.to_csv()

        context['data']['modules'] = []

        for module in subset['subset']:

            if os.path.exists(os.path.join(OUTPUT_DIRECTORY, 'modules', 'csv', construct_csv_filename(module, label=label))):
                with open(os.path.join(OUTPUT_DIRECTORY, 'modules', 'csv', construct_csv_filename(module, label=label))) as input_file:
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
                        lowlights.sort_values('Agree', inplace=True, ascending=False)
                        module_data['lowlights'] = lowlights.to_csv()

                    context['data']['modules'].append(module_data)
                    context['modules'].append(module)


        fpath = os.path.join(BUILD_DIR, '%s Subset Evaluation Analysis Report - (%s).html' % (subset['title'], label))

        with open(fpath, 'w') as f:
            html = render_template('module_subset_evaluation_analysis.html', context)
            f.write(html)


def construct_lecturer_comparison_template(dataframes, label):

    print('\n\nWriting Lecturer Comparison Template')
    lecturer_comparison = pandas.DataFrame()
    subsets = pandas.DataFrame()

    for i in tqdm(range(1)):

        if os.path.exists(os.path.join(OUTPUT_DIRECTORY, 'lecturers', 'csv', construct_csv_filename('Lecturer Comparison', label=label))):
            with open(os.path.join(OUTPUT_DIRECTORY, 'lecturers', 'csv', construct_csv_filename('Lecturer Comparison', label=label))) as input_file:
                lecturer_comparison = pandas.read_csv(input_file, index_col=0)

        if os.path.exists(os.path.join(OUTPUT_DIRECTORY, 'lecturers', 'csv', construct_csv_filename('Lecturer Year and Subset Comparison', label=label))):
            with open(os.path.join(OUTPUT_DIRECTORY, 'lecturers', 'csv', construct_csv_filename('Lecturer Year and Subset Comparison', label=label))) as input_file:
                subsets = pandas.read_csv(input_file, index_col=0)

        context = {}
        context['data'] = {}
        context['data']['comparison'] = lecturer_comparison.to_csv()
        context['data']['subsets'] = subsets.to_csv()

        fpath = os.path.join(BUILD_DIR, 'Lecturer Evaluation Analysis Report - (%s).html' % (label))

        with open(fpath, 'w') as f:
            html = render_template('lecturer_evaluation_comparison.html', context)
            f.write(html)



def copy_template_files():
    template_files = os.listdir(TEMPLATE_PATH)
    template_files = [f for f in template_files if f.endswith('.css') or f.endswith('.js')]
    print('\n\nCopying template files')
    for f in tqdm(template_files):
        shutil.copy(os.path.join(TEMPLATE_PATH, f), BUILD_DIR)



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

    construct_lecturer_templates(dataframes, label)
    construct_module_templates(dataframes, label)
    construct_subset_comparison_templates(dataframes, label)
    construct_lecturer_comparison_template(dataframes, label)

    copy_template_files()
