# coding=utf-8
from __future__ import absolute_import
from collections import OrderedDict

from sql import Table, Join
from sql.operators import Equal

from ooquery.operators import *
from ooquery.expression import Expression, InvalidExpressionException


class Parser(object):
    def __init__(self, table, foreign_key=None):
        self.operators = OPERATORS_MAP
        self.table = table
        self.joins_map = OrderedDict()
        self.foreign_key = foreign_key

    def get_join(self, join):
        for j in self.joins:
            if str(j.right) == str(join.right):
                if str(j.condition) == str(join.condition):
                    return j
        return None

    @property
    def joins(self):
        return list(self.joins_map.values())

    @property
    def join_on(self):
        if self.joins:
            return self.joins[-1]
        else:
            return self.table

    def parse_join(self, fields_join):
        table = self.table
        join_path = []
        for field_join in fields_join:
            join_path.append(field_join)
            fk = self.foreign_key(table._name)[field_join]
            table_join = Table(fk['foreign_table_name'])
            join = Join(self.join_on, table_join)
            column = getattr(table, fk['column_name'])
            fk_col = getattr(join.right, fk['foreign_column_name'])
            join.condition = Equal(column, fk_col)
            join = self.get_join(join)
            if not join:
                join = self.join_on.join(table_join)
                join.condition = Equal(column, fk_col)
                self.joins_map['.'.join(join_path)] = join
                table = table_join
            else:
                table = join.right

    def parse(self, query):
        result = []
        while query:
            expression = query.pop()
            if (not Expression.is_expression(expression)
                    and expression not in self.operators):
                raise InvalidExpressionException
            if Expression.is_expression(expression):
                field = expression[0]
                column = getattr(self.table, field)
                if '.' in field:
                    fields_join = field.split('.')[:-1]
                    field_join = field.split('.')[-1]
                    self.parse_join(fields_join)
                    join = self.joins_map['.'.join(field.split('.')[:-1])]
                    column = getattr(join.right, field_join)
                expression = Expression(expression)
                expression.left = column
                result.append(expression.expression)
            else:
                op = self.operators[expression]
                q = []
                for _ in range(0, op.n_pops):
                    q1 = result.pop()
                    q.append(q1)
                result.append(op(q))
        return And(reversed(result))
