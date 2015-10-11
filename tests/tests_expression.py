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

    def test_joins(self):
        expression = ('invoice_id.journal_id.code', '=', 'BANK')
        exp = Expression(expression)
        self.assertEqual(
            exp.joins,
            [
                ('invoice_id_table', ('main_table.invoice_id', 'invoice_id_table.id')),
                ('journal_id_table', ('invoice_id_table.journal_id', 'journal_id_table.id'))
            ]
        )
        self.assertEqual(
            exp.conditions,
            [('journal_id_table.code', '=', 'BANK')]
        )
