## INFO ##
## INFO ##

# Import python modules
from itertools   import chain
from collections import OrderedDict
from string      import ascii_letters, digits

# Import orderedset modules
from orderedset  import OrderedSet

# Import argon modules
from argon.text  import Section, Header, Paragraph, Flags



#------------------------------------------------------------------------------#
class Pattern:
    """
    Create a new Pattern instance.

    ARGUMENTS:

        long_flag:
            This will be the name of the Pattern. When some input is parsed,
            this value will be returned associated with the passed flag and
            value. It will also be used as the `--long_flag` option. It has to
            be unique Scheme wide.

        short_flags:
            By default, a Pattern does not have any short_flags. This argument
            takes an iterable, and each item in it will be a shortflag. If a
            scheme has more than one shortflags which are the same, the
            association will be undefined.

        long_prefix:
            By default it will be `--`.

        short_prefix:
            By default it will be `-`.

        flag_type:
            This will restrict the number of usages of a flag in a command.

            COMMON (default):
                Flag can appear more than one times anywhere in the command
                sequence. Therefore the following example is perfectly valid:

                    cmd --this w --context1 --this x --this y
                                 --context2 --this z

            PRIMAL:
                Flag can appear only once in every context (top-level, context,
                sub-context). Therefore the following example is perfectly
                valid:

                    cmd --this x --context1 --this y
                                 --context2 --this z

                However the next examples are not:

                    cmd --this x --this y
                    cmd --this x --context --this y --this z

            UNIQUE:
                Flag can appear only once anywhere. Therefore the following
                example is perfectly valid:

                    cmd --this x

                However the next examples are not:

                    cmd --this x --group --this y
                    cmd --group --this x --this y
                    cmd --group1 --this x --group2 --this y

        members:
            A flag can have members, which means the flag becomes a `context`.
            The argument takes string (as references to other Patterns) or
            Pattern instances.

        member_type:
            This argument restrict how many members are allowed in the context
            of this Pattern at one time.

            ONE:
                Only one member allowed at the context of this Pattern

            ANY (default):
                Any members allowed at any context of any Patterns


        value_type:
            This argument will specify what kind of values a Pattern takes.

            STATE_SWITCH:
                The flags of this Pattern does not take any values. If they are
                present in the command, their value will be True.

                    Eg. cmd --this
                        cmd --this --that

                Which can roughly be translated to:

                    {this: True}
                    {this: True, that: True}

            SINGLE_VALUE (default):
                The flags of this Pattern takes a single value only.

                    Eg. cmd --this hello --that

                Which can roughly be translated to:

                    {'this': 'hello', 'that': True}

            COMMON_ARRAY:
                The flags of this Pattern takes one or more values, which values
                will be returned as is.

                    Eg. cmd --this a b c a b c d --that

                Which can roughly be translated to:

                    {'this': ['a', 'b', 'c', 'a', 'b', 'c', 'd'], 'that': True}

            UNIQUE_ARRAY:
                The flags of this Pattern takes one or more values, which values
                will be returned filtered (duplicates removed).

                    Eg. cmd --this a b c a b c d --that

                Which can roughly be translated to:

                    {'this': ['a', 'b', 'c', 'd'], 'that': True}

            NAMED_VALUES:
                The flags of this Pattern takes one or more key-value pairs.

                    Eg. cmd --this hello 0 world 1 --that

                Which can roughly be translated to:

                    {'this': {'hello': '0', 'world': '1'}, 'that': True}

        value_necessity:

            OPTIONAL:
                Defining value(s) for the flags of this Pattern is optional.

                    Eg. cmd --this --that

                Which can roughly be translated to:

                    {'this': None, 'that': []}

            REQUIRED (default):
                Defining value(s) for the flags of this Pattern is mandatory.

                    Eg. cmd --this hello --that 1 2 3

                Which can roughly be translated to:

                    {'this': 'hello', 'that': ['1', '2', '3']}


        flag_validator:
            This argument specifies the callback function which will validate
            the flags of this Pattern. The default validator function will
            assume, that the following characters are valid for a flag:

                abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-

        description:
            Takes a string or a argon.text.Section which will describe the
            behavior of this Pattern to the user. (This will be used by the
            argon.scheme.Scheme.write_help method.)
    """

    __FLAG_TYPE       = tuple(range(3))
    __MEMBER_TYPE     = tuple(range(2))
    __VALUE_NECESSITY = tuple(range(2))

    # 'flag_type-enums'
    (COMMON,
     PRIMAL,
     UNIQUE) = __FLAG_TYPE

    # 'member_type-enums'
    (ONE,
     ANY) = __MEMBER_TYPE

    # 'value_necessity-enums'
    (OPTIONAL,
     REQUIRED) = __VALUE_NECESSITY


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    class PatternException(Exception)         : pass
    class InvalidFlagName(PatternException)   : pass
    class FinishedPattern(PatternException)   : pass
    class UnfinishedPattern(PatternException) : pass


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    class _EOL:
        def __repr__(self):
            return '<EOL>'


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    class _ObjectHook:

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
        @property
        def name(self):
            return self._name

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
        @property
        def flag(self):
            return self._flag

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
        def close(self, name, flag):
            return self._values


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    class STATE_SWITCH(_ObjectHook):


        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
        def __init__(self, name, flag, is_required):
            self._name   = name
            self._flag   = flag
            self._values = True

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
        def add_value(self, value):
            raise Pattern.FinishedPattern(
                Pattern.STATE_SWITCH, self._flag, value) from None


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    class SINGLE_VALUE(_ObjectHook):

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
        def __init__(self, name, flag, is_required):
            self._name        = name
            self._flag        = flag
            self._values      = None
            self._is_required = is_required

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
        def add_value(self, value):
            if self._values is not None:
                raise Pattern.FinishedPattern(
                    Pattern.SINGLE_VALUE, self._flag, value) from None
            self._values = value

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
        def close(self, name, flag):
            if (self._is_required and
                self._values is None):
                    raise Pattern.UnfinishedPattern(
                        Pattern.SINGLE_VALUE, self._flag,
                        Pattern._EOL() if name is NotImplemented else flag) from None
            return self._values


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    class COMMON_ARRAY(_ObjectHook):

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
        def __init__(self, name, flag, is_required):
            self._name        = name
            self._flag        = flag
            self._values      = []
            self._is_required = is_required

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
        def add_value(self, value):
            self._values.append(value)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
        def close(self, name, flag):
            if (self._is_required and
                not self._values):
                    raise Pattern.UnfinishedPattern(
                        Pattern.SINGLE_VALUE, self._flag,
                        Pattern._EOL() if name is NotImplemented else flag) from None
            return self._values


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    class UNIQUE_ARRAY(_ObjectHook):

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
        def __init__(self, name, flag, is_required):
            self._name        = name
            self._flag        = flag
            self._values      = OrderedSet()
            self._is_required = is_required

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
        def add_value(self, value):
            self._values.add(value)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
        def close(self, name, flag):
            if (self._is_required and
                not self._values):
                    raise Pattern.UnfinishedPattern(
                        Pattern.SINGLE_VALUE, self._flag,
                        Pattern._EOL() if name is NotImplemented else flag) from None
            return self._values


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    class NAMED_VALUES(_ObjectHook):

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
        def __init__(self, name, flag, is_required):
            self._name        = name
            self._flag        = flag
            self._key         = NotImplemented
            self._values      = OrderedDict()
            self._is_required = is_required

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
        def add_value(self, value):
            if self._key is NotImplemented:
                self._key = value
            else:
                self._values[self._key] = value
                self._key = NotImplemented

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
        def close(self, name, flag):
            if (self._key is not NotImplemented or
                (self._is_required and
                 not self._values)):
                    raise Pattern.UnfinishedPattern(
                        Pattern.SINGLE_VALUE, self._flag,
                        Pattern._EOL() if name is NotImplemented else flag) from None
            return self._values


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    @staticmethod
    def FLAG_VALIDATOR(string, valid_chars=set(ascii_letters + digits + '_-')):
        if set(string) - valid_chars:
            raise Pattern.InvalidFlagName(
                'Flag name {!r} containes an '
                'invalid character: {!r}'.format(string, char)) from None


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
    def value_necessity(self):
        return self._value_necessity


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
                       short_flags     = (),
                       long_prefix     = '--',
                       short_prefix    = '-',
                       flag_type       = COMMON,
                       members         = (),
                       member_type     = ANY,
                       value_type      = SINGLE_VALUE,
                       value_necessity = REQUIRED,
                       flag_validator  = FLAG_VALIDATOR.__func__,
                       description     = ''):
        # Check for flag's validity
        short_flags = set(short_flags)
        for flag in chain((long_flag,), short_flags):
            if not isinstance(flag, str):
                raise Pattern.InvalidFlagName(
                    "Type of a flag name should be 'str', not "
                    "{0.__class__.__qualname__!r} ".format(flag))
            # If the user accidentally added the `-` or `--` prefixes
            # TODO: check for `/` windows prefix as well
            if flag.startswith('-'):
                raise Pattern.InvalidFlagName("Flag name cannot start with '-'")
            # Check every character if it is inappropriate
            flag_validator(flag)

        # Store flags
        self._name  = long_flag
        self._flags = {f for f in chain((long_prefix + long_flag,),
                                        (short_prefix + s for s in short_flags))}

        # Check and store flag_type
        if flag_type not in Pattern.__FLAG_TYPE:
            raise ValueError("'flag_type' has to be Pattern.COMMON "
                             "or Pattern.PRIMAL or Pattern.UNIQUE, "
                             "not {!r}".format(flag_type))
        self._flag_type = flag_type

        # Check and store value_type
        if value_type not in Pattern.__VALUE_TYPE:
            raise ValueError("'value_type' has to be Pattern.STATE_SWITCH "
                             "or Pattern.SINGLE_VALUE or Pattern.COMMON_ARRAY "
                             "or Pattern.UNIQUE_ARRAY or Pattern.NAMED_VALUES, "
                             "not {!r}".format(value_type))
        self._object_hook = value_type

        # Check and store value_necessity
        if value_necessity not in Pattern.__VALUE_NECESSITY:
            raise ValueError("'value_necessity' has to be Pattern.OPTIONAL or "
                             "Pattern.REQUIRED, not {!r}".format(value_necessity))
        self._value_necessity = value_necessity
        if value_necessity:
            necessity = lambda s: s
        else:
            necessity = lambda s: '[' + s + ']'

        # Check and store member_type
        if member_type not in Pattern.__MEMBER_TYPE:
            raise ValueError("'member_type' has to be Pattern.ONE or "
                             "Pattern.ANY, not {!r}".format(member_type))
        self._member_type = member_type

        # Check and store description
        if isinstance(description, str):
            description = Section(
                Flags({Pattern.STATE_SWITCH: '',
                       Pattern.SINGLE_VALUE: necessity('<value>'),
                       Pattern.COMMON_ARRAY: necessity('<value>...'),
                       Pattern.UNIQUE_ARRAY: necessity('<value>...'),
                       Pattern.NAMED_VALUES: necessity('<key> <value>...')}[value_type]),
                Paragraph(description))
        elif not isinstance(description, Section):
            raise TypeError("'description' expected str or argon.text.Section, "
                            "got {.__class__.__qualname__!r}".format(description))
        description.owner = self
        self._description = description

        # Store static values
        if isinstance(members, str):
            self._members = {members}
        else:
            self._members = set(members)



#------------------------------------------------------------------------------#
class Program(Pattern):
    """Convenient wrapper class around Pattern"""

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    @staticmethod
    def ACCEPT_ANYTHING(string):
        pass


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, long_flag, *args, **kwargs):
        # Check if command has members
        if not kwargs.get('members', None):
            raise ValueError("Missing or empty 'members' for Program")
        # If otherwise not specified set command as a switch
        kwargs.setdefault('value_type', Pattern.STATE_SWITCH)
        # If otherwise not specified set flag_validator to accept file names
        kwargs.setdefault('flag_validator', Program.ACCEPT_ANYTHING)

        # Create basic documentation
        description = kwargs.get('description', '')
        if isinstance(description, str):
            kwargs['description'] = Section(
                Header('NAME'),
                Paragraph(long_flag +
                               ((' - ' + description) if description else '')))

        # Set default values if they are not already defined by the user
        kwargs.setdefault('long_prefix', '')
        kwargs.setdefault('flag_type', Pattern.UNIQUE)

        # Initialize Pattern
        super().__init__(long_flag, *args, **kwargs)