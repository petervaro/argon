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
            This argument restricts how many members are allowed in the context
            of this Pattern at one time.

            ONE:
                Only one member allowed at the context of this Pattern.

                    Eg. cmd --this --that

                This is not valud, since `cmd`'s member_type is ONE, and both
                `this` and `that` are members of `cmd`, therefore only one of
                them allowed to be used at a time.

            ANY (default):
                Any members allowed at any context of any Patterns.

        member_necessity:
            This argument restricts the usage of the members of this pattern.

            OPTIONAL (default):
                This pattern can be followed by its members, another pattern or
                nothing.

            REQUIRED:
                This pattern must be followed by at least one of its patterns.


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

        value_immediate:
            Can be True or False (default). Indicates wether a flag can be
            followed by a value without any spaces, for example: --flag12, where
            flag is '--flag' and the value is '12'. This option will be
            overwritten, if the same option is set in the Scheme object.

        value_delimiter:
            Specifies a string (with no spaces) which is allowed to be between a
            flag and a value. For example: --flag=12, where flag is '--flag',
            the delimiter is '=', and the value is '12'. This option will be
            overwritten, if the same option is set in the Scheme object.

        flag_validator:
            This argument specifies the callback function which will validate
            the flags of this Pattern. The default validator function will
            assume, that the following characters are valid for a flag:

                abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-

        double_dash:
            This argument specifies wether the rest of the arguments following
            the 'double_dash' value, should be stored in an array and should be
            set as the value of the current pattern. The argument has to be a
            non-empty string and the value_type of the pattern should be either
            COMMON_ARRAY or UNIQUE_ARRAY. If the value of 'double_dash' is a
            valid flag in the current context, the behaviour is undefined.
            The conventional value is '--'.

        description:
            Takes a string or a argon.text.Section which will describe the
            behavior of this Pattern to the user. (This will be used by the
            argon.scheme.Scheme.write_help method.)
    """

    __FLAG_TYPE   = tuple(range(3))
    __MEMBER_TYPE = tuple(range(2))
    __NECESSITY   = tuple(range(2))

    # 'flag_type-enums'
    (COMMON,
     PRIMAL,
     UNIQUE) = __FLAG_TYPE

    # 'member_type-enums'
    (ONE,
     ANY) = __MEMBER_TYPE

    # 'value_necessity-enums'
    (OPTIONAL,
     REQUIRED) = __NECESSITY


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    class PatternException(Exception)         : pass
    class InvalidFlagName(PatternException)   : pass
    class FinishedPattern(PatternException)   : pass
    class UnfinishedPattern(PatternException) : pass


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    class EOL:
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
                        Pattern.EOL() if name is NotImplemented else flag) from None
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
                        Pattern.COMMON_ARRAY, self._flag,
                        Pattern.EOL() if name is NotImplemented else flag) from None
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
                        Pattern.UNIQUE_ARRAY, self._flag,
                        Pattern.EOL() if name is NotImplemented else flag) from None
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
                        Pattern.NAMED_VALUES, self._flag,
                        Pattern.EOL() if name is NotImplemented else flag) from None
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
    def long_flag(self):
        return self._long_flag


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    @property
    def flags(self):
        yield from chain((self._long_flag,), self._short_flags)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    @property
    def members(self):
        yield from self._members


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    @property
    def member_necessity(self):
        return self._member_necessity


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
    def value_immediate(self):
        return self._value_immediate
    @value_immediate.setter
    def value_immediate(self, value):
        self._value_immediate = value


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    @property
    def value_delimiter(self):
        return self._value_delimiter
    @value_delimiter.setter
    def value_delimiter(self, value):
        self._value_delimiter = value


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    @property
    def object_hook(self):
        return self._object_hook


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    @property
    def double_dash(self):
        return self._double_dash


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    @property
    def description(self):
        return self._description


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, long_flag,
                       short_flags      = (),
                       long_prefix      = '--',
                       short_prefix     = '-',
                       flag_type        = COMMON,
                       members          = (),
                       member_type      = ANY,
                       member_necessity = OPTIONAL,
                       value_delimiter      = '',
                       value_immediate       = False,
                       value_type       = SINGLE_VALUE,
                       value_necessity  = REQUIRED,
                       flag_validator   = FLAG_VALIDATOR.__func__,
                       double_dash      = '',
                       description      = ''):
        # Check for flag's validity
        short_flags = set(short_flags)
        for flag in chain((long_flag,), short_flags):
            if not isinstance(flag, str):
                raise Pattern.InvalidFlagName(
                    "Type of a flag name should be 'str', not: "
                    "{0.__class__.__qualname__!r} ".format(flag))
            # If the user accidentally added the `-` or `--` prefixes
            # TODO: check for `/` windows prefix as well
            if flag.startswith('-'):
                raise Pattern.InvalidFlagName("Flag name cannot start with '-'")
            # Check every character if it is inappropriate
            flag_validator(flag)

        # Store flags
        self._name        = long_flag
        self._long_flag   = long_prefix + long_flag
        self._short_flags = {short_prefix + f for f in short_flags}

        # Check and store flag_type
        if flag_type not in Pattern.__FLAG_TYPE:
            # If passed value is not a class
            if not isinstance(flag_type, type):
                flag_type = flag_type.__class__
            raise ValueError("'flag_type' has to be Pattern.COMMON "
                             "or Pattern.PRIMAL or Pattern.UNIQUE, "
                             "not: {.__qualname__!r}".format(flag_type))
        self._flag_type = flag_type

        # Check and store value_type
        if value_type not in Pattern.__VALUE_TYPE:
            # If passed value is not a class
            if not isinstance(value_type, type):
                value_type = value_type.__class__
            raise ValueError("'value_type' has to be Pattern.STATE_SWITCH "
                             "or Pattern.SINGLE_VALUE or Pattern.COMMON_ARRAY "
                             "or Pattern.UNIQUE_ARRAY or Pattern.NAMED_VALUES, "
                             "not: {!r}".format(value_type))
        self._object_hook = value_type

        # Check and store value_necessity
        if value_necessity not in Pattern.__NECESSITY:
            # If passed value is not a class
            if not isinstance(value_necessity, type):
                value_necessity = value_necessity.__class__
            raise ValueError("'value_necessity' has to be Pattern.OPTIONAL or "
                             "Pattern.REQUIRED, not: {!r}".format(value_necessity))
        self._value_necessity = value_necessity
        if value_necessity:
            necessity = lambda s: s
        else:
            necessity = lambda s: '[' + s + ']'

        # Check and store member_type
        if member_type not in Pattern.__MEMBER_TYPE:
            # If passed value is not a class
            if not isinstance(member_type, type):
                member_type = member_type.__class__
            raise ValueError("'member_type' has to be Pattern.ONE or "
                             "Pattern.ANY, not: {!r}".format(member_type))
        self._member_type = member_type

        # Check and store member_necessity
        if member_necessity not in Pattern.__NECESSITY:
            # If passed value is not a class
            if not isinstance(member_necessity, type):
                member_necessity = member_necessity.__class__
            raise ValueError("'member_necessity' has to be Pattern.OPTIONAL or "
                             "Pattern.REQUIRED, not: {!r}".format(member_necessity))
        self._member_necessity = member_necessity

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
                            "got: {.__class__.__qualname__!r}".format(description))
        description.owner = self
        self._description = description

        # Check and store double-dash value
        if (double_dash and
            value_type not in (Pattern.COMMON_ARRAY, Pattern.UNIQUE_ARRAY)):
                raise ValueError("'double_dash' defined, but the 'value_type' of "
                                 "the pattern is not 'Pattern.COMMON_ARRAY', nor "
                                 "'Pattern.UNIQUE_ARRAY'")
        self._double_dash = double_dash

        # Check and store
        if (value_delimiter and
            value_delimiter == ' '):
                raise ValueError("'value_delimiter' cannot be ' ' (space)")
        self._value_delimiter = value_delimiter

        # Store static values
        self._value_immediate = value_immediate
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
