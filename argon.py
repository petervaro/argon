## INFO ##
## INFO ##

# Import python modules
from itertools    import chain
from sys          import stdout
from collections  import OrderedDict
from string       import ascii_letters, digits

# Import orderedset modules
from orderedset   import OrderedSet

# Import dagger modules
from dagger.graph import Graph
from dagger.tools import topo_sort, a_star, DAGCycleError



#------------------------------------------------------------------------------#
class Option:
    """
    Valid characters for flags are:
        abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-

    member_type:
    ------------
        ONE:
            Only one member allowed at the current level

        ANY (default):
            Any members allowed at the current level


    value_type:
    -----------
        STATE_SWITCH:

                Eg. cmd --that
                    cmd --this --that

            Will be translated to (simplified):

                {this: False, that: True}
                {this: True, that: True}

        SINGLE_VALUE (default):

                Eg. cmd --this hello --that

            Will be translated to (simplified):

                {'this': 'hello', 'that': True}

        COMMON_ARRAY:

                Eg. cmd --this a b c a b c d --that

            Will be translated to (simplified):

                {'this': ['a', 'b', 'c', 'a', 'b', 'c', 'd'], 'that': True}

        UNIQUE_ARRAY:

                Eg. cmd --this a b c a b c d --that

            Will be translated to (simplified):

                {'this': ['a', 'b', 'c', 'd'], 'that': True}

        NAMED_VALUES:

                Eg. cmd --this hello 0 world 1 --that

            Will be translated to (simplified):

                {'this': {'hello': '0', 'world': '1'}, 'that': True}


    flag_type:
    ----------
        COMMON (default):
            Flag can appear more than one times anywhere in the command
            sequence. Therefore the following example is perfectly valid:

                cmd --this w --group1 --this x --this y --group2 --this z

        PRIMAL:
            Flag can appear only once in every scope (top-level, group,
            sub-group). Therefore the following example is perfectly valid:

                cmd --this x --group1 --this y --group2 --this z

            However the followings are not valid:

                cmd --this x --this y
                cmd --this x --group --this y --this z

        UNIQUE:
            Flag can appear only once anywhere. Therefore the following example
            is perfectly valid:

                cmd --this x

            However the next example is not:

                cmd --this x --group --this y
                cmd --group --this x --this y
                cmd --group1 --this x --group2 --this y
    """

    __VALID       = ascii_letters + digits + '_-'
    __FLAG_TYPE   = tuple(range(3))
    __MEMBER_TYPE = tuple(range(2))

    # 'flag_type-enums'
    (COMMON,
     PRIMAL,
     UNIQUE) = __FLAG_TYPE

    # 'member_type-enum'
    (ONE,
     ANY) = __MEMBER_TYPE


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    class OptionException(Exception): pass
    class InvalidFlagName(OptionException): pass
    class FinishedOption(OptionException): pass
    class UnfinishedOption(OptionException): pass


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    class _ObjectHook:

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
        @property
        def name(self):
            return self._name

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
        def close(self, flag):
            return self._values


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    class STATE_SWITCH(_ObjectHook):


        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
        def __init__(self, name):
            self._name = name
            self._values = True

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
        def add_value(self, value):
            raise Option.FinishedOption(self._name, value) from None



    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    class SINGLE_VALUE(_ObjectHook):

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
        def __init__(self, name):
            self._name = name
            self._values = NotImplemented

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
        def add_value(self, value):
            if self._values is not NotImplemented:
                raise Option.FinishedOption(self._name, value) from None
            self._values = value

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
        def close(self, flag):
            if self._values is NotImplemented:
                raise Option.UnfinishedOption((self._name, flag)) from None
            return self._values


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    class COMMON_ARRAY(_ObjectHook):

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
        def __init__(self, name):
            self._name = name
            self._values = []

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
        def add_value(self, value):
            self._values.append(value)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
        def close(self, flag):
            if not self._values:
                raise Option.UnfinishedOption((self._name, flag)) from None
            return self._values


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    class UNIQUE_ARRAY(_ObjectHook):

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
        def __init__(self, name):
            self._name = name
            self._values = OrderedSet()

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
        def add_value(self, value):
            self._values.add(value)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
        def close(self, flag):
            if not self._values:
                raise Option.UnfinishedOption((self._name, flag)) from None
            return self._values


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    class NAMED_VALUES(_ObjectHook):

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
        def __init__(self, name):
            self._name = name
            self._key = NotImplemented
            self._values = OrderedDict()

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
        def add_value(self, value):
            if self._key is NotImplemented:
                self._key = value
            else:
                self._values[self._key] = value
                self._key = NotImplemented

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
        def close(self, flag):
            if (not self._values or
                self._key is not NotImplemented):
                    raise Option.UnfinishedOption((self._name, flag)) from None
            return self._values


    # 'value_type-enums'
    __VALUE_TYPE = (STATE_SWITCH,
                    SINGLE_VALUE,
                    COMMON_ARRAY,
                    UNIQUE_ARRAY,
                    NAMED_VALUES)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    @property
    def name(self):
        return self._name


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    @property
    def flags(self):
        yield from self._flags


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    @property
    def members(self):
        yield from self._members


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    @property
    def object_hook(self):
        return self._object_hook


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    @property
    def description(self):
        return self._description


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, long_flag,
                       short_flags  = (),
                       long_prefix  = '--',
                       short_prefix = '-',
                       flag_type    = COMMON,
                       members      = (),
                       member_type  = ANY,
                       value_type   = SINGLE_VALUE,
                       description  = ''):
        # Check for flag's validity
        short_flags = set(short_flags)
        for flag in chain((long_flag,), short_flags):
            if not isinstance(flag, str):
                raise Option.InvalidFlagName(
                    "Flag's type should be 'str', not {0.__class__.__name__!r} "
                    "for flag {0!r}".format(flag))
            # If the user accidentally added the `-` or `--` prefixes
            # TODO: check for `/` windows prefix as well
            if flag.startswith('-'):
                raise Option.InvalidFlagName("Flag name cannot start with '-'")
            # If character is inappropriate
            for char in flag:
                if char not in Option.__VALID:
                    raise Option.InvalidFlagName(
                        'Flag name {!r} has an '
                        'invalid character {!r}'.format(flag, char))
        # Store flags
        self._name  = long_flag
        self._flags = {f for f in chain((long_prefix + long_flag,),
                                        (short_prefix + s for s in short_flags))}

        # Check and store flag_type
        if flag_type not in Option.__FLAG_TYPE:
            raise ValueError("'flag_type' has to be Option.COMMON "
                             "or Option.PRIMAL or Option.UNIQUE, "
                             "not {!r}".format(flag_type))
        self._flag_type = flag_type

        # Check and store value_type
        if value_type not in Option.__VALUE_TYPE:
            raise ValueError("'value_type' has to be Option.STATE "
                             "or Option.VALUE or Option.ARRAY "
                             "or Option.PAIRS, not {!r}".format(value_type))
        self._object_hook = value_type


        # Store static values
        self._members     = set(members)
        self._description = description



#------------------------------------------------------------------------------#
class Arguments(Graph):

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    class ArgumentsException(Exception): pass
    class InvalidOptionMember(ArgumentsException): pass
    class InvalidArgument(ArgumentsException): pass
    class ArgumentOutOfContext(ArgumentsException): pass
    class CyclicOptionRelations(ArgumentsException): pass

    class _ContextFound(Exception): pass


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    # Branch-builder helper recursive function
    @staticmethod
    def _branch(parent):
        branch = {}
        for child in parent.vertices():
            branch[child.id] = Arguments._branch(child)
        return branch


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, *option_objects):
        # Make Arguments a Graph
        super().__init__()

        # Create graphs (forward, reversed) and root vertex (id=0)
        fgraph = Graph()
        rgraph = Graph()

        # Create a flat map, a flag map and a graph from options
        options = {}
        self._flags = flags = {}
        for option in option_objects:
            options[option.name] = option
            fgraph.add_vertex(option.name)
            rgraph.add_vertex(option.name)
            for flag in option.flags:
                flags[flag] = option

        # Build graph edges
        for name, option in options.items():
            # If option is a group, create edges to its members
            for member in option._members:
                # If member is an Option instance
                if isinstance(member, Option):
                    fgraph.add_edge(name, member.name)
                    rgraph.add_edge(member.name, name)
                # If member is a string-name reference
                elif isinstance(member, str):
                    fgraph.add_edge(name, member)
                    rgraph.add_edge(member, name)
                # If not Option nor string
                else:
                    raise Arguments.InvalidOptionMember(
                        "Option.member's type should be 'str' or 'Option' "
                        "for member {!r} of option {!r}".format(member, name))

        # Build hierarchy
        self._hierarchy = hierarchy = {}
        try:
            for vertex in topo_sort(fgraph, tracking=True):
                # If vertex doesn't have parent(s)
                if not rgraph.vertex(vertex.id).vertices():
                    # Build its branch
                    hierarchy[vertex.id] = Arguments._branch(vertex)
        except DAGCycleError as cycle:
            raise Arguments.CyclicOptionRelations(cycle) from None


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def translate_args(self, arguments):
        """
        Each flag will be translated to a tuple:

            ('<long_flag>', <value>, [<members>])

        Errors:
            Option.FinishedOption
            Option.UnfinishedOption
            Arguments.InvalidArgument
            Arguments.ArgumentOutOfContext
        """
        flags        = self._flags
        hierarchy    = self._hierarchy
        context      = hierarchy
        contexts     = [context]
        curr_values  = None
        open_values  = []
        curr_members = None
        open_members = []
        #unique_flags = set()

        for argument in arguments:
            # Get option object associated with flag (argument)
            try:
                option = flags[argument]
            # If no option found
            except KeyError:
                # If there is an open option waiting for values
                try:
                    curr_values.add_value(argument)
                    # Move on to the next argument
                    continue
                # If there are no open options waiting for values
                except AttributeError:
                    raise Arguments.InvalidArgument(argument) from None

            # Try to find the context of the flag
            name = option.name
            try:
                while True:
                    # If context of option found (current context)
                    if name in context:
                        # If nth argument
                        try:
                            # Close current option
                            curr = (curr_values.name, curr_values.close(name), open_members.pop())
                            curr_members = open_members[-1]
                            curr_members.append(curr)
                            open_values.pop()
                            curr_values = open_values[-1]
                        # If first argument
                        except AttributeError:
                            pass
                        # Finished closing
                        raise Arguments._ContextFound

                    # Check if context of option is a new sub-context
                    for sub_context in context.values():
                        # If context of option found
                        if name in sub_context:
                            # Open new context
                            contexts.append(sub_context)
                            # Jump one level down
                            context = sub_context
                            # Finished closing
                            raise Arguments._ContextFound
                    # If context of option is not found
                    # (in current context and in sub-context)
                    # Close current context and jump one level up
                    contexts.pop()
                    context = contexts[-1]
                    # Close current option
                    # TODO: At some point add better feedback to object hook
                    #       when closing, to produce error like this:
                    #       UnfinishedOption: this, abc
                    #           fullcmd --this --that abc xyz
                    #                   ~~~~~~        ^^^
                    curr = (curr_values.name, curr_values.close(name), open_members.pop())
                    # Jump a level up
                    curr_members = open_members[-1]
                    curr_members.append(curr)
                    open_values.pop()
                    curr_values = open_values[-1]
            except IndexError:
                raise Arguments.ArgumentOutOfContext(argument) from None
            except Arguments._ContextFound:
                pass

            # Open a new option
            curr_values  = option.object_hook(name)
            curr_members = []
            open_values.append(curr_values)
            open_members.append(curr_members)

        # Close all open options
        while True:
            try:
                processed = open_members.pop()
                # Close current option
                curr = (curr_values.name, curr_values.close(name), processed)
                # Jump a level up
                curr_members = open_members[-1]
                curr_members.append(curr)
                open_values.pop()
                curr_values = open_values[-1]
            except IndexError:
                processed = [(curr_values.name, curr_values.close(name), processed)]
                break

        # Return translated arguments
        return processed


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def traverse_args(self, arguments):
        """
        Traverse will walk through the translated arguments as a generator.
        Unlike the self.translate_args() method, it returns a yuple of four
        values:

            (<group>, <long_flag>, <value>, [<members>])
        """
        options = [(None, self.translate_args(arguments))]
        for group, gmembers in options:
            for flag, value, fmembers in gmembers:
                yield group, flag, value, fmembers
                options.append((flag, fmembers))


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def write_help(self, file=stdout):
        pass



#------------------------------------------------------------------------------#
if __name__ == '__main__':
    args = Arguments(Option(long_flag   = 'pmt',
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


    # Example command
    cmd = ('pmt', 'set', 'issues', '-t', 'milestones',
                                         '-m', 'open',
                                   '-t', 'issues',
                                         '-L', 'MyOtherLabel',
                                   '-v',
                                         'status', 'closed',
                                         'labels', 'MyLabel',)

    print('Processing command:', ' '.join(cmd), sep='\n    ', end='\n\n')

    print('Translated:\n')
    print(args.translate_args(cmd))

    print('\nTraversed:\n')
    # Get processed arguments
    args = args.traverse_args(cmd)

    # Get command and its value (if any)
    _, command, value, _ = next(args)
    print('command:', command)

    # Process flags
    for group, flag, value, _ in args:
        print(group, '.', flag, ' = ', value, sep='')
















