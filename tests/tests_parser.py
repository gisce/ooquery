import unittest

from ooquery.parser import Parser
from ooquery.operators import OPERATORS_MAP


class ExpressionTests(unittest.TestCase):

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