## INFO ##
## INFO ##

# Import argin modules
from argon import Arguments, Option


#------------------------------------------------------------------------------#
# Pretty printer
def translate_traverse(arguments, command):
    print('Raw command :', ' '.join(command), sep='\n    ')
    processed = arguments.translate_args(command)
    print('Translated  :', processed, sep='\n    ')

    # Traverse #1
    print('\nBreadth First Traverse:\n')
    # Get traverse generator
    traverse = Arguments.breadth_first_traverse(processed)
    # Get command separately
    _, command, *_ = next(traverse)
    print('command:', command)
    # Get flags
    for group, flag, value, _ in traverse:
        print(group, '.', flag, ' = ', value, sep='')


    # Traverse #2
    print('\nBranch Traverse:\n')
    # Get traverse generator
    traverse = Arguments.branch_traverse(processed)
    # Get command separately
    command, _ = next(traverse)
    print('command:', command)
    # Get flags
    for flag, value in traverse:
        print(flag, '=', value)


    # Traverse #3
    print('\nBranch Full Traverse:\n')
    traverse = Arguments.branch_full_traverse(processed)
    # Get command separately
    (command, *_), *_ = next(traverse)
    print('command:', command)
    # Get flags
    for (_, *path), value in traverse:
        print('.'.join(path), '=', value)


#------------------------------------------------------------------------------#
# Build definition
argdef = Arguments(Option(long_flag   = 'pmt',
                          long_prefix = '',
                          flag_type   = Option.UNIQUE,
                          value_type  = Option.STATE_SWITCH,
                          members     = ('set', 'add'),
                          member_type = Option.ONE),
                   Option(long_flag   = 'set',
                          long_prefix = '',
                          flag_type   = Option.UNIQUE,
                          members     = ('target', 'values')),
                   Option(long_flag   = 'add',
                          long_prefix = '',
                          flag_type   = Option.UNIQUE,
                          members     = ('target', 'values')),
                   Option(long_flag   = 'target',
                          short_flags = 't',
                          members     = ('milestone', 'label-name')),
                   Option(long_flag   = 'values',
                          short_flags = 'v',
                          value_type  = Option.NAMED_VALUES),
                   Option(long_flag   = 'milestone',
                          short_flags = 'm'),
                   Option(long_flag   = 'label-name',
                          short_flags = 'L'))


#------------------------------------------------------------------------------#
# Tests
translate_traverse(
    argdef,
    ('pmt', 'set', 'issues', '-t', 'milestones',
                                         '-m', 'open',
                                   '-t', 'issues',
                                         '-L', 'MyOtherLabel',
                                   '-v',
                                         'status', 'closed',
                                         'labels', 'MyLabel',))
