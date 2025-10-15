# coding=utf-8
from ooquery import OOQuery
from ooquery.functions import Unaccent
from sql import Table
from sql.functions import Upper, Lower
from sql.operators import And

from expects import *
from mamba import *


with description('PostgreSQL Functions'):
    with description('UNACCENT function'):
        with it('should work with field and literal value'):
            q = OOQuery('table')
            sql = q.select(['field1', 'field2']).where([
                (Unaccent('field1'), '=', Unaccent('value'))
            ])
            t = Table('table')
            sel = t.select(t.field1.as_('field1'), t.field2.as_('field2'))
            sel.where = And((Unaccent(t.field1) == Unaccent('value'),))
            expect(tuple(sql)).to(equal(tuple(sel)))

        with it('should work comparing two fields'):
            from ooquery.expression import Field
            
            q = OOQuery('table')
            sql = q.select(['field1', 'field2']).where([
                (Unaccent('field1'), '>', Unaccent(Field('field2')))
            ])
            t = Table('table')
            sel = t.select(t.field1.as_('field1'), t.field2.as_('field2'))
            sel.where = And((Unaccent(t.field1) > Unaccent(t.field2),))
            expect(tuple(sql)).to(equal(tuple(sel)))

        with it('should work with ilike operator'):
            q = OOQuery('table')
            sql = q.select(['field1']).where([
                (Unaccent('field1'), 'ilike', Unaccent('%pattern%'))
            ])
            t = Table('table')
            sel = t.select(t.field1.as_('field1'))
            sel.where = And((Unaccent(t.field1).ilike(Unaccent('%pattern%')),))
            expect(tuple(sql)).to(equal(tuple(sel)))

        with it('should work in joins'):
            def dummy_fk(table, field):
                fks = {
                    'related_id': {
                        'constraint_name': 'fk_constraint',
                        'table_name': 'table',
                        'column_name': 'related_id',
                        'foreign_table_name': 'related',
                        'foreign_column_name': 'id'
                    }
                }
                return fks[field]

            q = OOQuery('table', dummy_fk)
            sql = q.select(['field1', 'related_id.name']).where([
                (Unaccent('related_id.name'), '=', Unaccent('Test'))
            ])
            t = Table('table')
            t2 = Table('related')
            join = t.join(t2)
            join.condition = join.left.related_id == join.right.id
            sel = join.select(t.field1.as_('field1'), t2.name.as_('related_id.name'))
            sel.where = And((Unaccent(join.right.name) == Unaccent('Test'),))
            expect(tuple(sql)).to(equal(tuple(sel)))

        with it('should work with only left side unaccent'):
            q = OOQuery('table')
            sql = q.select(['field1']).where([
                (Unaccent('field1'), '=', 'test')
            ])
            t = Table('table')
            sel = t.select(t.field1.as_('field1'))
            sel.where = And((Unaccent(t.field1) == 'test',))
            expect(tuple(sql)).to(equal(tuple(sel)))

    with description('UPPER function'):
        with it('should work with field and literal value'):
            q = OOQuery('table')
            sql = q.select(['field1', 'field2']).where([
                (Upper('field1'), '=', Upper('value'))
            ])
            t = Table('table')
            sel = t.select(t.field1.as_('field1'), t.field2.as_('field2'))
            sel.where = And((Upper(t.field1) == Upper('value'),))
            expect(tuple(sql)).to(equal(tuple(sel)))

        with it('should work comparing two fields'):
            from ooquery.expression import Field
            
            q = OOQuery('table')
            sql = q.select(['field1', 'field2']).where([
                (Upper('field1'), '>', Upper(Field('field2')))
            ])
            t = Table('table')
            sel = t.select(t.field1.as_('field1'), t.field2.as_('field2'))
            sel.where = And((Upper(t.field1) > Upper(t.field2),))
            expect(tuple(sql)).to(equal(tuple(sel)))

        with it('should work with like operator'):
            q = OOQuery('table')
            sql = q.select(['field1']).where([
                (Upper('field1'), 'like', Upper('%PATTERN%'))
            ])
            t = Table('table')
            sel = t.select(t.field1.as_('field1'))
            sel.where = And((Upper(t.field1).like(Upper('%PATTERN%')),))
            expect(tuple(sql)).to(equal(tuple(sel)))

        with it('should work in joins'):
            def dummy_fk(table, field):
                fks = {
                    'related_id': {
                        'constraint_name': 'fk_constraint',
                        'table_name': 'table',
                        'column_name': 'related_id',
                        'foreign_table_name': 'related',
                        'foreign_column_name': 'id'
                    }
                }
                return fks[field]

            q = OOQuery('table', dummy_fk)
            sql = q.select(['field1', 'related_id.name']).where([
                (Upper('related_id.name'), '=', Upper('TEST'))
            ])
            t = Table('table')
            t2 = Table('related')
            join = t.join(t2)
            join.condition = join.left.related_id == join.right.id
            sel = join.select(t.field1.as_('field1'), t2.name.as_('related_id.name'))
            sel.where = And((Upper(join.right.name) == Upper('TEST'),))
            expect(tuple(sql)).to(equal(tuple(sel)))

        with it('should work with only left side upper'):
            q = OOQuery('table')
            sql = q.select(['field1']).where([
                (Upper('field1'), '=', 'TEST')
            ])
            t = Table('table')
            sel = t.select(t.field1.as_('field1'))
            sel.where = And((Upper(t.field1) == 'TEST',))
            expect(tuple(sql)).to(equal(tuple(sel)))

    with description('LOWER function'):
        with it('should work with field and literal value'):
            q = OOQuery('table')
            sql = q.select(['field1', 'field2']).where([
                (Lower('field1'), '=', Lower('value'))
            ])
            t = Table('table')
            sel = t.select(t.field1.as_('field1'), t.field2.as_('field2'))
            sel.where = And((Lower(t.field1) == Lower('value'),))
            expect(tuple(sql)).to(equal(tuple(sel)))

        with it('should work comparing two fields'):
            from ooquery.expression import Field
            
            q = OOQuery('table')
            sql = q.select(['field1', 'field2']).where([
                (Lower('field1'), '<', Lower(Field('field2')))
            ])
            t = Table('table')
            sel = t.select(t.field1.as_('field1'), t.field2.as_('field2'))
            sel.where = And((Lower(t.field1) < Lower(t.field2),))
            expect(tuple(sql)).to(equal(tuple(sel)))

        with it('should work with ilike operator'):
            q = OOQuery('table')
            sql = q.select(['field1']).where([
                (Lower('field1'), 'ilike', Lower('%pattern%'))
            ])
            t = Table('table')
            sel = t.select(t.field1.as_('field1'))
            sel.where = And((Lower(t.field1).ilike(Lower('%pattern%')),))
            expect(tuple(sql)).to(equal(tuple(sel)))

        with it('should work in joins'):
            def dummy_fk(table, field):
                fks = {
                    'related_id': {
                        'constraint_name': 'fk_constraint',
                        'table_name': 'table',
                        'column_name': 'related_id',
                        'foreign_table_name': 'related',
                        'foreign_column_name': 'id'
                    }
                }
                return fks[field]

            q = OOQuery('table', dummy_fk)
            sql = q.select(['field1', 'related_id.name']).where([
                (Lower('related_id.name'), '=', Lower('test'))
            ])
            t = Table('table')
            t2 = Table('related')
            join = t.join(t2)
            join.condition = join.left.related_id == join.right.id
            sel = join.select(t.field1.as_('field1'), t2.name.as_('related_id.name'))
            sel.where = And((Lower(join.right.name) == Lower('test'),))
            expect(tuple(sql)).to(equal(tuple(sel)))

        with it('should work with only left side lower'):
            q = OOQuery('table')
            sql = q.select(['field1']).where([
                (Lower('field1'), '=', 'test')
            ])
            t = Table('table')
            sel = t.select(t.field1.as_('field1'))
            sel.where = And((Lower(t.field1) == 'test',))
            expect(tuple(sql)).to(equal(tuple(sel)))

    with description('Multiple functions in same query'):
        with it('should work with different functions in same query'):
            q = OOQuery('table')
            sql = q.select(['field1', 'field2']).where([
                (Upper('field1'), '=', Upper('TEST')),
                (Lower('field2'), '=', Lower('test'))
            ])
            t = Table('table')
            sel = t.select(t.field1.as_('field1'), t.field2.as_('field2'))
            sel.where = And((
                Upper(t.field1) == Upper('TEST'),
                Lower(t.field2) == Lower('test')
            ))
            expect(tuple(sql)).to(equal(tuple(sel)))

        with it('should work with UNACCENT in complex joins'):
            def dummy_fk(table, field):
                if table == 'table':
                    fks = {
                        'parent_id': {
                            'constraint_name': 'fk_parent',
                            'table_name': 'table',
                            'column_name': 'parent_id',
                            'foreign_table_name': 'parent',
                            'foreign_column_name': 'id'
                        }
                    }
                elif table == 'parent':
                    fks = {
                        'grandparent_id': {
                            'constraint_name': 'fk_grandparent',
                            'table_name': 'parent',
                            'column_name': 'grandparent_id',
                            'foreign_table_name': 'grandparent',
                            'foreign_column_name': 'id'
                        }
                    }
                return fks[field]

            q = OOQuery('table', dummy_fk)
            sql = q.select(['field1']).where([
                (Unaccent('parent_id.grandparent_id.name'), '=', Unaccent('Tëst'))
            ])
            t = Table('table')
            t2 = Table('parent')
            t3 = Table('grandparent')
            join = t.join(t2)
            join.condition = t.parent_id == join.right.id
            join2 = join.join(t3)
            join2.condition = t2.grandparent_id == join2.right.id
            sel = join2.select(t.field1.as_('field1'))
            sel.where = And((Unaccent(join2.right.name) == Unaccent('Tëst'),))
            expect(tuple(sql)).to(equal(tuple(sel)))
