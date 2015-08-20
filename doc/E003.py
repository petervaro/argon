"""
Example 003
Command with limited unique boolean flags,
with proper error handling,
and string-based declaration.
"""
# Import python modules
from errno import EINVAL
from sys   import argv, exit

# Import argon modules
from argon import Arguments, Command, Option

# Argument-definition
definition = Arguments(Command(__file__, members     = ('this',
                                                        'that',
                                                        'these',
                                                        'those'),
                                         member_type = Option.ONE),

                       Option('this'   , value_type  = Option.STATE_SWITCH,
                                         flag_type   = Option.UNIQUE),

                       Option('that'   , value_type  = Option.STATE_SWITCH,
                                         flag_type   = Option.UNIQUE),

                       Option('these'  , value_type  = Option.STATE_SWITCH,
                                         flag_type   = Option.UNIQUE),

                       Option('those'  , value_type  = Option.STATE_SWITCH,
                                         flag_type   = Option.UNIQUE))

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
for flag, value in Arguments.branch_traverse(processed):
    print(flag, '=>', value)
