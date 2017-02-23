import pandas

from module_evaluation.analysis import LECTURER_COLUMNS, LIKERT


def get_lecturer_list(dataframes):

    # find out which lecturers we have
    lecturers = set()

    for df in dataframes:
        l = [n.replace(LECTURER_COLUMNS[0], '') for n in df.columns if n.endswith(LECTURER_COLUMNS[0])]
        lecturers |= set(l)

    return list(lecturers)


def combine_lecturer_data(dataframes, lecturers):

    all_lecturer_frames = []

    for lecturer in lecturers:

        this_lecturer_columns = ['%s%s' % (lecturer, column) for column in LECTURER_COLUMNS]
        lecturer_frames = []

        for df in dataframes:
            if this_lecturer_columns[0] in df.columns:
                ld_f = df[['Module'] + this_lecturer_columns].dropna()
                lecturer_frames.append(ld_f)

        lecturer_data = pandas.concat(lecturer_frames)
        lecturer_data.rename(columns = lambda x:  x.replace(lecturer, ''), inplace=True)
        all_lecturer_frames.append(lecturer_data)

    all_lecturer_data = pandas.concat(all_lecturer_frames)
    return all_lecturer_data


def extract_lecturer_data(dataframes, lecturer):

    this_lecturer_columns = ['%s%s' % (lecturer, column) for column in LECTURER_COLUMNS]

    lecturer_frames = []

    for df in dataframes:

        if this_lecturer_columns[0] in df.columns:

            ld_f = df[['Module'] + this_lecturer_columns].dropna()
            lecturer_frames.append(ld_f)

    lecturer_data = pandas.concat(lecturer_frames)
    lecturer_data.rename(columns = lambda x:  x.replace(lecturer, ''), inplace=True)

    return lecturer_data
