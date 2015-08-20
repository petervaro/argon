"""
Example 004
Command with limited unique boolean flags,
with proper error handling,
string-based declaration,
and help text.
"""
# Import python modules
from errno import EINVAL
from sys   import argv, exit

# Import argon modules
from argon import Arguments, Command, Option, Text

# Argument-definition
definition = Arguments(
    Command(__file__,
            members=('this', 'that', 'these', 'those', 'help'),
            member_type=Option.ONE,
            description=Text.Section(
                Text.Section(
                    Text.Header('NAME'),
                    Text.Paragraph(__file__ + ' - Testing `argon`.')),
                Text.Section(
                    Text.Header('SYNOPSIS'),
                    Text.Paragraph(__file__ + ' [OPTIONS]')),
                Text.Section(
                    Text.Header('DESCRIPTION'),
                    Text.Paragraph('This is a test script, to find out how the '
                                   'help-text construction and generation is '
                                   'working in `argon`.')))),
    Option('this',
           value_type  = Option.STATE_SWITCH,
           flag_type   = Option.UNIQUE,
           description = Text.Section(
               Text.Flags(),
               Text.Paragraph('Optional value: set `this`.'))),
    Option('that',
           value_type = Option.STATE_SWITCH,
           flag_type  = Option.UNIQUE,
           description = Text.Section(
               Text.Flags(),
               Text.Paragraph('Optional value: set `that`.'))),
    Option('these',
           value_type = Option.STATE_SWITCH,
           flag_type  = Option.UNIQUE,
           description = Text.Section(
               Text.Flags(),
               Text.Paragraph('Optional value: set `these`.'))),
    Option('those',
           value_type = Option.STATE_SWITCH,
           flag_type  = Option.UNIQUE,
           description = Text.Section(
               Text.Flags(),
               Text.Paragraph('Optional value: set `those`.'))),
    Option('help',
           short_flags = 'hH',
           value_type  = Option.STATE_SWITCH,
           flag_type   = Option.UNIQUE,
           description = Text.Section(
               Text.Flags(),
               Text.Paragraph('Print this text.'))))

# Process input from user
try:
    processed = definition.translate_args(argv)
except Option.FinishedOption as e:
    flag, value = e.args
    if flag == __file__:
        print('Invalid flag for {!r}: {!r}'.format(flag, value))
    else:
        print('Flag {!r} does not take any value, '
              'but {!r} was given'.format(flag, value))
    # Invalid argument exit
    exit(EINVAL)

# Print what we have
traverse = Arguments.branch_traverse(processed)
next(traverse)
try:
    flag, value = next(traverse)
    if flag == 'help':
        raise StopIteration
    else:
        print(flag, '=>', value)
except StopIteration:
    definition.write_help(
        Text.Section(
            __file__,
            Text.Section(
                Text.Header('OPTIONS'),
                Text.Section(
                    'this',
                    'that',
                    'these',
                    'those',
                    'help', indent=1))))
