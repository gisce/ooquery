class Expression(object):
    def __init__(self, expression):
        if not self.is_expression(expression):
            raise InvalidExpressionException
        self.expression = expression

    @staticmethod
    def is_expression(expression):
        """Check if is a valid expression.
        """
        return isinstance(expression, (list, tuple)) and len(expression) == 3


class InvalidExpressionException(Exception):
    pass
