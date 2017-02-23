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


