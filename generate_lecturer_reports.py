import os
import shutil
import pandas
import subprocess

from tqdm import tqdm
from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader

from module_evaluation.analysis import *
from module_evaluation.data_transform import *
from module_evaluation.extract_lecturer_data import *

TEMPLATE_PATH = os.path.join(os.getcwd(), 'templates')
TEMPLATE_ENVIRONMENT = Environment(autoescape=False, loader=FileSystemLoader(TEMPLATE_PATH), trim_blocks=False)
TEMPLATE_FILES = ['style.css', 'evaluation_pie.js', 'against_average.js']

INPUT_DIR = os.path.join(os.getcwd(), 'input')
CSV_OUTPUT_DIR = os.path.join(os.getcwd(), 'output', 'lecturers', 'csv')
PDF_OUTPUT_DIR = os.path.join(os.getcwd(), 'output', 'lecturers', 'pdf')
BUILD_DIR = os.path.join(os.getcwd(), 'build')

def render_template(template_filename, context):
    return TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)


def generate_lecturer_data(pdfs=False):

    if not os.path.exists(CSV_OUTPUT_DIR):
        os.makedirs(CSV_OUTPUT_DIR)

    if not os.path.exists(PDF_OUTPUT_DIR):
        os.makedirs(PDF_OUTPUT_DIR)

    if not os.path.exists(BUILD_DIR):
        os.makedirs(BUILD_DIR)

    context = {}
    context['data'] = {}

    print('Reading input')
    dataframes = read_input_dataframes(INPUT_DIR)


    print('Getting list of lecturers')
    lecturers = get_lecturer_list(dataframes)

    print('Calculating scores over all modules')
    all_lecturer_data = combine_lecturer_data(dataframes, lecturers)
    all_lecturer_data_counts = convert_to_likert_and_reduce(all_lecturer_data)
    all_lecturer_data_counts_T = transpose_and_name_index(all_lecturer_data_counts, 'question');

    with open(os.path.join(CSV_OUTPUT_DIR, 'all_lecturer_percent_scores.csv'), 'w') as output_file:
        all_lecturer_data_counts_T.to_csv(output_file)

    context['data']['all_lecturer_percent_scores'] = all_lecturer_data_counts_T.to_csv()

    all_lecturer_data = combine_lecturer_data(dataframes, lecturers)

    lecturer_comparison = pandas.DataFrame(index=[LECTURER_COLUMNS])
    lecturer_comparison_by_module = pandas.DataFrame(index=[LECTURER_COLUMNS])
    lecturer_comparison['All Lecturers'] = all_lecturer_data_counts.ix['Agree']
    lecturer_comparison_by_module['All Lecturers'] = all_lecturer_data_counts.ix['Agree']
    module_count = pandas.Series()
    lecturer_count = pandas.Series()

    print('Calculating and writing per lecturer data report templates')
    for lecturer in tqdm(lecturers):

        lecturer_data = extract_lecturer_data(dataframes, lecturer)
        lecturer_data_by_module = lecturer_data.groupby('Module')

        context['data']['modules'] = []

        for module in lecturer_data_by_module.groups:

            mld = lecturer_data_by_module.get_group(module)
            del mld['Module']

            mld_counts = convert_to_likert_and_reduce(mld)
            mld_counts_T = transpose_and_name_index(mld_counts, 'question')

            with open(os.path.join(CSV_OUTPUT_DIR, '%s_%s_percent_agreement_data.csv' % (lecturer, module.replace('/', '-'))), 'w') as output_file:
                mld_counts_T.to_csv(output_file)

            lecturer_comparison_by_module['%s: %s' % (lecturer, module)] = mld_counts.ix['Agree']
            module_count['%s: %s' % (lecturer, module)] =  len(mld.index)

        if 'Module' in lecturer_data.columns:
            del lecturer_data['Module']

        # count the number of answers for each value of the likert scale, and store in a new DataFrame
        lecturer_data_counts = convert_to_likert_and_reduce(lecturer_data)
        lecturer_data_counts_T = transpose_and_name_index(lecturer_data_counts, 'question')

        lecturer_count[lecturer] = len(lecturer_data.index)
        context['lecturer'] = lecturer
        context['count'] = len(lecturer_data.index)

        with open(os.path.join(CSV_OUTPUT_DIR, '%s_percent_agreement_all_data.csv' % (lecturer)), 'w') as output_file:
            lecturer_data_counts_T.to_csv(output_file)
        context['data']['agreement_overall'] = lecturer_data_counts_T.to_csv()

        lecturer_comparison['%s' % (lecturer)] = lecturer_data_counts.ix['Agree']

        fpath = os.path.join(BUILD_DIR, '%s_report_lecturer.html' % (lecturer))

        with open(fpath, 'w') as f:
            html = render_template('lecturer_evaluation_analysis.html', context)
            f.write(html)

    with open(os.path.join(CSV_OUTPUT_DIR, 'lecturer_count.csv'), 'w') as output_file:
        lecturer_count.to_csv(output_file)

    with open(os.path.join(CSV_OUTPUT_DIR, 'lecturer_by_module_count.csv'), 'w') as output_file:
        module_count.to_csv(output_file)

    lecturer_comparison.index.name = 'question'
    with open(os.path.join(CSV_OUTPUT_DIR, 'all_lecturers_percent_agreement.csv'), 'w') as output_file:
        lecturer_comparison.to_csv(output_file)

    lecturer_comparison_by_module.index.name = 'question'
    with open(os.path.join(CSV_OUTPUT_DIR, 'all_lecturers_percent_agreement_by_module.csv'), 'w') as output_file:
        lecturer_comparison_by_module.to_csv(output_file)

    print('Copying template files')
    for f in tqdm(TEMPLATE_FILES):
        shutil.copy(os.path.join(TEMPLATE_PATH, f), BUILD_DIR)

    if pdfs:
        print('Creating PDF reports')
        lecturer_templates = [f for f in os.listdir(BUILD_DIR) if f.endswith('_report_lecturer.html')]
        for lecturer in tqdm(lecturer_templates):
            mcode = lecturer[:lecturer.find('_report_lecturer.html')]
            template_file = "file://%s" % os.path.join(BUILD_DIR, lecturer)
            output_file = os.path.join("output", "lecturers", "pdf", "%s_report.pdf" % mcode)
            args = ['node', 'utils/generate_landscape_pdf.js', template_file, output_file]
            subprocess.call(args)


if __name__ == '__main__':
    generate_lecturer_data(True)
