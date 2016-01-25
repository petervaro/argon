"""
Example 003
Command with limited unique boolean flags,
with proper error handling,
and string-based declaration.
"""
# Import python modules
from errno import EINVAL
from sys   import argv, exit, path

# TODO: Testing hack
path.append('../argon')

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
processed = scheme.parse_iter(argv, catch_errors=True)

# Print what we have if there was no error
try:
    for flag, value in Scheme.branch_traverse(processed):
        print(flag, '=>', value)
# If there was error
except TypeError:
    exit(EINVAL)
