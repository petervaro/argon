## INFO ##
## INFO ##

# Import python modules
from textwrap import fill
from os       import isatty

# Import argon modules
import argon



#------------------------------------------------------------------------------#
class Block:
    """Base class of all text related objects in argon"""

    INDENT = 0

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    @property
    def owner(self):
        return self._owner
    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    @owner.setter
    def owner(self, owner):
        self._owner = owner


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, *blocks,
                       indent = None):
        self._blocks = blocks
        self._indent = self.INDENT if indent is None else indent


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def write(self, indent,
                    stream,
                    width,
                    spaces,
                    ending   = '\n',
                    owner    = None,
                    patterns = {},
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



#------------------------------------------------------------------------------#
class Section(Block):

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def write(self, *args, **kwargs):
        # If Section has an owner, use it instead
        if kwargs['owner'] is None:
            try:
                kwargs['owner'] = self._owner
            except AttributeError:
                pass

        # Increase indentation
        kwargs['indent'] += self._indent

        for block in self._blocks:
            # If block is a string reference to a Pattern
            if isinstance(block, str):
                try:
                    block = kwargs['patterns'][block].description
                except KeyError:
                    raise ValueError('Pattern not in Scheme: '
                                     '{!r}'.format(block)) from None

            # If block is a Pattern object
            elif isinstance(block, argon.pattern.Pattern):
                block = block.description

            # If block is something unexpected
            if not isinstance(block, Block):
                raise ValueError('Section expected Pattern or name of '
                                 'Pattern (as str) or any Block object, '
                                 'got {.__class__.__qualname__!r}'.format(block))
            # Write block
            block.write(*args, **kwargs)



#------------------------------------------------------------------------------#
class Header(Block):

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def write(self, *args, **kwargs):
        super().write(*args, strong=True, **kwargs)



#------------------------------------------------------------------------------#
class Paragraph(Block):

    INDENT = 1

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def write(self, *args, **kwargs):
        super().write(*args, ending='\n\n', **kwargs)



#------------------------------------------------------------------------------#
class Span(Block):

    INDENT = 1



#------------------------------------------------------------------------------#
class Flags(Block):

    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def __init__(self, *args,
                       new_line=False,
                       **kwargs):
        self._new_line = new_line
        super().__init__(*args, **kwargs)


    #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - #
    def write(self, *args, **kwargs):
        values = ' '.join(self._blocks)
        text   = []
        blocks = self._blocks

        # Construct flags
        try:
            for flag in reversed(sorted(kwargs['owner'].flags)):
                text.append(flag + ((' ' + values) if values else ''))
        except AttributeError:
            raise ValueError('Flags should be used inside a Section, which '
                             'should be passed to a Pattern, before the '
                             'writing is happening') from None
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
