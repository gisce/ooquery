from ooquery.operators import *
from ooquery.expression import Expression


class Parser(object):
    def __init__(self, operators):
        self.operators = operators

    def parse(self, query):
        result = []
        while query:
            expression = query.pop()
            if Expression.is_expression(expression):
                result.append(expression)
            else:
                op = self.operators[expression]
                q = []
                for _ in range(0, op.n_pops):
                    q1 = result.pop()
                    Expression(q1)
                    q.append(q1)
                result.append(op(*q).expression)
        return And(*result).expression