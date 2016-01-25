"""
Example 002
Command with limited unique boolean flags.
"""
# Import python modules
from sys import argv, path

# TODO: Testing hack
path.append('../argon')

# Import argon modules
from argon import *

# Possible boolean flags
this  = Pattern('this' , value_type = Pattern.STATE_SWITCH,
                         flag_type  = Pattern.UNIQUE)
that  = Pattern('that' , value_type = Pattern.STATE_SWITCH,
                         flag_type  = Pattern.UNIQUE)
these = Pattern('these', value_type = Pattern.STATE_SWITCH,
                         flag_type  = Pattern.UNIQUE)
those = Pattern('those', value_type = Pattern.STATE_SWITCH,
                         flag_type  = Pattern.UNIQUE)

# Command object
cmd = Program(__file__,
              members=(this, that, these, those),
              member_type=Pattern.ONE)

# Scheme object
scheme = Scheme(cmd, *cmd.members)

# Process input from user
processed = scheme.parse_iter(argv)
# Print what we have
for flag, value in Scheme.branch_traverse(processed):
    print(flag, '=>', value)
