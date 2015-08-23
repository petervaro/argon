"""
Example 001
Command with simple boolean flags.
"""

# Import python modules
from sys import argv

# Import argon modules
from argon import *

# Possible boolean flags
this  = Pattern('this' , value_type=Pattern.STATE_SWITCH)
that  = Pattern('that' , value_type=Pattern.STATE_SWITCH)
these = Pattern('these', value_type=Pattern.STATE_SWITCH)
those = Pattern('those', value_type=Pattern.STATE_SWITCH)

# Program object
cmd = Program(__file__, members=(this, that, these, those))

# Scheme object
scheme = Scheme(cmd, *cmd.members)

# Process input from user
processed = scheme.translate_args(argv)
# Print what we have
for flag, value in Scheme.branch_traverse(processed):
    print(flag, '=>', value)
