import os
import shutil
import pandas
import subprocess

from tqdm import tqdm
from weasyprint import HTML
from jinja2 import Environment, FileSystemLoader

from module_evaluation.analysis import *
from module_evaluation.extract_module_data import *

TEMPLATE_PATH = os.path.join(os.getcwd(), 'templates')
TEMPLATE_ENVIRONMENT = Environment(autoescape=False, loader=FileSystemLoader(TEMPLATE_PATH), trim_blocks=False)
TEMPLATE_FILES = ['style.css', 'module_against_average.js', 'module_comparison.js', 'overall_pie.js', 'highlowlights.js']

INPUT_DIR = os.path.join(os.getcwd(), 'input')
CSV_OUTPUT_DIR = os.path.join(os.getcwd(), 'output', 'modules', 'csv')
PDF_OUTPUT_DIR = os.path.join(os.getcwd(), 'output', 'modules', 'pdf')
BUILD_DIR = os.path.join(os.getcwd(), 'build')

def render_template(template_filename, context):
    return TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)

def read_input_dataframes():
    input_files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.xlsx')]
    dataframes = [pandas.read_excel(os.path.join(INPUT_DIR, f)) for f in input_files]
    return dataframes

def generate_module_data(pdfs=False):

    if not os.path.exists(CSV_OUTPUT_DIR):
        os.makedirs(CSV_OUTPUT_DIR)

    if not os.path.exists(PDF_OUTPUT_DIR):
        os.makedirs(PDF_OUTPUT_DIR)

    if not os.path.exists(BUILD_DIR):
        os.makedirs(BUILD_DIR)

    context = {}
    context['data'] = {}

    print('Reading input')
    dataframes = read_input_dataframes()

    print('Calculating scores over all modules')
    all_module_data = combine_module_evaluation_data(dataframes)
    all_module_data_counts = convert_to_likert_and_reduce(all_module_data)
    all_module_data_counts_T = all_module_data_counts.T
    all_module_data_counts_T.index.name = "question"
    with open(os.path.join(CSV_OUTPUT_DIR, 'all_module_percent_scores.csv'), 'w') as output_file:
        all_module_data_counts_T.to_csv(output_file)
    context['data']['all_module_percent_scores'] = all_module_data_counts_T.to_csv()

    print('Calculating number of responses per module')
    all_module_data = combine_module_evaluation_data(dataframes)
    module_counts = get_module_count(all_module_data)
    with open(os.path.join(CSV_OUTPUT_DIR, 'all_module_counts.csv'), 'w') as output_file:
        module_counts.to_csv(output_file)

    all_module_data = combine_module_evaluation_data(dataframes)
    module_comparison = pandas.DataFrame(index=[m for m in MODULE_COLUMNS if m != 'Module'])
    data_by_module = all_module_data.groupby('Module')

    module_comparison['AllModules'] = all_module_data_counts.ix['Agree']

    print('Calculating and writing per module data and writing report templates')
    for module in tqdm(data_by_module.groups):

            context['module'] = module
            context['count'] = int(module_counts[module])

            module_agreement_comparison = pandas.DataFrame(index=[m for m in MODULE_COLUMNS if m != 'Module'])

            module_data = data_by_module.get_group(module).dropna(axis=1, how='all')

            module_data_counts = convert_to_likert_and_reduce(module_data)
            module_data_counts_T = transpose_and_name_index(module_data_counts, 'question')

            module_agreement_comparison['module'] = module_data_counts.ix['Agree']
            module_agreement_comparison['AllModules'] = module_comparison['AllModules']
            module_agreement_comparison.index.name = "question"

            with open(os.path.join(CSV_OUTPUT_DIR, '%s_percent_agreement_comparison.csv' % (module.replace('/', '-'))), 'w') as output_file:
                module_agreement_comparison.to_csv(output_file)
            context['data']['percent_agreement_comparison'] = module_agreement_comparison.to_csv()

            highlights = module_data_counts_T.nlargest(3, 'Agree')[0:3]
            context['data']['highlights'] = highlights.to_csv()

            lowlights = module_data_counts_T.nsmallest(3, 'Agree')[0:3]
            context['data']['lowlights'] = lowlights.to_csv()

            with open(os.path.join(CSV_OUTPUT_DIR, '%s_percent_scores.csv' % (module.replace('/', '-'))), 'w') as output_file:
                module_data_counts_T.to_csv(output_file)
            context['data']['percent_scores'] = module_data_counts_T.to_csv()

            module_comparison[module] = module_data_counts.ix['Agree']

            fpath = os.path.join(BUILD_DIR, '%s_report.html' % (module.replace('/', '-')))

            with open(fpath, 'w') as f:
                html = render_template('module_evaluation_analysis.html', context)
                f.write(html)

    print('Writing module comparison data')
    module_comparison.index.name = 'question'
    with open(os.path.join(CSV_OUTPUT_DIR, 'all_module_percent_agreement_comparison.csv'), 'w') as output_file:
        module_comparison.to_csv(output_file)

    print('Copying template files')
    for f in tqdm(TEMPLATE_FILES):
        shutil.copy(os.path.join(TEMPLATE_PATH, f), BUILD_DIR)

    if pdfs:
        print('Creating PDF reports')
        module_templates = [f for f in os.listdir(BUILD_DIR) if f.endswith('html')]
        for module in tqdm(module_templates):
            mcode = module[:module.find('_report.html')]
            template_file = "file://%s" % os.path.join(BUILD_DIR, module)
            output_file = os.path.join("output", "modules", "pdf", "%s_report.pdf" % mcode)
            args = ['node', 'utils/generate_pdf.js', template_file, output_file]
            subprocess.call(args)


if __name__ == '__main__':
    generate_module_data(True)
