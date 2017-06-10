def construct_csv_filename(*args, label=''):
    if label != '':
        return '%s - (%s).csv' % (' - '.join(args), label)
    else:
        return '%s.csv' % (' - '.join(args))
