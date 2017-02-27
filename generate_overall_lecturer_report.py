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
TEMPLATE_FILES = ['lecturer_style.css']

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

    all_lecturer_data = combine_lecturer_data(dataframes, lecturers)

    lecturer_comparison = pandas.DataFrame(index=[LECTURER_COLUMNS])

    context['data']['average'] = all_lecturer_data_counts.ix['Agree'].to_csv()

    lecturer_count = pandas.Series()

    print('Calculating and writing data report templates')
    for lecturer in tqdm(lecturers):

        lecturer_data = extract_lecturer_data(dataframes, lecturer)

        if 'Module' in lecturer_data.columns:
            del lecturer_data['Module']

        # count the number of answers for each value of the likert scale, and store in a new DataFrame
        lecturer_data_counts = convert_to_likert_and_reduce(lecturer_data)
        lecturer_count[lecturer] = len(lecturer_data.index)
        lecturer_comparison['%s' % (lecturer)] = lecturer_data_counts.ix['Agree']

        lecturer_comparison_T = transpose_and_name_index(lecturer_comparison, 'lecturer')

    context['data']['lecturer_count'] = lecturer_count.to_csv()
    context['data']['lecturer_comparison'] = lecturer_comparison_T.to_csv()
    context['questions'] = [{'id': 'q%s' % i, 'q': l.replace(": ", "")} for i, l in enumerate(LECTURER_COLUMNS)]

    fpath = os.path.join(BUILD_DIR, 'overall_report_lecturer.html')

    with open(fpath, 'w') as f:
        html = render_template('overall_lecturer_evaluation_analysis.html', context)
        f.write(html)

    print('Copying template files')
    for f in tqdm(TEMPLATE_FILES):
        shutil.copy(os.path.join(TEMPLATE_PATH, f), BUILD_DIR)

    if pdfs:
        print('Creating PDF report')
        template_file = "file://%s" % fpath
        output_file = os.path.join("output", "lecturers", "pdf", "overall_lecturer_report.pdf")
        args = ['node', 'utils/generate_pdf.js', template_file, output_file]
        subprocess.call(args)


if __name__ == '__main__':
    generate_lecturer_data()
