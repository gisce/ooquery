import unittest

from ooquery.operators import *


class TestOperators(unittest.TestCase):
    def test_or(self):
        operation = Or(('a', '=', 'b'), ('a', '=', 'c'))
        self.assertEqual(
            operation.expression,
            "(('a', '=', 'b') OR ('a', '=', 'c'))"
        )

    def test_flattern(self):
        operation = Or(Or(('a', '=', 'b'), ('a', '=', 'c')), ('a', '=', 'd'))

        self.assertEqual(
            operation.args,
            [('a', '=', 'b'), ('a', '=', 'c'), ('a', '=', 'd')]
        )

        self.assertEqual(
            operation.expression,
            "(('a', '=', 'b') OR ('a', '=', 'c') OR ('a', '=', 'd'))"
        )

    def test_flattern_different_operators(self):
        operation = (
            And(
                And(
                    Or(('a', '=', 'b'), ('a', '=', 'c')),
                    ('z', '=', 'x')
                ),
                ('j', '=', 'i')
            )
        )
        self.assertEqual(
            operation.expression,
            "((('a', '=', 'b') OR ('a', '=', 'c')) AND ('z', '=', 'x') "
            "AND ('j', '=', 'i'))"
        )