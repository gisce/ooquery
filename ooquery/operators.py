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
