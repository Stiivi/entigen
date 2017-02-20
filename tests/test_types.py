import unittest

from entigen.types import Type

class TestTypes(unittest.TestCase):

    def test_basic(self) -> None:
        t = Type.from_string("string")
        self.assertEqual(t.name, "string")
        self.assertEqual(t.children, None)

    def test_composedl(self) -> None:
        t = Type.from_string("list<string>")
        self.assertEqual(t.name, "list")
        self.assertEqual(len(t.children), 1)

        child = t.first_child
        self.assertEqual(child.name, "string")
        self.assertEqual(child.children, None)
