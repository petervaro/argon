## INFO ##
## INFO ##

# Import python modules
from textwrap     import fill
from itertools    import chain
from os           import isatty
from sys          import stdout
from collections  import OrderedDict
from shutil       import get_terminal_size
from string       import ascii_letters, digits

# Import orderedset modules
from orderedset   import OrderedSet

# Import dagger modules
from dagger.graph import Graph
from dagger.tools import topo_sort, a_star, DAGCycleError



#------------------------------------------------------------------------------#
class Text:

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    class Block:

        INDENT = 0

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
        @property
        def owner(self):
            return self._owner

        @owner.setter
        def owner(self, owner):
            self._owner = owner

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
        def __init__(self, *blocks,
                           indent = None):
            self._blocks = blocks
            self._indent = self.INDENT if indent is None else indent

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
        def write(self, indent,
                        stream,
                        width,
                        spaces,
                        ending   = '\n',
                        owner    = None,
                        options  = {},
                        no_color = False,
                        strong   = False):
            # Indent and wrap text
            indent = (indent + self._indent)*spaces
            text = []
            for paragraph in self._blocks:
                text.append(fill(paragraph, width, initial_indent    = indent,
                                                   subsequent_indent = indent))
            text = '\n'.join(text)

            # Colorize text if instructed
            # and colors are available
            try:
                if (not no_color and
                    strong and
                    isatty(stream.fileno())):
                        text = '\033[1m{}\033[0m'.format(text)
            except AttributeError:
                pass

            # Write content to stream
            print(text, file=stream, end=ending)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    class Section(Block):

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
        def write(self, *args, **kwargs):
            if kwargs['owner'] is None:
                try:
                    kwargs['owner'] = self._owner
                except AttributeError:
                    pass

            kwargs['indent'] += self._indent

            for block in self._blocks:
                # If block is a string reference to an Option
                if isinstance(block, str):
                    try:
                        block = kwargs['options'][block].description
                    except KeyError:
                        raise ValueError('Option not in Arguments: '
                                         '{!r}'.format(block)) from None

                # If block is an Option object
                elif isinstance(block, Option):
                    block = block.description

                # If block is something unexpected
                if not isinstance(block, Text.Block):
                    raise ValueError('Text.Section expected Option or name of '
                                     'Option (as str) or Text.Block object, '
                                     'got {.__class__.__qualname__!r}'.format(block))
                # Write block
                block.write(*args, **kwargs)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    class Header(Block):

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
        def write(self, *args, **kwargs):
            super().write(*args, strong=True, **kwargs)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    class Paragraph(Block):

        INDENT = 1

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
        def write(self, *args, **kwargs):
            super().write(*args, ending='\n\n', **kwargs)



    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    class Span(Block):

        INDENT = 1


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    class Flags(Block):

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
        def __init__(self, *args,
                           new_line=False,
                           **kwargs):
            self._new_line = new_line
            super().__init__(*args, **kwargs)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
        def write(self, *args, **kwargs):
            values = ' '.join(self._blocks)
            text   = []
            blocks = self._blocks
            # Construct flags
            try:
                for flag in reversed(sorted(kwargs['owner'].flags)):
                    text.append(flag + ((' ' + values) if values else ''))
            except AttributeError:
                raise ValueError('Text.Flag should be used inside a '
                                 'Text.Section, which will be passed to an '
                                 'Option, before the writing is '
                                 'happening') from None
            # TODO: ** Clean this mess up **
            #       Make it simple and beautiful
            if self._new_line:
                self._blocks = [f + ',' for f in text[:-1]]
                self._blocks.append(text[-1])
            else:
                self._blocks = (', '.join(text),)

            # Write content to stream
            super().write(*args, strong=True, **kwargs)
            self._blocks = blocks



#------------------------------------------------------------------------------#
class Option:
    """
    By default valid characters for flags are:

        abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-

    But this can be overwritten, by passing a `char_validator` function to the
    Option object during the initialization.

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

            However the next examples are not:

                cmd --this x --this y
                cmd --this x --group --this y --this z

        UNIQUE:
            Flag can appear only once anywhere. Therefore the following example
            is perfectly valid:

                cmd --this x

            However the next examples are not:

                cmd --this x --group --this y
                cmd --group --this x --this y
                cmd --group1 --this x --group2 --this y
    """

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
    class OptionException(Exception)        : pass
    class InvalidFlagName(OptionException)  : pass
    class FinishedOption(OptionException)   : pass
    class UnfinishedOption(OptionException) : pass


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

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    @staticmethod
    def CHAR_VALIDATOR(string, valid_chars=ascii_letters + digits + '_-'):
        for char in string:
            if char not in valid_chars:
                raise Option.InvalidFlagName(
                    'Flag name {!r} has an '
                    'invalid character {!r}'.format(string, char)) from None


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
    def flag_type(self):
        return self._flag_type


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    @property
    def member_type(self):
        return self._member_type


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
                       short_flags    = (),
                       long_prefix    = '--',
                       short_prefix   = '-',
                       flag_type      = COMMON,
                       members        = (),
                       member_type    = ANY,
                       value_type     = SINGLE_VALUE,
                       char_validitor = CHAR_VALIDATOR.__func__,
                       description    = ''):
        # Check for flag's validity
        short_flags = set(short_flags)
        for flag in chain((long_flag,), short_flags):
            if not isinstance(flag, str):
                raise Option.InvalidFlagName(
                    "Flag's type should be 'str', not {0.__class__.__qualname__!r} "
                    "for flag {0!r}".format(flag))
            # If the user accidentally added the `-` or `--` prefixes
            # TODO: check for `/` windows prefix as well
            if flag.startswith('-'):
                raise Option.InvalidFlagName("Flag name cannot start with '-'")
            # Check every character if it is inappropriate
            char_validitor(flag)

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
            raise ValueError("'value_type' has to be Option.STATE_SWITCH "
                             "or Option.SINGLE_VALUE or Option.COMMON_ARRAY "
                             "or Option.UNIQUE_ARRAY or Option.NAMED_VALUES, "
                             "not {!r}".format(value_type))
        self._object_hook = value_type

        # Check and store member_type
        if member_type not in Option.__MEMBER_TYPE:
            raise ValueError("'member_type' has to be Option.ONE or "
                             "Option.ANY, not {!r}".format(member_type))
        self._member_type = member_type

        # Check and store description
        if isinstance(description, str):
            description = Text.Section(
                Text.Flags({Option.STATE_SWITCH: '',
                            Option.SINGLE_VALUE: '<value>',
                            Option.COMMON_ARRAY: '<value>...',
                            Option.UNIQUE_ARRAY: '<value>...',
                            Option.NAMED_VALUES: '<key> <value>...'}[value_type]),
                Text.Paragraph(description))
        elif not isinstance(description, Text.Section):
            raise TypeError("'description' expected str or Text.Section, "
                            "got {.__class__.__qualname__!r}".format(description))
        description.owner = self
        self._description = description

        # Store static values
        if isinstance(members, str):
            self._members = {members}
        else:
            self._members = set(members)



#------------------------------------------------------------------------------#
class Command(Option):
    """Convenient wrapper class around Option"""

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    @staticmethod
    def ACCEPT_ANYTHING(string):
        pass


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, long_flag, *args, **kwargs):
        # Check if command has members
        if not kwargs.get('members', None):
            raise ValueError("Missing or empty 'members' for Command")
        # If otherwise not specified set command as a switch
        kwargs.setdefault('value_type', Option.STATE_SWITCH)
        # If otherwise not specified set char_validator to accept file names
        kwargs.setdefault('char_validitor', Command.ACCEPT_ANYTHING)

        # Create basic documentation
        description = kwargs.get('description', '')
        if isinstance(description, str):
            kwargs['description'] = Text.Section(
                Text.Header('NAME'),
                Text.Paragraph(long_flag +
                               ((' - ' + description) if description else '')))

        # Initialize Option
        super().__init__(long_flag,
                         *args,
                         long_prefix='',
                         flag_type=Option.UNIQUE,
                         **kwargs)



#------------------------------------------------------------------------------#
class Arguments:

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    # Internal errors
    class _ContextFound(Exception)       : pass
    class _CloseCurrentOption(Exception) : pass


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    # Public errors
    class ArgumentsException(Exception)             : pass
    class InvalidOptionMember(ArgumentsException)   : pass
    class InvalidArgument(ArgumentsException)       : pass
    class ArgumentOutOfContext(ArgumentsException)  : pass
    class CyclicOptionRelations(ArgumentsException) : pass
    class DoubleUniqueArgument(ArgumentsException)  : pass
    class DoublePrimalArgument(ArgumentsException)  : pass
    class MemberTypeAlreadyUsed(ArgumentsException) : pass


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    # Internal branch-builder helper recursive function
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
        self._flags   = flags   = {}
        self._options = options = {}
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
                Raised when trying to add value to STATE_SWITCH or SINGLE_VALUE
            Option.UnfinishedOption
                Raised when name given but value is missing from NAMED_VALUES
            Arguments.InvalidArgument
                Raised when trying to add value to a non-open option
            Arguments.ArgumentOutOfContext
                Raised when option is valid but not in the given context
            Arguments.DoubleUniqueArgument
                Raised when UNIQUE option is used more than once
            Arguments.DoublePrimalArgument
                Raised when PRIMAL option is used more than once in context
            Arguments.MemberTypeAlreadyUsed
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
                # Get option object associated with flag (argument)
                try:
                    option = flags[argument]
                    # If option is UNIQUE
                    if option.flag_type == Option.UNIQUE:
                        # If unique option already used
                        if option.name in unique_flags:
                            raise Arguments.DoubleUniqueArgument(argument) from None
                        # If not used, mark it as first used
                        unique_flags.add(option.name)
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
            # If all arguments processed
            except StopIteration:
                # Start a "close-all-left" cycle, where an invalid-name will
                # cause the context-search to close all left open options
                name = NotImplemented

            try:
                while True:
                    try:
                        # If context of option found (current context)
                        if name in context:
                            # Close current context and open a new option
                            raise Arguments._CloseCurrentOption(True)

                        # Check if context of option is a new sub-context
                        for sub_context in context.values():
                            # If context of option found
                            if name in sub_context:
                                # Open new context
                                contexts.append(sub_context)
                                # Jump one level down
                                context = sub_context
                                # Create new primal flag context
                                curr_primals = set()
                                primal_flags.append(curr_primals)
                                # Finished searching
                                raise Arguments._ContextFound

                        # If context of option is not found
                        # (in current context and in sub-context)
                        # Close current context and jump one level up
                        try:
                            contexts.pop()
                            context = contexts[-1]
                            curr_primals = primal_flags.pop()
                        except IndexError:
                            # If this is a regular cycle, not a "close-all-left"
                            if name is not NotImplemented:
                                raise Arguments.ArgumentOutOfContext(argument) from None

                        # Close current option and
                        # continue searching for context
                        raise Arguments._CloseCurrentOption(False)

                    # Close current option
                    except Arguments._CloseCurrentOption as message:
                        # If this is the nth argument
                        try:
                            # TODO: ** Meaningful error strings **
                            #       At some point add better feedback to object
                            #       hook when closing, to produce error like
                            #       this:
                            #
                            #           fullcmd --this --that abc xyz
                            #                   ~~~~~~        ^^^
                            #       UnfinishedOptionError: this, abc

                            # Create option-tuple
                            curr = (curr_values.name,
                                    curr_values.close(name),
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
                            raise Arguments._ContextFound

            # If a new option can be opened
            except Arguments._ContextFound:
                # If current context limits the number of use of its members
                try:
                    # If member has already been used
                    if len(curr_ones):
                        raise Arguments.MemberTypeAlreadyUsed(
                            curr_ones.pop(), argument) from None
                    # If this is the first time, this member appeared
                    curr_ones.add(argument)
                # If current context allows for its
                # member to appear more than once
                except TypeError:
                    pass

                # If option is PRIMAL
                if option.flag_type == Option.PRIMAL:
                    # If primal option already used in the current context
                    if name in curr_primals:
                        raise Arguments.DoublePrimalArgument(argument) from None
                    # If not used, mark it as used for the first time
                    curr_primals.add(name)

                # Open a new option
                curr_values  = option.object_hook(name)
                curr_members = []
                open_values.append(curr_values)
                open_members.append(curr_members)

                # If this context limits the number of appearences of its
                # members, use a collections, otherwise a None
                curr_ones = set() if option.member_type is Option.ONE else None
                open_ones.append(curr_ones)

            # If reached the top-level and the context still did not match
            except IndexError:
                # Return translated arguments
                return [(curr_values.name,
                         curr_values.close(name),
                         processed)]


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    @staticmethod
    def branch_traverse(options):
        """
        Returns:

            (<long_flag>, <value>)
        """
        for flag, value, members in options:
            yield flag, value
            yield from Arguments.branch_traverse(members)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    @staticmethod
    def branch_full_traverse(options, path=[]):
        """
        Returns:

            ([<group>..., <long_flag>], <value>)
        """
        for flag, value, members in options:
            path.append(flag)
            yield path, value
            yield from Arguments.branch_full_traverse(members, path)
            path.pop()


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    @staticmethod
    def breadth_first_traverse(options):
        """
        Traverse will walk through the translated arguments as a generator.
        Unlike the self.translate_args() method, it returns a yuple of four
        values:

            (<group>, <long_flag>, <value>, [<members>...])
        """
        options = [(None, options)]
        for group, gmembers in options:
            for flag, value, fmembers in gmembers:
                yield group, flag, value, fmembers
                options.append((flag, fmembers))


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def write_help(self, *blocks,
                         file     = stdout,
                         width    = None,
                         tab_size = 4,
                         no_color = False):
        # Write all blocks to file
        Text.Section(*blocks).write(indent   = 0,
                                    stream   = file,
                                    width    = width or get_terminal_size().columns,
                                    spaces   = abs(int(tab_size))*' ',
                                    no_color = no_color,
                                    owner    = None,
                                    options  = self._options)
