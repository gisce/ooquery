import unittest

from ooquery.expression import Expression, InvalidExpressionException


class ExpressionTests(unittest.TestCase):

    def test_is_expression(self):
        self.assertTrue(Expression.is_expression(('a', '=', 'b')))
        self.assertFalse(Expression.is_expression('a'))

    def test_raise_invalid_excpetion(self):
        def raises():
            Expression(('a',))
        self.assertRaises(InvalidExpressionException, raises)
