import unittest

from ooquery.expression import Expression


class ExpressionTests(unittest.TestCase):

    def test_is_expression(self):
        self.assertTrue(Expression.is_expression(('a', '=', 'b')))
        self.assertFalse(Expression.is_expression('a'))
