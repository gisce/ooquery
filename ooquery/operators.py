# coding=utf-8
from __future__ import absolute_import

from sql import operators


class OOOperator(object):
    __slots__ = ()


class Or(OOOperator, operators.Or):
    n_pops = 2


class And(OOOperator, operators.And):
    _operator = 'AND'
    n_pops = 2


class Not(OOOperator, operators.Not):
    _operator = 'NOT'
    n_pops = 1


OPERATORS_MAP = {
    '|': Or,
    '&': And,
    '!': Not
}


class JoinType(object):
    type_ = None
    __slots__ = ('field', )

    def __init__(self, field):
        self.field = field

    def __repr__(self):
        return '{}({})'.format(self.type_, self.field)

    def __str__(self):
        return self.field

    def replace(self, *args):
        return self.field.replace(*args)


class InnerJoin(JoinType):
    type_ = 'INNER'


class LeftJoin(JoinType):
    type_ = 'LEFT'


class LeftOuterJoin(JoinType):
    type_ = 'LEFT OUTER'


class RightJoin(JoinType):
    type_ = 'RIGHT'


class RightOuterJoin(JoinType):
    type_ = 'RIGHT OUTER'


class FullJoin(JoinType):
    type_ = 'FULL'


class FullOuterJoin(JoinType):
    type_ = 'FULL OUTER'


class CrossJoin(JoinType):
    type_ = 'CROSS'
