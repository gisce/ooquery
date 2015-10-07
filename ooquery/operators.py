__all__ = ['Or', 'And', 'Not']


class Operator(object):
    def __init__(self, *args):
        self.args = []
        for arg in args:
            if isinstance(arg, self.__class__):
                self.args.extend(arg.args)
            elif isinstance(arg, Operator):
                self.args.append(arg.expression)
            else:
                self.args.append(arg)

    @property
    def operator(self):
        return ' {} '.format(self._operator)

    @property
    def expression(self):
        conditions = self.operator.join([str(x) for x in self.args])
        if len(self.args) > 1:
            conditions = '({0})'.format(conditions)
        return conditions


class Or(Operator):
    _operator = 'OR'
    n_pops = 2


class And(Operator):
    _operator = 'AND'
    n_pops = 2

class Not(Operator):
    _operator = 'NOT'
    n_pops = 1

OPERATORS_MAP = {
    '|': Or,
    '&': And
}
