import pandas

from module_evaluation.config import LIKERT


def get_lecturer_list(dataframes):

    # find out which lecturers we have
    lecturers = set()

    for df in dataframes:
        lecturer_columns = [c[:c.find(':')] for c in df.columns if c.find(':') != -1]
        lecturers |= set(lecturer_columns)

    return list(lecturers)


def combine_lecturer_data(dataframes, lecturers):

    all_lecturer_frames = []

    for lecturer in lecturers:

        lecturer_frames = []

        for df in dataframes:
            this_lecturer_columns = [c for c in df.columns if c.find(':') != -1 and c.find(lecturer) != -1]
            if(len(this_lecturer_columns) > 0):
                ld_f = df[['Module'] + this_lecturer_columns].dropna()
                lecturer_frames.append(ld_f)

        lecturer_data = pandas.concat(lecturer_frames)
        lecturer_data.rename(columns = lambda x:  x.replace(lecturer, ''), inplace=True)
        all_lecturer_frames.append(lecturer_data)

    all_lecturer_data = pandas.concat(all_lecturer_frames)
    return all_lecturer_data


def extract_lecturer_data(dataframes, lecturer):

    lecturer_frames = []

    for df in dataframes:
        this_lecturer_columns = [c for c in df.columns if c.find(':') != -1 and c.find(lecturer) != -1]

        if(len(this_lecturer_columns) > 0):
            ld_f = df[['Module'] + this_lecturer_columns].dropna()
            lecturer_frames.append(ld_f)

    lecturer_data = pandas.concat(lecturer_frames)
    lecturer_data.rename(columns = lambda x:  x.replace(lecturer, ''), inplace=True)

    return lecturer_data


def extract_lecturer_data_for_module_occurence(dataframes, lecturer, module, occurence):
    lecturer_data = extract_lecturer_data(dataframes, lecturer)
    lecturer_module_data = lecturer_data.loc[lecturer_data['Module'] == '%s/%s' % (module, occurence)]
    return lecturer_module_data
