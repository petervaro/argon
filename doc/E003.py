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
from argon import *

# Scheme object
scheme = Scheme(Program(__file__, members     = ('this',
                                                 'that',
                                                 'these',
                                                 'those'),
                                  member_type = Pattern.ONE),

                Pattern('this'  , value_type  = Pattern.STATE_SWITCH,
                                  flag_type   = Pattern.UNIQUE),

                Pattern('that'  , value_type  = Pattern.STATE_SWITCH,
                                  flag_type   = Pattern.UNIQUE),

                Pattern('these' , value_type  = Pattern.STATE_SWITCH,
                                  flag_type   = Pattern.UNIQUE),

                Pattern('those' , value_type  = Pattern.STATE_SWITCH,
                                  flag_type   = Pattern.UNIQUE))

# Process input from user
try:
    processed = scheme.parse_iter(argv)
except Pattern.FinishedPattern as e:
    flag, value = e.args
    if flag == __file__:
        print('Invalid flag for {!r}: {!r}'.format(flag, value))
    else:
        print('Flag {!r} does not take any value, '
              'but {!r} was given'.format(flag, value))
    # Invalid argument exit
    exit(EINVAL)

# Print what we have
for flag, value in Scheme.branch_traverse(processed):
    print(flag, '=>', value)
