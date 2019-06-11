# coding=utf-8
from __future__ import absolute_import
from collections import OrderedDict

from sql import Table, Join
from sql.operators import Equal

from ooquery.operators import *
from ooquery.expression import Expression, InvalidExpressionException, Field


class Parser(object):
    def __init__(self, table, foreign_key=None):
        self.operators = OPERATORS_MAP
        self.table = table
        self.joins_map = OrderedDict()
        self.joins = []
        self.join_path = []
        self.foreign_key = foreign_key

    def get_join(self, dottet_path):
        return self.joins_map.get(dottet_path, None)

    @property
    def join_on(self):
        if self.joins:
            return self.joins[-1]
        else:
            return self.table

    def get_field_from_table(self, table, field):
        return getattr(table, field)

    def get_field_from_related_table(self, join_path_list, field_name):
        self.parse_join(join_path_list)
        path = '.'.join(join_path_list)
        join = self.joins_map.get(path)
        if join:
            table = join.right
            return self.get_field_from_table(table, field_name)

    def get_table_field(self, table, field):
        if '.' in field:
            return self.get_field_from_related_table(
                field.split('.')[:-1], field.split('.')[-1]
            )
        else:
            return self.get_field_from_table(table, field)

    def parse_join(self, fields_join):
        table = self.table
        self.join_path = []
        for field_join in fields_join:
            self.join_path.append(field_join)
            fk = self.foreign_key(table._name, field_join)
            table_join = Table(fk['foreign_table_name'])
            join = Join(self.join_on, table_join)
            column = getattr(table, fk['column_name'])
            fk_col = getattr(join.right, fk['foreign_column_name'])
            join.condition = Equal(column, fk_col)
            dotted_path = '.'.join(self.join_path)
            join = self.get_join(dotted_path)
            if not join:
                join = self.join_on.join(table_join)
                join.condition = Equal(column, fk_col)
                self.joins_map[dotted_path] = join
                self.joins.append(join)
                table = table_join
            else:
                if join not in self.joins:
                    self.joins.append(join)

                table = join.right

    def create_expressions(self, expression, column_left, column_right=None):
        expression = Expression(expression)
        expression.left = column_left
        if column_right:
            expression.right = column_right

        return [expression.expression]

    def get_expressions(self, expression):
        fields = [expression[0]]
        columns = []
        if isinstance(expression[2], Field):
            fields.append(expression[2].name)

        for idx, field in enumerate(fields):
            columns.append(self.get_table_field(self.table, field))
            if '.' in field:
                fields_join = field.split('.')[:-1]
                field_join = field.split('.')[-1]
                self.parse_join(fields_join)
                join = self.joins_map['.'.join(field.split('.')[:-1])]
                columns[idx] = self.get_table_field(join.right, field_join)

        return self.create_expressions(expression, *columns)

    def parse(self, query):
        result = []
        query = query[:]
        while query:
            expression = query.pop()
            if (not Expression.is_expression(expression)
                    and expression not in self.operators):
                raise InvalidExpressionException
            if Expression.is_expression(expression):
                result += self.get_expressions(expression)
            else:
                op = self.operators[expression]
                q = []
                for _ in range(0, op.n_pops):
                    q1 = result.pop()
                    q.append(q1)
                result.append(op(q))
        return And(reversed(result))
