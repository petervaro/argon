## INFO ##
## INFO ##

from argon import *

def cmd(scheme, line):
    processed = scheme.parse_line(line, True, True)
    if processed:
        print('==> Processed:\n    ', processed, sep='')

#------------------------------------------------------------------------------#
s = Scheme(Program('app', members=('bool', 'value', 'clist', 'ulist', 'map')),
           Pattern('bool', value_type=Pattern.STATE_SWITCH),
           Pattern('value'),
           Pattern('clist', value_type=Pattern.COMMON_ARRAY),
           Pattern('ulist', value_type=Pattern.UNIQUE_ARRAY),
           Pattern('map', value_type=Pattern.NAMED_VALUES))

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
s = Scheme(Program('app', members=('bool', 'value', 'clist', 'ulist', 'map', 'ctx-bool', 'ctx-nested')),
           Pattern('bool', value_type=Pattern.STATE_SWITCH),
           Pattern('value'),
           Pattern('clist', value_type=Pattern.COMMON_ARRAY),
           Pattern('ulist', value_type=Pattern.UNIQUE_ARRAY),
           Pattern('map', value_type=Pattern.NAMED_VALUES),
           Pattern('ctx-bool', members=('ctx-member',), value_type=Pattern.STATE_SWITCH),
           Pattern('ctx-member', value_type=Pattern.STATE_SWITCH),
           Pattern('ctx-nested', members=('ctx-subctx',), value_type=Pattern.STATE_SWITCH),
           Pattern('ctx-subctx', members=('ctx-submember',), value_type=Pattern.STATE_SWITCH),
           Pattern('ctx-submember', value_type=Pattern.STATE_SWITCH))

# Error: ArgumentOutOfContext
cmd(s, 'app --ctx-member')
cmd(s, 'app --bool --ctx-member')
cmd(s, 'app --bool --ctx-bool --ctx-member --ctx-subctx --ctx-submember')



#------------------------------------------------------------------------------#
s = Scheme(Program('app', members=('bool', 'value', 'clist', 'ulist', 'map')),
           Pattern('bool', value_type=Pattern.STATE_SWITCH),
           Pattern('value'),
           Pattern('clist', value_type=Pattern.COMMON_ARRAY),
           Pattern('ulist', value_type=Pattern.UNIQUE_ARRAY),
           Pattern('map', value_type=Pattern.NAMED_VALUES))

# Error: DoubleUniqueArgument
cmd(s, 'app')

# Error: DoublePrimalArgument
cmd(s, 'app')