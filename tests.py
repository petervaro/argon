## INFO ##
## INFO ##

# Import argin modules
from argon import *


#------------------------------------------------------------------------------#
# Pretty printer
def translate_traverse(arguments, command):
    print()
    print('-'*80)
    print('Raw command :', ' '.join(command), sep='\n    ')
    print('Context hierarchy :', arguments._hierarchy, sep='\n    ')
    processed = arguments.parse_iter(command)
    print('Translated  :', processed, sep='\n    ')

    # Traverse #1
    print('\nBreadth First Traverse:\n')
    # Get traverse generator
    traverse = Scheme.breadth_first_traverse(processed)
    # Get command separately
    _, command, *_ = next(traverse)
    print('command:', command)
    # Get flags
    for group, flag, value, _ in traverse:
        print(group, '.', flag, ' = ', value, sep='')


    # Traverse #2
    print('\nBranch Traverse:\n')
    # Get traverse generator
    traverse = Scheme.branch_traverse(processed)
    # Get command separately
    command, _ = next(traverse)
    print('command:', command)
    # Get flags
    for flag, value in traverse:
        print(flag, '=', value)


    # Traverse #3
    print('\nBranch Full Traverse:\n')
    traverse = Scheme.branch_full_traverse(processed)
    # Get command separately
    (command, *_), *_ = next(traverse)
    print('command:', command)
    # Get flags
    for (_, *path), value in traverse:
        print('.'.join(path), '=', value)
    print()


#------------------------------------------------------------------------------#
# Build definitions
scheme1 = Scheme(Program('pmt',
                         members     = ('set', 'add'),
                         member_type = Pattern.ONE),

                 Pattern(long_flag    = 'set',
                         long_prefix  = '',
                         flag_type    = Pattern.UNIQUE,
                         members      = ('target', 'values')),

                 Pattern(long_flag    = 'add',
                         long_prefix  = '',
                         flag_type    = Pattern.UNIQUE,
                         members      = ('target', 'values')),

                 Pattern(long_flag    = 'target',
                         short_flags  = 't',
                         members      = ('milestone', 'label-name')),

                 Pattern(long_flag    = 'values',
                         short_flags  = 'v',
                         value_type   = Pattern.NAMED_VALUES,
                         flag_type    = Pattern.PRIMAL),

                 Pattern(long_flag    = 'milestone',
                         short_flags  = 'm',
                         flag_type    = Pattern.PRIMAL),

                 Pattern(long_flag    = 'label-name',
                         short_flags  = 'L',
                         flag_type    = Pattern.PRIMAL))


scheme2 = Scheme(Program('test',
                         members     = ('ham',),
                         member_type = Pattern.ONE),

                 Pattern(long_flag    = 'ham',
                         short_flags  = 'hH',
                         flag_type    = Pattern.PRIMAL,
                         value_type   = Pattern.STATE_SWITCH))


#------------------------------------------------------------------------------#
# Tests
translate_traverse(
    scheme1,
    ('pmt', 'set', 'issues', '-t', 'milestones',
                                         '-m', 'open',
                                         #'-m', 'closed',
                                   '-t', 'issues',
                                         '-L', 'MyOtherLabel',
                                   '-v',
                                         'status', 'closed',
                                         'labels', 'MyLabel',))

try:
    translate_traverse(
        scheme2,
        ('test', '--ham', '-H'))
except Scheme.MemberTypeAlreadyUsed:
    print('[PASS]')
