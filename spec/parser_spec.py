# coding=utf-8
from sql import Table, Literal
from sql.operators import *
from ooquery.parser import Parser
from ooquery.expression import InvalidExpressionException

from expects import *


with description('A parser'):
    with before.all:
        self.t = Table('table')
        self.p = Parser(self.t)

    with it('parsing a query the original must be keeped'):
        domain = [('a', '=', Literal('b'))]
        domain_orig = domain[:]
        x = self.p.parse(domain)
        expect(domain).to(equal(domain_orig))

    with it("with a simple notation [('a', '=', 'b')]"):
        x = self.p.parse([('a', '=', Literal('b'))])
        op = And((Equal(self.t.a, 'b') ,))
        expect(x).to(equal(op))

    with it('must use And as default operator'):
        parsed = self.p.parse([('a', '=', Literal(1)), ('b', '=', Literal(2))])
        op = And((Equal(self.t.a, 1), Equal(self.t.b, 1)))
        expect(parsed).to(equal(op))

    with it('must support or of two operators'):
        parsed = self.p.parse(['|', ('a', '=', Literal(1)), ('b', '=', Literal(2))])
        op = And((Or([Equal(self.t.a, 1), Equal(self.t.b, 2)]),))
        expect(parsed).to(equal(op))

    with it('must support mixing and and or operators'):
        parsed = self.p.parse([
            ('x', '=', Literal(2)),
            '|', ('a', '=', Literal(1)), ('b', '=', Literal(2))])
        op = And((
            Equal(self.t.x, 2),
             Or((Equal(self.t.a, 1), Equal(self.t.b, 2)))
        ))
        expect(parsed).to(equal(op))

    with it('must support to multiple operators'):
        parsed = self.p.parse([
            '|',
            ('x', '=', Literal(2)),
            '|',
            ('a', '=', Literal(1)), ('b', '=', Literal(2))
        ])
        op = And((Or((
            Equal(self.t.x, 2), Or((Equal(self.t.a, 1), Equal(self.t.b, 2)))
        )),))
        expect(parsed).to(equal(op))

    with context('If has an invalid expression'):
        with it('must raise an exception'):
            def callback():
                p = Parser(Table('table'))
                p.parse([('a', '=', Literal('b')), ('c')])

            expect(callback).to(raise_error(InvalidExpressionException))

    with context('if an expression have joins'):
        with it('the parser must have the joins of all the expressions'):

            def dummy_fk(table, field):
                fks = {
                    'table_2': {
                        'constraint_name': 'fk_contraint_name',
                        'table_name': 'table',
                        'column_name': 'table_2',
                        'foreign_table_name': 'table2',
                        'foreign_column_name': 'id'
                    }
                }
                return fks[field]

            t = Table('table')
            p = Parser(t, dummy_fk)
            x = p.parse([('table_2.code', '=', Literal('XXX'))])
            expect(p.joins).to(have_len(1))
            expect(p.joins_map).to(have_len(1))

            join = t.join(Table('table2'))
            join.condition = join.left.table_2 == join.right.id

            expect(str(p.joins[0])).to(equal(str(join)))
            expect(p.joins_map).to(have_key('table_2'))
            expect(str(p.joins_map['table_2'])).to(equal(str(join)))

        with it('must have a function to get a join'):
            def dummy_fk(table, field):
                if table == 'table':
                    fks = {
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
                    fks = {
                        'table_3_id': {
                            'constraint_name': 'fk_contraint_name',
                            'table_name': 'table2',
                            'column_name': 'table_3_id',
                            'foreign_table_name': 'table3',
                            'foreign_column_name': 'id'
                        }
                    }
                return fks[field]


            t = Table('table')
            p = Parser(t, dummy_fk)
            p.parse([
                ('table_4_id.failed', '=', Literal(True)),
                ('table_2_id.table_3_id.code', '=', Literal('XXX')),
                ('table_2_id.state', '=', Literal('open')),
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
        with it('must allow for predefined joins'):
            def dummy_fk(table, field):
                fks = {
                    'table_2': {
                        'constraint_name': 'fk_contraint_name',
                        'table_name': 'table',
                        'column_name': 'table_2',
                        'foreign_table_name': 'table2',
                        'foreign_column_name': 'id'
                    },
                    'table_3': {
                        'constraint_name': 'fk_contraint_name',
                        'table_name': 'table',
                        'column_name': 'table_3',
                        'foreign_table_name': 'table3',
                        'foreign_column_name': 'id'
                    }
                }
                return fks[field]

            t = Table('table')
            t3 = Table('table3')
            p = Parser(t, dummy_fk)

            expect(p.joins).to(have_len(0))
            expect(p.joins_map).to(have_len(0))

            custom_join = t.join(t3)
            custom_join.condition = t.table_3 == custom_join.right.id
            p.joins_map['table_3'] = custom_join

            expect(p.joins).to(have_len(0))
            expect(p.joins_map).to(have_len(1))

            x = p.parse([('table_2.code', '=', Literal('XXX'))])

            expect(p.joins).to(have_len(1))
            expect(p.joins_map).to(have_len(2))

            join = t.join(Table('table2'))
            join.condition = join.left.table_2 == join.right.id

            expect(str(p.joins[0])).to(equal(str(join)))
            expect(p.joins_map).to(have_key('table_2'))
            expect(str(p.joins_map['table_2'])).to(equal(str(join)))
        with it('it must allow custom joins to be added to the search'):
            def dummy_fk(table, field):
                fks = {
                    'table_2': {
                        'constraint_name': 'fk_contraint_name',
                        'table_name': 'table',
                        'column_name': 'table_2',
                        'foreign_table_name': 'table2',
                        'foreign_column_name': 'id'
                    },
                    'table_3': {
                        'constraint_name': 'fk_contraint_name',
                        'table_name': 'table',
                        'column_name': 'table_3',
                        'foreign_table_name': 'table3',
                        'foreign_column_name': 'id'
                    }
                }
                return fks[field]

            t = Table('table')
            t3 = Table('table3')
            p = Parser(t, dummy_fk)

            custom_join = t.join(t3)
            custom_join.condition = t.table_3 == custom_join.right.id
            p.joins_map['table_3'] = custom_join

            x = p.parse(
                [('table_2.code', '=', Literal('XXX')), ('table_3.code', '=', Literal('YYY'))]
            )

            expect(p.joins).to(have_len(2))
            expect(p.joins_map).to(have_len(2))

            index = p.joins.index(custom_join)

            expect(str(p.joins[index])).to(equal(str(custom_join)))
            expect(p.joins[index]).to(equal(custom_join))
