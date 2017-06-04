def construct_filename_identifier(identifier):
    return '%s.csv' % (identifier)

def construct_filename_identifier_and_occurence(identifier, occurence):
    return '%s - (%s).csv' % (identifier, occurence)

def construct_filename_lecturer_module_occurence(lecturer, module, occurence):
    return construct_filename_identifier_and_occurence('%s - %s' % (lecturer, module), occurence)
