"""
Example 001
Command with simple boolean flags.
"""

# Import python modules
from sys import argv

# Import argon modules
from argon import Arguments, Command, Option

# Possible boolean flags
this  = Option('this' , value_type=Option.STATE_SWITCH)
that  = Option('that' , value_type=Option.STATE_SWITCH)
these = Option('these', value_type=Option.STATE_SWITCH)
those = Option('those', value_type=Option.STATE_SWITCH)

# Command object
cmd = Command(__file__, members=(this, that, these, those))

# Argument-definition
definition = Arguments(cmd, *cmd.members)

# Process input from user
processed = definition.translate_args(argv)
# Print what we have
for flag, value in Arguments.branch_traverse(processed):
    print(flag, '=>', value)
