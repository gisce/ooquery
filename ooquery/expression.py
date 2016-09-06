# coding=utf-8
from sql.operators import *

OPERATORS = {
    '=': Equal,
    '!=': NotEqual,
    '<>': NotEqual,
    '<=': LessEqual,
    '<': Less,
    '>': Greater,
    '>=': GreaterEqual,
    '=like': Like,
    'like': Like,
    'not like': NotLike,
    'ilike': ILike,
    'not ilike': NotILike,
    'in': In,
    'not in': NotIn,
}


class Expression(object):
    def __init__(self, expression):
        if not self.is_expression(expression):
            raise InvalidExpressionException
        self.left, self.operator, self.rigth = expression
        try:
            self.operator = OPERATORS[self.operator]
        except KeyError:
            raise ValueError('Operator {} is not supported'.format(
                self.operator
            ))

    @property
    def expression(self):
        return self.operator(self.left, self.rigth)

    @staticmethod
    def is_expression(expression):
        """Check if is a valid expression.
        """
        return isinstance(expression, (list, tuple)) and len(expression) == 3


class InvalidExpressionException(Exception):
    pass
