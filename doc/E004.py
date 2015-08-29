"""
Example 004
Program with limited unique boolean flags,
with proper error handling,
string-based declaration,
and help text.
"""
# Import python modules
from errno import EINVAL
from sys   import argv, exit

# Import argon modules
from argon import *

# Scheme object
scheme = Scheme(
    Program(__file__,
            members=('this', 'that', 'these', 'those', 'help'),
            member_type=Pattern.ONE,
            description=Section(
                Section(
                    Header('NAME'),
                    Paragraph(__file__ + ' - Testing `argon`.')),
                Section(
                    Header('SYNOPSIS'),
                    Paragraph(__file__ + ' [OPTIONS]')),
                Section(
                    Header('DESCRIPTION'),
                    Paragraph('This is a test script, to find out how the '
                                   'help-text construction and generation is '
                                   'working in `argon`.')))),
    Pattern('this',
            value_type  = Pattern.STATE_SWITCH,
            flag_type   = Pattern.UNIQUE,
            description = Section(
                Flags(),
                Paragraph('Optional value: sets `this`.'))),
    Pattern('that',
            value_type = Pattern.STATE_SWITCH,
            flag_type  = Pattern.UNIQUE,
            description = Section(
                Flags(),
                Paragraph('Optional value: sets `that`.'))),
    Pattern('these',
            value_type = Pattern.STATE_SWITCH,
            flag_type  = Pattern.UNIQUE,
            description = Section(
                Flags(),
                Paragraph('Optional value: sets `these`.'))),
    Pattern('those',
            value_type = Pattern.STATE_SWITCH,
            flag_type  = Pattern.UNIQUE,
            description = Section(
                Flags(),
                Paragraph('Optional value: sets `those`.'))),
    Pattern('help',
            short_flags = 'hH',
            value_type  = Pattern.STATE_SWITCH,
            flag_type   = Pattern.UNIQUE,
            description = Section(
                Flags(),
                Paragraph('Print this text.'))))

# Process input from user
processed = scheme.parse_iter(argv, catch_errors=True)
traverse  = Scheme.branch_traverse(processed)

# Get what we have if there was no error
try:
    # Get rid of command-name
    next(traverse)
# If there was error
except TypeError:
    exit(EINVAL)


# Process arguments
try:
    flag, value = next(traverse)
    if flag == 'help':
        raise StopIteration
    else:
        print(flag, '=>', value)
except StopIteration:
    scheme.write_help(
        Section(
            __file__,
            Section(
                Header('OPTIONS'),
                Section(
                    'this',
                    'that',
                    'these',
                    'those',
                    'help', indent=1),
                Header('AUTHOR'),
                Section(
                    Header('Peter Varo'),
                    Paragraph('<petervaro@sketchandprototype.com>'), indent=1))))
