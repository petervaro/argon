"""
Example 002
Command with limited unique boolean flags.
"""
# Import python modules
from sys import argv

# Import argon modules
from argon import Arguments, Command, Option

# Possible boolean flags
this  = Option('this' , value_type = Option.STATE_SWITCH,
                        flag_type  = Option.UNIQUE)
that  = Option('that' , value_type = Option.STATE_SWITCH,
                        flag_type  = Option.UNIQUE)
these = Option('these', value_type = Option.STATE_SWITCH,
                        flag_type  = Option.UNIQUE)
those = Option('those', value_type = Option.STATE_SWITCH,
                        flag_type  = Option.UNIQUE)

# Command object
cmd = Command(__file__,
              members=(this, that, these, those),
              member_type=Option.ONE)

# Argument-definition
definition = Arguments(cmd, *cmd.members)

# Process input from user
processed = definition.translate_args(argv)
# Print what we have
for flag, value in Arguments.branch_traverse(processed):
    print(flag, '=>', value)
