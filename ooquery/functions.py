# -*- coding: utf-8 -*-
from sql.functions import Function

class Unaccent(Function):
    __slots__ = ()
    _function = 'UNACCENT'