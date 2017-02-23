import unittest
import textwrap

from entigen.block import Block

class TestBlock(unittest.TestCase):
    def test_basic(self) -> None:
        b = Block()

        b += "text"

        self.assertTrue(str(b), "test")

    def test_multiline(self) -> None:
        text = textwrap.dedent("""
        print(this)
        print(that)""").strip()

        b = Block()

        b += "print(this)"
        b += "print(that)"

        self.assertEqual(str(b), text)

    def test_nested(self) -> None:
        text = textwrap.dedent("""
        begin
        one
        two
        end""").strip()

        inner = Block()
        inner += "one"
        inner += "two"
        b = Block()

        b += "begin"
        b += inner
        b += "end"

        self.assertEqual(str(b), text)

    def test_indented(self) -> None:
        text = textwrap.dedent("""
        begin
          one
          two
        end""").strip()

        inner = Block(indent=2)
        inner += "one"
        inner += "two"
        b = Block()

        b += "begin"
        b += inner
        b += "end"

        self.assertEqual(str(b), text)

    def test_indented_nested(self) -> None:
        text = textwrap.dedent("""
        begin
          begin inner
            one
            two
          end inner
        end""").strip()

        cmds = Block(indent=2)
        cmds += "one"
        cmds += "two"

        inner = Block(indent=2)

        inner += "begin inner"
        inner += cmds
        inner += "end inner"

        b = Block()
        b += "begin"
        b += inner
        b += "end"

        self.assertEqual(str(b), text)

    def test_prefix(self) -> None:
        text = textwrap.dedent("""
        begin
          # one
          # two
        end""").strip()

        inner = Block(indent=2, prefix="# ")
        inner += "one"
        inner += "two"

        b = Block()

        b += "begin"
        b += inner
        b += "end"

        self.assertEqual(str(b), text)

    def test_prefix_nested(self) -> None:
        text = textwrap.dedent("""
        begin
          # one
          # two
        end""").strip()

        inner = Block()
        inner += "one"
        inner += "two"

        outer = Block(indent=2, prefix="# ")
        outer += inner

        b = Block()

        b += "begin"
        b += outer
        b += "end"

        self.assertEqual(str(b), text)

    def test_suffix(self) -> None:
        text = textwrap.dedent("""
        begin
          one,
          two,
        end""").strip()

        inner = Block(indent=2, suffix=",")
        inner += "one"
        inner += "two"

        b = Block()

        b += "begin"
        b += inner
        b += "end"

        self.assertEqual(str(b), text)


    def test_lastsuffix(self) -> None:
        text = textwrap.dedent("""
        if \\
            cond1 \\
            cond2 \\
            cond3:
          pass""").strip()

        inner = Block(indent=4, suffix=" \\", last_suffix=":")
        inner += "cond1"
        inner += "cond2"
        inner += "cond3"

        b = Block()

        b += "if \\"
        b += inner

        b += Block("pass", indent=2)

        self.assertEqual(str(b), text)


    def test_first_indent(self) -> None:
        text = textwrap.dedent("""
        if cond1 \\
            cond2 \\
            cond3:
          pass""").strip()

        inner = Block(indent=4, first_indent=0,
                      first_prefix="if ",
                      suffix=" \\", last_suffix=":")
        inner += "cond1"
        inner += "cond2"
        inner += "cond3"

        b = Block()

        b += inner
        b += Block("pass", indent=2)

        self.assertEqual(str(b), text)


