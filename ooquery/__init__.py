from ooquery.operators import *


def is_expression(expression):
    """Check if is a valid expression.
    """
    return isinstance(expression, (list, tuple)) and len(expression) == 3


class Parser(object):
    def __init__(self, operators):
        self.operators = operators

    def parse(self, query):
        result = []
        while query:
            expression = query.pop()
            if is_expression(expression):
                result.append(expression)
            else:
                op = self.operators[expression]
                q = []
                for _ in range(0, op.n_pops):
                    q1 = result.pop()
                    assert is_expression(q1)
                    q.append(q1)
                result.append(op(*q).expression)
        return And(*result).expression