# coding=utf-8
from __future__ import absolute_import
from functools import reduce

from sql import Table, Literal, NullOrder, As
from sql.aggregate import Aggregate
from sql.conditionals import Conditional
from sql.operators import Operator
from ooquery.parser import Parser


class OOQuery(object):
    def __init__(self, table, foreign_key=None):
        self._fields = []
        self.table = Table(table)
        self.foreign_key = foreign_key
        self._select = self.table.select()
        self.parser = self.create_parser()
        self.select_opts = {}
        self.as_ = {}

    def create_parser(self):
        return Parser(self.table, self.foreign_key)

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
            output_name = None
            if isinstance(field, As):
                output_name = field.output_name
                field = field.expression
            if isinstance(field, Aggregate):
                aggr = field.__class__
                field = field.expression
                table_field = self.parser.get_table_field(self.table, field)
                table_field = aggr(table_field)
                if not output_name:
                    field = '{}_{}'.format(aggr._sql, field).lower()
                    fields.append(table_field.as_(self.as_.get(field, field)))
                else:
                    fields.append(table_field.as_(output_name))
            elif isinstance(field, Conditional):
                cond = field.__class__
                params = []
                for param in field.values:
                    if not isinstance(param, Literal):
                        param = self.parser.get_table_field(self.table, param)
                    else:
                        param = param.value
                    params.append(param)
                table_field = cond(*params)
                fields.append(table_field)
            elif isinstance(field, Operator):
                operator = field.__class__
                operands = []
                for operand in field._operands:
                    if not isinstance(operand, Literal):
                        operand = self.parser.get_table_field(self.table, operand)
                    else:
                        operand = operand.value
                    operands.append(operand)
                table_field = operator(*operands)
                fields.append(table_field)
            else:
                table_field = self.parser.get_table_field(self.table, field)
                if table_field is None:
                    raise AttributeError(
                        u"Field '{field}' does not exist on table: "
                        u"'{table}'".format(
                            field=field, table=self.table._name
                        )
                    )
                fields.append(table_field.as_(self.as_.get(field, field)))
        return fields

    def select(self, fields=None, **kwargs):
        self.parser = self.create_parser()
        self._fields = fields
        self.select_opts = kwargs
        self.as_ = kwargs.pop('as_', self.as_)
        order_by = kwargs.pop('order_by', None)
        group_by = kwargs.pop('group_by', None)
        if order_by:
            kwargs['order_by'] = []
            for item in order_by:
                null_order = None
                if isinstance(item, NullOrder):
                    null_order = item.__class__
                    item = item.expression
                order_values = item.rsplit('.', 1)
                order = self.parser.get_table_field(self.table, order_values[0])
                if len(order_values) > 1:
                    order = getattr(order, order_values[1])
                if null_order:
                    order = null_order(order)
                kwargs['order_by'].append(order)
        if group_by:
            kwargs['group_by'] = []
            for item in group_by:
                table_field = self.parser.get_table_field(
                    self.table, item
                )
                kwargs['group_by'].append(
                    table_field
                )
        self._select = self.select_on.select(*self.fields, **self.select_opts)
        return self

    def where(self, domain):
        where = self.parser.parse(domain)
        self._select = self.select_on.select(*self.fields, **self.select_opts)
        self._select.where = where
        return self._select
