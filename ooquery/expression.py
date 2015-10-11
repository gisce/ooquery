class Join(object):
    def __init__(self, table, field):
        self.table = table
        self.join_field = field

    def get_table(self):
        return '{0}_table'.format(self.join_field)

    @property
    def expression(self):
        return (self.get_table(), (
            '{0}.{1}'.format(self.table, self.join_field),
            '{0}.id'.format(self.get_table())
        ))


class Expression(object):
    def __init__(self, expression):
        if not self.is_expression(expression):
            raise InvalidExpressionException
        self.expression = expression
        self.joins = []
        self.conditions = []
        joins = self.expression[0].split('.')
        if len(joins) > 1:
            table = 'main_table'
            for idx, join in enumerate(joins):
                j = Join(table, join)
                if idx == len(joins) - 1:
                    self.conditions.append(
                        ('{0}.{1}'.format(
                            table, join),
                         self.expression[1], self.expression[2]
                        )
                    )
                else:
                    self.joins.append(j.expression)
                    table = j.get_table()

    @staticmethod
    def is_expression(expression):
        """Check if is a valid expression.
        """
        return isinstance(expression, (list, tuple)) and len(expression) == 3


class InvalidExpressionException(Exception):
    pass
