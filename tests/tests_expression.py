import unittest

from ooquery import is_expression, Parser
from ooquery.operators import *



class ExpressionTests(unittest.TestCase):

    def test_is_expression(self):
        self.assertTrue(is_expression(('a', '=', 'b')))
        self.assertFalse(is_expression('a'))

    def test_parse_polish_notation(self):
        expression = [
            '|',
                ('table.a', '=', '1'),
                ('table.a', '=', '2')
        ]
        parser = Parser(OPERATORS_MAP)
        self.assertEqual(
            parser.parse(expression),
            "(('table.a', '=', '1') OR ('table.a', '=', '2'))"
        )
        self.assertEqual(
            parser.parse([('a', '=', 'b')]),
            "('a', '=', 'b')"
        )
        self.assertEqual(
            parser.parse([('a', '=', 'b'), ('c', '=', 'd')]),
            "(('c', '=', 'd') AND ('a', '=', 'b'))"
        )


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