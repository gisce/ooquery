# coding=utf-8
from ooquery import OOQuery
from ooquery.expression import Field
from sql import Table, Literal, NullsFirst, NullsLast
from sql.operators import And, Concat
from sql.aggregate import Max
from sql.conditionals import Coalesce, Greatest, Least

from expects import *
from mamba import *


with description('The OOQuery object'):
    with description('when creating an ooquery object'):
        with it('should get the table to query'):
            q = OOQuery('table')
            expect(q.table).to(be_a(Table))
        with it('should have a select method which returns table.attr'):
            q = OOQuery('table')
            sel = q.select(['field1', 'field2'])
            sel2 = q.table.select(q.table.field1.as_('field1'), q.table.field2.as_('field2'))
            expect(str(sel._select)).to(equal(str(sel2)))
        with it('should have a where method to pass the domain'):
            q = OOQuery('table')
            sql = q.select(['field1', 'field2']).where([('field3', '=', 4)])
            t = Table('table')
            sel = t.select(t.field1.as_('field1'), t.field2.as_('field2'))
            sel.where = And((t.field3 == 4,))
            expect(tuple(sql)).to(equal(tuple(sel)))

        with it('should have where mehtod and compare two fields of the table'):
            q = OOQuery('table')
            sql = q.select(['field1', 'field2']).where([('field3', '>', Field('field4'))])
            t = Table('table')
            sel = t.select(t.field1.as_('field1'), t.field2.as_('field2'))
            sel.where = And((t.field3 > t.field4,))
            expect(tuple(sql)).to(equal(tuple(sel)))

        with it('should have where and compare two fields of joined tables'):
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

            q = OOQuery('table', dummy_fk)
            sql = q.select(['field1', 'field2', 'table_2.name']).where([
                ('field1', '=', Field('table_2.name'))
            ])
            t = Table('table')
            t2 = Table('table2')
            join = t.join(t2)
            join.condition = join.left.table_2 == join.right.id
            sel = join.select(t.field1.as_('field1'), t.field2.as_('field2'), t2.name.as_('table_2.name'))
            sel.where = And((join.left.field1 == join.right.name,))
            expect(tuple(sql)).to(equal(tuple(sel)))


        with it('must support joins'):
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

            q = OOQuery('table', dummy_fk)
            sql = q.select(['field1', 'field2', 'table_2.name']).where([
                ('table_2.code', '=', 'XXX')
            ])
            t = Table('table')
            t2 = Table('table2')
            join = t.join(t2)
            join.condition = join.left.table_2 == join.right.id
            sel = join.select(t.field1.as_('field1'), t.field2.as_('field2'), t2.name.as_('table_2.name'))
            sel.where = And((join.right.code == 'XXX',))
            expect(tuple(sql)).to(equal(tuple(sel)))

            q = OOQuery('table', dummy_fk)
            sql = q.select(['field1', 'field2', 'table_2.name']).where([])
            t = Table('table')
            t2 = Table('table2')
            join = t.join(t2)
            join.condition = join.left.table_2 == join.right.id
            sel = join.select(t.field1.as_('field1'), t.field2.as_('field2'), t2.name.as_('table_2.name'))
            expect(tuple(sql)).to(equal(tuple(sel)))

        with it('must support deep joins'):
            def dummy_fk(table, field):
                if table == 'table':
                    fks = {
                        'table_2_id': {
                            'constraint_name': 'fk_contraint_name',
                            'table_name': 'table',
                            'column_name': 'table_2_id',
                            'foreign_table_name': 'table2',
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


            q = OOQuery('table', dummy_fk)
            sql = q.select(['field1', 'field2', 'table_2_id.table_3_id.name']).where([
                ('table_2_id.table_3_id.code', '=', 'XXX')
            ])
            t = Table('table')
            t2 = Table('table2')
            t3 = Table('table3')
            join = t.join(t2)
            join.condition = t.table_2_id == join.right.id
            join2 = join.join(t3)
            join2.condition = t2.table_3_id == join2.right.id
            sel = join2.select(t.field1.as_('field1'), t.field2.as_('field2'), t3.name.as_('table_2_id.table_3_id.name'))
            sel.where = And((join2.right.code == 'XXX',))
            expect(tuple(sql)).to(equal(tuple(sel)))
            expect(q.parser.joins_map).to(have_len(2))
            expect(str(q.parser.joins_map['table_2_id'])).to(equal(str(join)))
            expect(str(q.parser.joins_map['table_2_id.table_3_id'])).to(equal(str(join2)))

        with it('must support multiple deep joins'):
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


            q = OOQuery('table', dummy_fk)
            sql = q.select(['field1', 'field2']).where([
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

            sel = join3.select(t.field1.as_('field1'), t.field2.as_('field2'))
            sel.where = And((
                join3.right.failed == True,
                join2.right.code == 'XXX',
                join.right.state == 'open'
            ))
            expect(tuple(sql)).to(equal(tuple(sel)))

        with it('must support kwargs as python-sql select'):
            q = OOQuery('table', None)
            sql = q.select(['a', 'b'], limit=10).where([])

            t = Table('table')
            sel = t.select(t.a.as_('a'), t.b.as_('b'), limit=10)
            expect(tuple(sql)).to(equal(tuple(sel)))

        with it('must support order'):
            q = OOQuery('table', None)
            sql = q.select(['a', 'b'], order_by=('a.asc', 'b.desc')).where([])

            t = Table('table')
            sel = t.select(t.a.as_('a'), t.b.as_('b'), order_by=(t.a.asc, t.b.desc))
            expect(tuple(sql)).to(equal(tuple(sel)))

        with it('must support nulls first/nulls last options'):
            q = OOQuery('table', None)
            sql = q.select(['a', 'b'], order_by=('a.asc.nulls_first', 'b.desc.nulls_last')).where([])

            t = Table('table')
            sel = t.select(t.a.as_('a'), t.b.as_('b'), order_by=(NullsFirst(t.a.asc), NullsLast(t.b.desc)))
            expect(tuple(sql)).to(equal(tuple(sel)))

        with it('must support alias'):
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

            q = OOQuery('table', dummy_fk)
            sql = q.select(['field1', 'field2', 'table_2.name']).where([])
            t = Table('table')
            t2 = Table('table2')
            join = t.join(t2)
            join.condition = join.left.table_2 == join.right.id
            sel = join.select(t.field1.as_('field1'), t.field2.as_('field2'), t2.name.as_('table_2.name'))
            expect(tuple(sql)).to(equal(tuple(sel)))

        with it('must support recursive joins'):
            def dummy_fk(table, field):
                fks = {
                    'parent_id': {
                        'constraint_name': 'fk_contraint_name',
                        'table_name': 'table',
                        'column_name': 'parent_id',
                        'foreign_table_name': 'table',
                        'foreign_column_name': 'id'
                    }
                }
                return fks[field]

            q = OOQuery('table', dummy_fk)
            sql = q.select(['id']).where([
                ('parent_id.parent_id.code', '=', 34)
            ])
            t = Table('table')
            t2 = Table('table')
            t3 = Table('table')
            join = t.join(t2)
            join.condition = t.parent_id == join.right.id
            join2 = join.join(t3)
            join2.condition = t2.parent_id == join2.right.id
            sel = join2.select(t.id.as_('id'))
            sel.where = And((t3.code == 34,))
            expect(tuple(sql)).to(equal(tuple(sel)))

        with it('must support group by'):
            q = OOQuery('table')
            sel = q.select([Max('field1')], group_by=['field2'])
            sel2 = q.table.select(
                Max(q.table.field1).as_('max_field1'),
                group_by=[q.table.field2]
            )
            expect(str(sel._select)).to(equal(str(sel2)))

        with it('must support concat'):
            q = OOQuery('table')
            sel = q.select([Concat('field1', Literal(' 01:00'))])
            sel2 = q.table.select(Concat(q.table.field1, ' 01:00'))
            expect(str(sel._select)).to(equal(str(sel2)))

        with it('must support coalesce'):
            q = OOQuery('table')
            sel = q.select([Coalesce('field1', Literal(3))])
            sel2 = q.table.select(Coalesce(q.table.field1, 3))
            expect(str(sel._select)).to(equal(str(sel2)))

        with it('must support greatest'):
            q = OOQuery('table')
            sel = q.select([Greatest('field1', 'field2')])
            sel2 = q.table.select(Greatest(q.table.field1, q.table.field2))
            expect(str(sel._select)).to(equal(str(sel2)))

        with it('must support least'):
            q = OOQuery('table')
            sel = q.select([Least('field1', 'field2')])
            sel2 = q.table.select(Least(q.table.field1, q.table.field2))
            expect(str(sel._select)).to(equal(str(sel2)))

        with it('must support as'):
            q = OOQuery('table')
            sel = q.select(
                ['field1', 'field2'],
                as_={'field1': 'first column', 'field2': 'second column'}
            )

            table = q.table
            sel2 = table.select(
                table.field1.as_('first column'),
                table.field2.as_('second column')
            )
            expect(str(sel._select)).to(equal(str(sel2)))

        with it('must support as with Aggregate fields'):
            q = OOQuery('table')
            sel = q.select(
                [Max('field1')],
                as_={'max_field1': 'max first column'}
            )
            sel2 = q.table.select(Max(q.table.field1).as_('max first column'))
            expect(str(sel._select)).to(equal(str(sel2)))

        with it('must support group by in joined queries'):
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


            q = OOQuery('table', dummy_fk)
            sql = q.select([Max('field1')], group_by=['table_2_id.code']).where([
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

            sel = join3.select(
                Max(t.field1).as_('max_field1'),
                group_by=[t2.code]
            )
            sel.where = And((
                join3.right.failed == True,
                join2.right.code == 'XXX',
                join.right.state == 'open'
            ))
            expect(tuple(sql)).to(equal(tuple(sel)))

        with context('on every select'):
            with it('parser must be initialized'):
                def dummy_fk(table, field):
                    if table == 'table':
                        fks = {
                            'parent_id': {
                                'constraint_name': 'fk_contraint_name',
                                'table_name': 'table',
                                'column_name': 'parent_id',
                                'foreign_table_name': 'table',
                                'foreign_column_name': 'id'
                            },
                        }
                        return fks[field]


                q = OOQuery('table', dummy_fk)
                sql = q.select(['id', 'name']).where([
                    ('parent_id.ean13', '=', '3020178572427')
                ])
                parser = q.parser
                sql = q.select(['id', 'name']).where([
                    ('parent_id.ean13', '=', '3020178572427')
                ])
                expect(q.parser).to(not_(equal(parser)))
