## INFO ##
## INFO ##

from argon import *

def cmd(scheme, line):
    processed = scheme.parse_line(line, True, True)
    if processed:
        print('==> Processed:\n    ', processed, sep='')

#------------------------------------------------------------------------------#
s = Scheme(Program('app',
                   members=('bool', 'ovalue', 'rvalue', 'clist', 'ulist', 'map')),

           Pattern('bool',
                   value_type=Pattern.STATE_SWITCH),

           Pattern('rvalue'),

           Pattern('ovalue',
                   value_necessity=Pattern.OPTIONAL),

           Pattern('clist',
                   value_type=Pattern.COMMON_ARRAY),

           Pattern('ulist',
                   value_type=Pattern.UNIQUE_ARRAY),

           Pattern('map',
                   value_type=Pattern.NAMED_VALUES))

# Error: no error
cmd(s, 'app --ovalue')

# Error: FinishedPattern
cmd(s, 'app --bool alpha')
cmd(s, 'app --value alpha beta')

# Error: UnfinishedPattern
cmd(s, 'app --value')
cmd(s, 'app --value --bool')

cmd(s, 'app --clist')
cmd(s, 'app --clist --bool')

cmd(s, 'app --ulist')
cmd(s, 'app --ulist --bool')

cmd(s, 'app --map')
cmd(s, 'app --map --bool')



#------------------------------------------------------------------------------#
s = Scheme(Program('app',
                   members=('bool', 'value', 'clist', 'ulist',
                            'map', 'ctx-bool', 'ctx-nested')),

           Pattern('bool',
                   value_type=Pattern.STATE_SWITCH),

           Pattern('value'),

           Pattern('clist',
                   value_type=Pattern.COMMON_ARRAY),

           Pattern('ulist',
                   value_type=Pattern.UNIQUE_ARRAY),

           Pattern('map',
                   value_type=Pattern.NAMED_VALUES),

           Pattern('ctx-bool',
                   members=('ctx-member',), value_type=Pattern.STATE_SWITCH),

           Pattern('ctx-member',
                   value_type=Pattern.STATE_SWITCH),

           Pattern('ctx-nested',
                   members=('ctx-sub-ctx',), value_type=Pattern.STATE_SWITCH),

           Pattern('ctx-sub-ctx',
                   members=('ctx-sub-member',), value_type=Pattern.STATE_SWITCH),

           Pattern('ctx-sub-member',
                   value_type=Pattern.STATE_SWITCH))

# Error: ArgumentOutOfContext
cmd(s, 'app --ctx-member')
cmd(s, 'app --bool --ctx-member')
cmd(s, 'app --bool --ctx-bool --ctx-member --ctx-sub-ctx --ctx-sub-member')



#------------------------------------------------------------------------------#
s = Scheme(Program('app',
                   members=('bool', 'uni-bool', 'ctx-bool', 'pri-bool')),

           Pattern('bool',
                   value_type=Pattern.STATE_SWITCH),

           Pattern('uni-bool',
                   flag_type=Pattern.UNIQUE,
                   value_type=Pattern.STATE_SWITCH),

           Pattern('pri-bool',
                   flag_type=Pattern.PRIMAL,
                   value_type=Pattern.STATE_SWITCH),

           Pattern('ctx-bool',
                   value_type=Pattern.STATE_SWITCH,
                   members=('ctx-uni-member', 'ctx-pri-member', 'pri-bool', 'ctx-nested')),

           Pattern('ctx-uni-member',
                   flag_type=Pattern.UNIQUE,
                   value_type=Pattern.STATE_SWITCH),

           Pattern('ctx-pri-member',
                   flag_type=Pattern.PRIMAL,
                   value_type=Pattern.STATE_SWITCH),

           Pattern('ctx-nested',
                   value_type=Pattern.STATE_SWITCH,
                   members=('ctx-sub-ctx',)),

           Pattern('ctx-sub-ctx',
                   value_type=Pattern.STATE_SWITCH,
                   members=('ctx-sub-member')),
           Pattern('ctx-sub-member',
                   flag_type=Pattern.PRIMAL,
                   value_type=Pattern.STATE_SWITCH))

# Error: DoubleUniqueArgument
cmd(s, 'app --bool --bool --uni-bool --uni-bool')
cmd(s, 'app --ctx-bool --ctx-uni-member --bool --ctx-bool --ctx-uni-member')

# Error: DoublePrimalArgument
cmd(s, 'app --pri-bool --ctx-bool --pri-bool') # => should not raise error
cmd(s, 'app --pri-bool --bool --pri-bool')
cmd(s, 'app --ctx-bool --pri-bool --pri-bool')
cmd(s, 'app --ctx-bool --ctx-nested --ctx-sub-ctx --ctx-sub-member --ctx-sub-member')



#------------------------------------------------------------------------------#
s = Scheme(Program('app',
                   member_type=Pattern.ONE,
                   members=('alpha', 'beta', 'gamma')),

           Pattern('alpha',
                   value_type=Pattern.STATE_SWITCH),

           Pattern('beta',
                   value_type=Pattern.STATE_SWITCH),

           Pattern('gamma',
                   member_type=Pattern.ONE,
                   members=('delta', 'epsilon'),
                   value_type=Pattern.STATE_SWITCH),

           Pattern('delta',
                   short_flags='dD',
                   value_type=Pattern.STATE_SWITCH),

           Pattern('epsilon',
                   value_type=Pattern.STATE_SWITCH))

# Error: TooManyMembersUsed
cmd(s, 'app --alpha --beta')
cmd(s, 'app --gamma --delta --delta --epsilon')
cmd(s, 'app --gamma --delta -d -D --epsilon')
