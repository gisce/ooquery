# coding=utf-8
from ooquery import OOQuery
from sql import Table
from sql.operators import *

from expects import *


with description('The OOQuery object'):
    with description('when creating an ooquery object'):
        with it('should get the table to query'):
            q = OOQuery('table')
            expect(q.table).to(be_a(Table))
        with it('should have a select method which returns table.attr'):
            q = OOQuery('table')
            sel = q.select(['field1', 'field2'])
            sel2 = q.table.select(q.table.field1, q.table.field2)
            expect(str(sel._select)).to(equal(str(sel2)))
        with it('should have a where method to pass the domain'):
            q = OOQuery('table')
            sql = q.select(['field1', 'field2']).where([('field3', '=', 4)])
            t = Table('table')
            sel = t.select(t.field1, t.field2)
            sel.where = And((t.field3 == 4,))
            expect(tuple(sql)).to(equal(tuple(sel)))

        with it('must support joins'):
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

            q = OOQuery('table', dummy_fk)
            sql = q.select(['field1', 'field2', 'table_2.name']).where([
                ('table_2.code', '=', 'XXX')
            ])
            t = Table('table')
            t2 = Table('table2')
            join = t.join(t2)
            join.condition = join.left.table_2 == join.right.id
            sel = join.select(t.field1, t.field2, t2.name)
            sel.where = And((join.right.code == 'XXX',))
            expect(tuple(sql)).to(equal(tuple(sel)))

            q = OOQuery('table', dummy_fk)
            sql = q.select(['field1', 'field2', 'table_2.name']).where([])
            t = Table('table')
            t2 = Table('table2')
            join = t.join(t2)
            join.condition = join.left.table_2 == join.right.id
            sel = join.select(t.field1, t.field2, t2.name)
            expect(tuple(sql)).to(equal(tuple(sel)))

        with it('must support deep joins'):
            def dummy_fk(table):
                if table == 'table':
                    return {
                        'table_2_id': {
                            'constraint_name': 'fk_contraint_name',
                            'table_name': 'table',
                            'column_name': 'table_2_id',
                            'foreign_table_name': 'table2',
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
            sel = join2.select(t.field1, t.field2, t3.name)
            sel.where = And((join2.right.code == 'XXX',))
            expect(tuple(sql)).to(equal(tuple(sel)))
            expect(q.parser.joins_map).to(have_len(2))
            expect(str(q.parser.joins_map['table_2_id'])).to(equal(str(join)))
            expect(str(q.parser.joins_map['table_2_id.table_3_id'])).to(equal(str(join2)))

        with it('must support multiple deep joins'):
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

            sel = join3.select(t.field1, t.field2)
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
            sel = t.select(t.a, t.b, limit=10)
            expect(tuple(sql)).to(equal(tuple(sel)))

        with it('must support order'):
            q = OOQuery('table', None)
            sql = q.select(['a', 'b'], order_by=('a.asc', 'b.desc')).where([])

            t = Table('table')
            sel = t.select(t.a, t.b, order_by=(t.a.asc, t.b.desc))
            expect(tuple(sql)).to(equal(tuple(sel)))
