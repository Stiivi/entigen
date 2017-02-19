"""Text block"""

from typing import Union, cast, List, Optional, Iterable

BlockType = Union["Block", str]
BlockConvertible = Union["Block", str, List[str]]

class Block:
    children: List[BlockType]
    first: Optional[int]
    indent: int
    
    def __init__(self, block: Optional[BlockConvertible]=None,
            indent: int=0,
            first: Optional[int]=None,
            suffix: Optional[str]=None) -> None:

        self.indent = indent
        self.first = first
        self.suffix = suffix

        if not block:
            self.children = []
        elif isinstance(block, Block):
            self.children = block.children
        elif isinstance(block, str):
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

    def lines(self, indent:int=0) -> Iterable[str]:
        """Iterate over lines of the block"""

        offset = self.indent + indent
        padding = " " * offset
        suffix = self.suffix or ""

        for child in self.children:
            if isinstance(child, str):
                yield padding + child + suffix
            else:
                for line in child.lines(indent=offset):
                    yield line

    def to_string(self, indent:int=0) -> str:
        """Return block as string with indent `indent`"""


        lines = self.lines(indent=indent)

        if self.suffix:
            lines = [line + self.suffix for line in lines]
        return "\n".join(lines)

    def __str__(self) -> str:
        return self.to_string(indent=0)



    
