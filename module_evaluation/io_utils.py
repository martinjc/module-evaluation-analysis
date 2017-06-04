def construct_filename_identifier(identifier):
    return '%s.csv' % (identifier)

def construct_filename_identifier_and_occurence(identifier, occurence):
    return '%s - (%s).csv' % (identifier, occurence)
