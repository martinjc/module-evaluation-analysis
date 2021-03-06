import os
# Non numeric columns, or columns that don't ask questions answered by a likert scale
# for now we exclude them from the analysis
#
EXCLUDE_COLUMNS = [
    'Evaluation',
    'What proportion of the timetabled activities have you attended?',
    'On average, how many hours have you spent per week on this module, outside of the timetabled activities? Please note: there is no optimal answer for this question',
    'What did you particularly value about the module?',
    'How do you think the module could be improved?',
    'What proportion of the timetabled activities have you attended?',
    'On average, how many hours have you spent per week on this module, outside of the timetabled activities?',
    'What did you particularly like about the module?',
    'What would you like to see changed?',
    'If your mid-module feedback identified an improvement to make, has this been done and how has it improved the module?'
]

# Mapping from numbers to human-readable strings
LIKERT = {
    0.0: 'N/A',
    1.0: 'Disagree Strongly',
    2.0: 'Disagree',
    3.0: 'Neither Agree nor Disagree',
    4.0: 'Agree',
    5.0: 'Agree Strongly'
}


# Collections of modules that may need to be analysed together
# Add or remove from here as you please
YEAR1 = ['CM1101', 'CM1102', 'CM1103', 'CM1104', 'CM1201', 'CM1202', 'CM1204', 'CM1205', 'CM1206', 'CM1208', 'CM1209', 'CM1210']
YEAR2 = ['CM2101', 'CM2102', 'CM2103', 'CM2104', 'CM2105', 'CM2201', 'CM2203', 'CM2205', 'CM2206', 'CM2207', 'CM2208', 'CM2302', 'CM2303', 'CM2305', 'CM2500']
YEAR3 = ['CM3101', 'CM3103', 'CM3104', 'CM3105', 'CM3106', 'CM3107', 'CM3109', 'CM3110', 'CM3111', 'CM3112', 'CM3113', 'CM3114', 'CM3201', 'CM3202', 'CM3203', 'CM3301', 'CM3302', 'CM3303', 'CM3304']
MSC = ['CMT102', 'CMT103', 'CMT104', 'CMT105', 'CMT106', 'CMT107', 'CMT108', 'CMT111', 'CMT112', 'CMT202', 'CMT205', 'CMT206', 'CMT207', 'CMT209', 'CMT212', 'CMT213', 'CMT301', 'CMT302', 'CMT303', 'CMT304', 'CMT305', 'CMT306', 'CMT400']
NSA_YEAR1 = ['CM6112', 'CM6113', 'CM6114', 'CM6121', 'CM6122', 'CM6123']
NSA_YEAR2 = ['CM6211', 'CM6212', 'CM6213', 'CM6221', 'CM6222', 'CM6223']
NSA_YEAR3 = ['CM6311', 'CM6312', 'CM6321', 'CM6331', 'CM6332']

PFMSADSA = ['CMT304', 'CMT302', 'CMT306', 'CMT106', 'CMT209', 'CMT107', 'CMT105', 'CMT213', 'CMT202', 'CMT108', 'CMT206', 'CMT104', 'CMT111']
PFMSCITA = ['CMT302', 'CMT301', 'CMT103', 'CMT112', 'CMT207', 'CMT212', 'CMT202', 'CMT206']
PFMSCMPA = ['CMT303', 'CMT103', 'CMT205', 'CMT112', 'CMT102', 'CMT302', 'CMT212', 'CMT111', 'CMT202', 'CMT206', 'CMT207']
PFMSDSYA = ['CMT108', 'CMT112', 'CMT103', 'CMT209', 'CMT212', 'CMT111', 'CMT202']
PFMSISPA = ['CMT301', 'CMT306', 'CMT105', 'CMT213', 'CMT104', 'CMT202']
PFMSCDJ = ['CMT112', 'CMT103', 'CMT212', 'CMT111', 'CMT206']


# Mapping of the subsets above to a human-readable string. Also collects all subsets together
# so they can all be referred to and analysed
SUBSETS = [
    {
        'title': 'Year 1 CS',
        'subset': YEAR1
    },
    {
        'title': 'Year 2 CS',
        'subset': YEAR2
    },
    {
        'title': 'Year 3 CS',
        'subset': YEAR3
    },
    {
        'title': 'MSc',
        'subset': MSC
    },
    {
        'title': 'Year 1 ASE',
        'subset': NSA_YEAR1
    },
    {
        'title': 'Year 2 ASE',
        'subset': NSA_YEAR2
    },
    {
        'title': 'Year 3 ASE',
        'subset': NSA_YEAR3
    },
    {
        'title': 'MSc Advanced Computer Science',
        'subset': PFMSADSA
    },
    {
        'title': 'MSc Computing and IT Management',
        'subset': PFMSCITA
    },
    {
        'title': 'MSc Computing',
        'subset': PFMSCMPA
    },
    {
        'title': 'MSc Data Science and Analytics',
        'subset': PFMSDSYA
    },
    {
        'title': 'MSc Information Security and Privacy',
        'subset': PFMSISPA
    },
    {
        'title': 'MSc Computational and Data Journalism',
        'subset': PFMSCDJ
    },
]

COLUMN_MAPPINGS = {
    "Feedback has helped me to clarify things i did not understand": "Feedback has helped me to clarify things I did not understand",
    "I feel confident in communicating the knowledge i have gained on the module": "I feel confident in communicating the knowledge I have gained on the module",
    "I had a clear sense of what is required of me in the assessment/s for this module": "I had a clear sense of what was required of me in the assessment/s for this module",
    "The module has been well organised": "The module was well organised and structured",
    "The module was well organised and structured (eg lectures, seminars, visiting speakers)": "The module was well organised and structured",
    "The module has helped my personal development by improving my employability skills (eg presentation skills, communication skills)": "The module has helped my personal development by improving my employability skills",
    "The module has helped my personal development by improving my employability skills (eg presentation skills, communication skills, groupwork, methods training)": "The module has helped my personal development by improving my employability skills",
    "The module met my expectations in terms of the knowledge i have gained": "The module met my expectations in terms of the knowledge I have gained",
    "The range of the module's resources (on Learning Central and /or in paper form) effectively supported my learning": "The range of the module's resources effectively supported my learning",
    "The range of the modules resources (on Learning Central and /or in paper form) effectively supported my learning": "The range of the module's resources effectively supported my learning",
    "The range of the module’s resources (on Learning Central and/or in paper form) has effectively supported my learning": "The range of the module's resources effectively supported my learning",
}

BUILD_DIR = os.path.join(os.getcwd(), 'build')
OUTPUT_DIRECTORY = os.path.join(os.getcwd(), 'output')
