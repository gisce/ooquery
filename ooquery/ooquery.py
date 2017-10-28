# coding=utf-8
from __future__ import absolute_import
from functools import reduce

from sql import Table
from ooquery.parser import Parser


class OOQuery(object):
    def __init__(self, table, foreign_key=None):
        self._fields = []
        self.table = Table(table)
        self.foreign_key = foreign_key
        self._select = self.table.select()
        self.parser = Parser(self.table, self.foreign_key)
        self.select_opts = {}

    @property
    def select_on(self):
        if self.parser.joins:
            return self.parser.joins[-1]
        else:
            return self.table

    def get_field_from_table(self, table, field):
        return getattr(table, field)

    def get_field_from_related_table(self, join_path_list, field_name):
        self.parser.parse_join(join_path_list)
        path = '.'.join(join_path_list)
        join = self.parser.joins_map.get(path)
        if join:
            table = join.right
            return self.get_field_from_table(table, field_name)

    def get_table_field(self, field):
        if '.' in field:
            return self.get_field_from_related_table(
                field.split('.')[:-1], field.split('.')[-1]
            )
        else:
            return self.get_field_from_table(self.table, field)

    @property
    def fields(self):
        fields = []
        for field in self._fields:
            table_field = self.get_table_field(field)
            fields.append(table_field.as_(field.replace('.', '_')))
        return fields

    def select(self, fields=None, **kwargs):
        self.parser = Parser(self.table, self.foreign_key)
        self._fields = fields
        self.select_opts = kwargs
        order_by = kwargs.pop('order_by', None)
        if order_by:
            kwargs['order_by'] = []
            for item in order_by:
                kwargs['order_by'].append(
                    reduce(getattr, item.split('.'), self.select_on)
                )
        self._select = self.select_on.select(*self.fields, **self.select_opts)
        return self

    def where(self, domain):
        where = self.parser.parse(domain)
        self._select = self.select_on.select(*self.fields, **self.select_opts)
        self._select.where = where
        return self._select
