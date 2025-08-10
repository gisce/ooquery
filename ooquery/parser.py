# coding=utf-8
from __future__ import absolute_import
from collections import OrderedDict

from sql import Table, Join
from sql.operators import Equal

from ooquery.operators import *
from ooquery.expression import Expression, InvalidExpressionException, Field
# Py2/3 compat per a tipus de cadena
try:  # Py2
    string_types = (basestring,)
except NameError:  # Py3
    string_types = (str,)
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
        # Accepta també Field d'ooquery: normalitza a nom
        if isinstance(field, Field):
            field = field.name
        return getattr(table, field)

    def get_field_from_related_table(self, join_path_list, field_name, join_type='INNER'):
        self.parse_join(join_path_list, join_type)
        path = '.'.join(join_path_list)
        join = self.joins_map.get(path)
        if join:
            table = join.right
            return self.get_field_from_table(table, field_name)

    def get_table_field(self, table, field):
        # Accepta també Field d'ooquery: normalitza a nom
        if isinstance(field, Field):
            field = field.name
        if isinstance(field, JoinType):
            join_type = field.type_
            field = field.field
        else:
            join_type = 'INNER'
        if isinstance(field, str) and '.' in field:
            return self.get_field_from_related_table(
                field.split('.')[:-1], field.split('.')[-1],
                join_type
            )
        else:
            return self.get_field_from_table(table, field)

    def parse_join(self, fields_join, join_type):
        table = self.table
        self.join_path = []
        for field_join in fields_join:
            self.join_path.append(field_join)
            fk = self.foreign_key(table._name, field_join)
            table_join = Table(fk['foreign_table_name'])
            join = Join(self.join_on, table_join, type_=join_type)
            column = getattr(table, fk['column_name'])
            fk_col = getattr(join.right, fk['foreign_column_name'])
            join.condition = Equal(column, fk_col)
            dotted_path = '.'.join(self.join_path)
            join = self.get_join(dotted_path)
            if not join:
                join = self.join_on.join(table_join, type_=join_type)
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
        from sql.functions import Function

        def resolve_value(value, side='left', in_function=False):
            """
            Rules:
              - Dins d'una Function: les cadenes són NOMS DE CAMP (possiblement 'a.b.c').
              - Top-level LEFT: cadenes = NOMS DE CAMP.
              - Top-level RIGHT: cadenes = LITERALS (parametritzats com %s).
            """
            # Funcions: resol paràmetres recursivament i reconstrueix la instància
            if isinstance(value, Function):
                new_params = []
                for p in value.params:
                    new_params.append(resolve_value(p, side='left', in_function=True))
                # IMPORTANT: no mutar tuples! Re-creem la funció amb els params resolts
                return value.__class__(*new_params)

            # Field d'ooquery → columna
            if isinstance(value, Field):
                return self.get_table_field(self.table, value.name)

            # JoinType → camí de camp amb tipus de join
            if isinstance(value, JoinType):
                return self.get_table_field(self.table, value)

            # Cadenes: segons context
            if isinstance(value, string_types):
                if in_function or side == 'left':
                    return self.get_table_field(self.table, value)
                else:
                    # RHS literal (permet: ('b.code', '=', 'XXX') → %s)
                    return value

            # Altres literals (números, None, etc.)
            return value

        left = expression[0]
        left_resolved = resolve_value(left, side='left')
        right_resolved = resolve_value(expression[2], side='right')

        return self.create_expressions(expression, left_resolved, right_resolved)

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
