"""Text block"""

from typing import Union, cast, List, Optional, Iterable

BlockType = Union["Block", str]
BlockConvertible = Union[BlockType, List[BlockType]]

class Block:
    """Represents a block of code. See the `__init__` method documentation for
    more information about the block properties.
    
    Blocks are composed of list of lines or other blocks. Blocks can be
    indented or decorated by suffixes or prefixes. Example use:

    .. code-block::

        body = Block(indent=4)
        body += "do_this()"
        body += "do_that()"

        block = Block()
        block += "begin"
        block += body
        block += "end"

    Which renders as:

    .. code-block::

        begin
            do_this()
            do_that()
        end
    """

    children: List[BlockType]
    indent: int
    prefix: Optional[str]
    suffix: Optional[str]
    first_prefix: Optional[str]
    first_indent: Optional[int]
    last_suffix: Optional[str]
    
    def __init__(self, block: Optional[BlockConvertible]=None,
            indent: int=0,
            prefix: Optional[str]=None,
            suffix: Optional[str]=None,
            first_prefix: Optional[str]=None,
            first_indent: Optional[int]=None,
            last_suffix: Optional[str]=None) -> None:
        """Create a code block. Arguments:
        
        * `block` – content of the block, either another block or a string.
        * `indent` – number of spaces before each line of the block body
        * `prefix` – string prepended to every line of the block after adding
          indentation padding.
        * `suffix` – string appended to every line of the block
        * `first_prefix` – if specified, then prepended to the first line of
          the block instead of the common `prefix`
        * `first_indent` – if specified, then it is used for padding of the
          first line of the block instead of the common indent.
        * `last_suffix` – if specified, then appended to the last line of the
          block instead of the common `suffix`

        """

        self.indent = indent
        self.prefix = prefix
        self.suffix = suffix
        self.first_indent = first_indent
        self.first_prefix = first_prefix
        self.last_suffix = last_suffix

        if not block:
            self.children = []
        elif isinstance(block, (Block, str)):
            self.children = [block]
        elif isinstance(block, list):
            self.children = cast(List[BlockType], block)
        else:
            raise Exception("Invalid block type: {}".format(type(block)))

    def __iadd__(self, block:BlockType) -> "Block":
        if not isinstance(block, (Block, str)):
            raise Exception("Invalid block type: {}".format(type(block)))
        self.children.append(block)
        return self

    def lines(self) -> Iterable[str]:
        """Iterate over lines of the block"""

        common_padding = " " * self.indent
        if self.first_indent is None:
            first_padding = common_padding
        else:
            first_padding = " " * self.first_indent

        common_prefix = self.prefix or ""
        if self.first_prefix is None:
            first_prefix = common_prefix
        else:
            first_prefix = self.first_prefix

        common_suffix = self.suffix or ""
        if self.last_suffix is None:
            last_suffix = common_suffix
        else:
            last_suffix = self.last_suffix

        # We gather all the lines, since we need to know which one is the last
        # one
        lines: List[str] = []

        for child in self.children:
            if isinstance(child, str):
                lines.append(child)
            else:
                for line in child.lines():
                    lines.append(line)

        count = len(lines)

        # Print-out the lines
        for i, line in enumerate(lines):
            prefix = common_prefix
            padding = common_padding
            suffix = common_suffix

            if i == 0:
                prefix = first_prefix
                padding = first_padding
            elif i >= count - 1:
                suffix = last_suffix

            yield padding + prefix + line + suffix

    def to_string(self, indent:int=0) -> str:
        """Return block as string with indent `indent`"""


        lines = self.lines()

        if self.suffix:
            lines = [line + self.suffix for line in lines]
        return "\n".join(lines)

    def __str__(self) -> str:
        return self.to_string(indent=0)



    
