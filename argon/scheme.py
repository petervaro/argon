## INFO ##
## INFO ##

# Import python modules
from sys           import stdout, stderr
from re            import compile, split
from shutil        import get_terminal_size

# Import dagger modules
from dagger.graph  import Graph
from dagger.tools  import topo_sort, a_star, DAGCycleError

# Import argon modules
from argon.text    import Section
from argon.pattern import Pattern



#------------------------------------------------------------------------------#
class Scheme:

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    # Internal errors
    class _ContextFound(Exception)       : pass
    class _CloseCurrentPattern(Exception) : pass


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    # Public errors
    class SchemeException(Exception)              : pass
    class LongFlagIsNotUnique(SchemeException)    : pass
    class InvalidPatternMember(SchemeException)   : pass
    class InvalidArgument(SchemeException)        : pass
    class InvalidMemberReference(SchemeException) : pass
    class ArgumentOutOfContext(SchemeException)   : pass
    class CircularReferences(SchemeException)     : pass
    class DoubleUniqueArgument(SchemeException)   : pass
    class DoublePrimalArgument(SchemeException)   : pass
    class MemberTypeAlreadyUsed(SchemeException)  : pass


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    # Internal branch-builder helper recursive function
    @staticmethod
    def _branch(parent):
        branch = {}
        for child in parent.vertices():
            branch[child.id] = Scheme._branch(child)
        return branch


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, *pattern_objects):
        # Create graphs (forward and reversed)
        fgraph = Graph()
        rgraph = Graph()

        # Create a flat map of all patterns, and
        # a flag map (associate all flags with all patterns), and
        # a graph all patterns, to build context hierarchy
        self._flags    = flags    = {}
        self._patterns = patterns = {}
        for pattern in pattern_objects:
            if patterns.get(pattern.name, None):
                raise Pattern.LongFlagIsNotUnique
            patterns[pattern.name] = pattern
            fgraph.add_vertex(pattern.name)
            rgraph.add_vertex(pattern.name)
            for flag in pattern.flags:
                flags[flag] = pattern

        # Build graph edges
        for name, pattern in patterns.items():
            # If pattern is a context, create edges to its members
            for member in pattern._members:
                # If member is an Pattern instance
                if isinstance(member, Pattern):
                    fgraph.add_edge(name, member.name)
                    rgraph.add_edge(member.name, name)
                # If member is a string-name reference
                elif isinstance(member, str):
                    # If member is not a real reference
                    if member not in patterns:
                        raise Scheme.InvalidMemberReference(member)
                    fgraph.add_edge(name, member)
                    rgraph.add_edge(member, name)
                # If member is not a Pattern nor a string
                else:
                    raise Scheme.InvalidPatternMember(
                        "Type of members of Pattern {!r} "
                        "should be 'str' or 'Pattern' not "
                        "{.__class__.__qualname__!r}".format(name, member))

        # Build context hierarchy
        self._hierarchy = hierarchy = {}
        try:
            for vertex in topo_sort(fgraph, tracking=True):
                # If vertex doesn't have parent(s)
                if not rgraph.vertex(vertex.id).vertices():
                    # Build its branch
                    hierarchy[vertex.id] = Scheme._branch(vertex)
        # If there are circular references in the graph
        except DAGCycleError as message:
            raise Scheme.CircularReferences(message.args) from None


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def _parse_iter(self, arguments):
        """
        Each flag will be translated to a tuple:

            ('<long_flag>', <value(s)>, [<member(s)>])

        Errors:
            Pattern.FinishedPattern
                Raised when trying to add value to STATE_SWITCH or SINGLE_VALUE
            Pattern.UnfinishedPattern
                Raised when name given but value is missing from NAMED_VALUES
            Scheme.InvalidArgument
                Raised when trying to add value to a non-open pattern
            Scheme.ArgumentOutOfContext
                Raised when pattern is valid but not in the given context
            Scheme.DoubleUniqueArgument
                Raised when UNIQUE pattern is used more than once
            Scheme.DoublePrimalArgument
                Raised when PRIMAL pattern is used more than once in context
            Scheme.MemberTypeAlreadyUsed
                Raised when members are limited to be used ONE time only
        """
        flags        = self._flags
        hierarchy    = self._hierarchy
        arguments    = iter(arguments)
        context      = hierarchy
        contexts     = [context]
        curr_values  = None
        open_values  = []
        curr_members = None
        open_members = []
        processed    = []
        curr_ones    = None
        open_ones    = []
        unique_flags = set()
        curr_primals = set()
        primal_flags = [curr_primals]

        #for argument in arguments:
        while True:
            # If any unprocessed arguments left
            try:
                # Get next argument
                argument = next(arguments)
                # Get pattern object associated with flag (argument)
                try:
                    pattern = flags[argument]
                    # If pattern is UNIQUE
                    if pattern.flag_type == Pattern.UNIQUE:
                        # If unique pattern already used
                        if pattern.name in unique_flags:
                            raise Scheme.DoubleUniqueArgument(argument) from None
                        # If not used, mark it as first used
                        unique_flags.add(pattern.name)
                # If no pattern found
                except KeyError:
                    # If there is an open pattern waiting for values
                    try:
                        curr_values.add_value(argument)
                        # Move on to the next argument
                        continue
                    # If there are no open patterns waiting for values
                    except AttributeError:
                        raise Scheme.InvalidArgument(argument) from None

                # Try to find the context of the flag
                name = pattern.name
            # If all arguments processed
            except StopIteration:
                # Start a "close-all-left" cycle, where an invalid-name will
                # cause the context-search to close all left open patterns
                name = NotImplemented

            try:
                while True:
                    try:
                        # If context of pattern found (current context)
                        if name in context:
                            # Close current context and open a new pattern
                            raise Scheme._CloseCurrentPattern(True)

                        # Check if context of pattern is a new sub-context
                        for sub_context in context.values():
                            # If context of pattern found
                            if name in sub_context:
                                # Open new context
                                contexts.append(sub_context)
                                # Jump one level down
                                context = sub_context
                                # Create new primal flag context
                                curr_primals = set()
                                primal_flags.append(curr_primals)
                                # Finished searching
                                raise Scheme._ContextFound

                        # If context of pattern is not found
                        # (in current context and in sub-context)
                        # Close current context and jump one level up
                        try:
                            contexts.pop()
                            context = contexts[-1]
                            curr_primals = primal_flags.pop()
                        except IndexError:
                            # If this is a regular cycle, not a "close-all-left"
                            if name is not NotImplemented:
                                raise Scheme.ArgumentOutOfContext(argument) from None

                        # Close current pattern and
                        # continue searching for context
                        raise Scheme._CloseCurrentPattern(False)

                    # Close current pattern
                    except Scheme._CloseCurrentPattern as message:
                        # If this is the nth argument
                        try:
                            # Create pattern-tuple
                            curr = (curr_values.name,
                                    curr_values.close(name, argument),
                                    open_members.pop())

                            # Store last members as a processed value
                            processed = curr[-1]

                            # Jump a level up
                            curr_members = open_members[-1]
                            curr_members.append(curr)
                            open_values.pop()
                            curr_values = open_values[-1]
                            open_ones.pop()
                            curr_ones = open_ones[-1]

                        # If this is the first argument
                        except AttributeError:
                            pass

                        # If context has also found
                        if message.args[0]:
                            raise Scheme._ContextFound

            # If a new pattern can be opened
            except Scheme._ContextFound:
                # If current context limits the number of use of its members
                try:
                    # If member has already been used
                    if len(curr_ones):
                        raise Scheme.MemberTypeAlreadyUsed(
                            curr_ones.pop(), argument) from None
                    # If this is the first time, this member appeared
                    curr_ones.add(argument)
                # If current context allows for its
                # member to appear more than once
                except TypeError:
                    pass

                # If pattern is PRIMAL
                if pattern.flag_type == Pattern.PRIMAL:
                    # If primal pattern already used in the current context
                    if name in curr_primals:
                        raise Scheme.DoublePrimalArgument(argument) from None
                    # If not used, mark it as used for the first time
                    curr_primals.add(name)

                # Open a new pattern
                curr_values  = \
                    pattern.object_hook(name, argument, pattern.value_necessity)
                curr_members = []
                open_values.append(curr_values)
                open_members.append(curr_members)

                # If this context limits the number of appearences of its
                # members, use a collections, otherwise a None
                curr_ones = set() if pattern.member_type is Pattern.ONE else None
                open_ones.append(curr_ones)

            # If reached the top-level and the context still did not match
            except IndexError:
                # Return translated arguments
                return [(curr_values.name,
                         curr_values.close(name, argument),
                         processed)]


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def parse_iter(self, arguments,
                         debug        = False,
                         catch_errors = False):
        if debug:
            print('\nRaw command:', *arguments, sep=' ')
            print('Context hierarchy:', self._hierarchy)
            print('All flags:', ', '.join(self._flags.keys()))
        if catch_errors:
            # TODO: ** "Graphical" error strings **
            #       At some point add better feedback to object
            #       hook when closing, to produce error like
            #       this:
            #
            #           fullcmd --this --that
            #                   ^^^^^^ ~~~~~~
            #       UnfinishedPattern: SINGLE_VALUE, --this, --that
            try:
                return self._parse_iter(arguments)
            except Pattern.FinishedPattern as e:
                type, flag, value = e.args
                try:
                    print({
                        Pattern.STATE_SWITCH:
                            'Flag {!r} does not take any values, '
                            'but one was given: {!r}',
                        Pattern.SINGLE_VALUE:
                            'Flag {!r} takes only a single value, '
                            'but another one was given: {!r}',
                        }[type].format(flag, value), file=stderr)
                except KeyError:
                    raise e
            except Pattern.UnfinishedPattern as e:
                type, flag, value = e.args
                try:
                    print({
                        Pattern.SINGLE_VALUE:
                            'Flag {!r} takes exactly one value, but '
                            'none was given before: {!r}',
                        Pattern.COMMON_ARRAY:
                            'Flag {!r} takes at least one value, but '
                            'none was given before: {!r}',
                        Pattern.UNIQUE_ARRAY:
                            'Flag {!r} takes at least one value, but '
                            'none was given before: {!r}',
                        Pattern.NAMED_VALUES:
                            'Flag {!r} takes at least one value pair, but '
                            'none was given before: {!r}',
                        }[type].format(flag, value), file=stderr)
                except KeyError:
                    raise e
            except Scheme.ArgumentOutOfContext as e:
                raise
        else:
            return self._parse_iter(arguments)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def parse_args(self, *arguments,
                         debug        = False,
                         catch_errors = False):
        return self.parse_iter(arguments, debug, catch_errors)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def parse_line(self, arguments,
                         debug         = False,
                         catch_errors  = False,
                         split_pattern = compile(r'(?<!\\)\s+')):
        return self.parse_iter(split(split_pattern, arguments), debug, catch_errors)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    @staticmethod
    def branch_traverse(patterns):
        """
        Returns:

            (<long_flag>, <value>)
        """
        for flag, value, members in patterns:
            yield flag, value
            yield from Scheme.branch_traverse(members)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    @staticmethod
    def branch_full_traverse(patterns, path=[]):
        """
        Returns:

            ([<group>..., <long_flag>], <value>)
        """
        for flag, value, members in patterns:
            path.append(flag)
            yield path, value
            yield from Scheme.branch_full_traverse(members, path)
            path.pop()


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    @staticmethod
    def breadth_first_traverse(patterns):
        """
        Traverse will walk through the translated arguments as a generator.
        Unlike the self.translate_args() method, it returns a yuple of four
        values:

            (<group>, <long_flag>, <value>, [<members>...])
        """
        patterns = [(None, patterns)]
        for group, gmembers in patterns:
            for flag, value, fmembers in gmembers:
                yield group, flag, value, fmembers
                patterns.append((flag, fmembers))


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def write_help(self, *blocks,
                         file     = stdout,
                         width    = None,
                         tab_size = 4,
                         no_color = False):
        # Write all blocks to file
        Section(*blocks).write(indent   = 0,
                               stream   = file,
                               width    = width or get_terminal_size().columns,
                               spaces   = abs(int(tab_size))*' ',
                               no_color = no_color,
                               owner    = None,
                               patterns  = self._patterns)