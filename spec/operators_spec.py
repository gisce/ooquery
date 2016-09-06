# coding=utf-8
from ooquery.operators import OPERATORS_MAP
from expects import *


with description('An operator'):
    with it('must have the number of pops to do'):
        pops_operator = {
            '|': 2,
            '&': 2,
            '!': 1
        }
        for op, n_pops in pops_operator.items():
            expect(OPERATORS_MAP[op].n_pops).to(equal(n_pops))
