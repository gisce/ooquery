# coding=utf-8
from sql import Table
from sql.operators import *
from ooquery.parser import Parser
from ooquery.expression import InvalidExpressionException

from expects import *


with description('A parser'):
    with before.all:
        self.t = Table('table')
        self.p = Parser(self.t)

    with it("with a simple notation [('a', '=', 'b')]"):
        x = self.p.parse([('a', '=', 'b')])
        op = And((Equal(self.t.a, 'b') ,))
        expect(x).to(equal(op))

    with it('must use And as default operator'):
        parsed = self.p.parse([('a', '=', 1), ('b', '=', 2)])
        op = And((Equal(self.t.a, 1), Equal(self.t.b, 1)))
        expect(parsed).to(equal(op))

    with it('must support or of two operators'):
        parsed = self.p.parse(['|', ('a', '=', 1), ('b', '=', 2)])
        op = And((Or([Equal(self.t.a, 1), Equal(self.t.b, 2)]),))
        expect(parsed).to(equal(op))

    with it('must support mixing and and or operators'):
        parsed = self.p.parse([
            ('x', '=', 2),
            '|', ('a', '=', 1), ('b', '=', 2)])
        op = And((
            Equal(self.t.x, 2),
             Or((Equal(self.t.a, 1), Equal(self.t.b, 2)))
        ))
        expect(parsed).to(equal(op))

    with it('must support to multiple operators'):
        parsed = self.p.parse([
            '|',
            ('x', '=', 2),
            '|',
            ('a', '=', 1), ('b', '=', 2)
        ])
        op = And((Or((
            Equal(self.t.x, 2), Or((Equal(self.t.a, 1), Equal(self.t.b, 2)))
        )),))
        expect(parsed).to(equal(op))

    with context('If has an invalid expression'):
        with it('must raise an exception'):
            def callback():
                p = Parser(Table('table'))
                p.parse([('a', '=', 'b'), ('c')])

            expect(callback).to(raise_error(InvalidExpressionException))

    with context('if an expression have joins'):
        with it('the parser must have the joins of all the expressions'):

            def dummy_fk(table):
                return {
                    'table_2': {
                        'constraint_name': 'fk_contraint_name',
                        'table_name': 'table',
                        'column_name': 'table_2',
                        'foreign_table_name': 'table2',
                        'foreign_column_name': 'id'
                    }
                }

            t = Table('table')
            p = Parser(t, dummy_fk)
            x = p.parse([('table_2.code', '=', 'XXX')])
            expect(p.joins).to(have_len(1))
            expect(p.joins_map).to(have_len(1))

            join = t.join(Table('table2'))
            join.condition = join.left.table_2 == join.right.id

            expect(str(p.joins[0])).to(equal(str(join)))
            expect(p.joins_map).to(have_key('table_2'))
            expect(str(p.joins_map['table_2'])).to(equal(str(join)))

