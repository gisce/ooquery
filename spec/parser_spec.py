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

        with it('must have a function to get a jon'):
            def dummy_fk(table):
                if table == 'table':
                    return {
                        'table_2_id': {
                            'constraint_name': 'fk_contraint_name',
                            'table_name': 'table',
                            'column_name': 'table_2_id',
                            'foreign_table_name': 'table2',
                            'foreign_column_name': 'id'
                        },
                        'table_4_id': {
                            'constraint_name': 'fk_contraint_name',
                            'table_name': 'table',
                            'column_name': 'table_4_id',
                            'foreign_table_name': 'table4',
                            'foreign_column_name': 'id'
                        }
                    }
                elif table == 'table2':
                    return {
                        'table_3_id': {
                            'constraint_name': 'fk_contraint_name',
                            'table_name': 'table2',
                            'column_name': 'table_3_id',
                            'foreign_table_name': 'table3',
                            'foreign_column_name': 'id'
                        }
                    }


            t = Table('table')
            p = Parser(t, dummy_fk)
            p.parse([
                ('table_4_id.failed', '=', True),
                ('table_2_id.table_3_id.code', '=', 'XXX'),
                ('table_2_id.state', '=', 'open'),
            ])
            t = Table('table')
            t2 = Table('table2')
            t3 = Table('table3')
            t4 = Table('table4')
            join = t.join(t2)
            join.condition = t.table_2_id == join.right.id

            join2 = join.join(t3)
            join2.condition = t2.table_3_id == join2.right.id

            join3 = join2.join(t4)
            join3.condition = t.table_4_id == join3.right.id

            sel = join3.select(t.field1, t.field2)
            sel.where = And((
                join3.right.failed == True,
                join2.right.code == 'XXX',
                join.right.state == 'open'
            ))
