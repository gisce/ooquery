# coding=utf-8
from __future__ import absolute_import
from sql import Table
from ooquery.parser import Parser


class OOQuery(object):
    def __init__(self, table, foreign_key=None):
        self._fields = []
        self.table = Table(table)
        self._select = self.table.select()
        self.parser = Parser(self.table, foreign_key)
        self.select_opts = {}

    @property
    def select_on(self):
        if self.parser.joins:
            return self.parser.joins[-1]
        else:
            return self.table

    @property
    def fields(self):
        fields = []
        for field in self._fields:
            if '.' in field:
                join_path = field.split('.')[:-1]
                self.parser.parse_join(join_path)
                path = '.'.join(join_path)
                join = self.parser.joins_map.get(path)
                if join:
                    table = join.right
                    fields.append(getattr(table, field.split('.')[-1]))
            else:
                fields.append(getattr(self.table, field))
        return fields

    def select(self, fields=None, **kwargs):
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
