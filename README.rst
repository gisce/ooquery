****************
OpenObject Query
****************

Python 2.7 and >=3.5

.. image:: https://travis-ci.org/gisce/ooquery.svg?branch=master
    :target: https://travis-ci.org/gisce/ooquery
.. image:: https://coveralls.io/repos/github/gisce/ooquery/badge.svg?branch=master
    :target: https://coveralls.io/github/gisce/ooquery?branch=master
.. image:: https://img.shields.io/pypi/v/ooquery.svg
    :target: https://pypi.python.org/pypi/ooquery


Parsers OpenObjectes queries like:

.. code-block:: python

   import pyscopg2

   from oopgrade.oopgrade import get_foreign_keys
   from ooquery import OOQuery

   conn = psycopg2.connect("dbname=test user=postgres")
   with conn.cursor() as cursor:
       def fk_function(table, field):
           fks = get_foreign_keys(cursor, table)
           return fks[field]

       q = OOQuery('account_invoice', fk_function)
       sql = q.select(['number', 'state']).where([
           ('state', '=', 'open'),
           ('partner_id.name', '=', 'Pepito')
       ])
       cursor.execute(*sql)

Support for reading from joined tables

.. code-block:: python

    q = OOQuery('account_invoice', fk_function)
    sql = q.select(['number', 'partner_id.name', 'partner_id.vat']).where([
        ('state', '=', 'open')
    ])

Domain to JSON Conversion
=========================

Convert OpenERP/Odoo domains to JSON format:

.. code-block:: python

    from ooquery import convert_from_domain
    import json

    # Simple domain
    domain = [('name', '=', 'John'), ('age', '>', 18)]
    result = convert_from_domain(domain)
    print(json.dumps(result, indent=2))
    # {
    #   "combinator": "and",
    #   "rules": [
    #     {"field": "name", "operator": "=", "value": "John"},
    #     {"field": "age", "operator": ">", "value": 18}
    #   ]
    # }

    # OR conditions  
    domain = ['|', ('state', '=', 'open'), ('state', '=', 'draft')]
    result = convert_from_domain(domain)
    # {
    #   "combinator": "or", 
    #   "rules": [
    #     {"field": "state", "operator": "=", "value": "open"},
    #     {"field": "state", "operator": "=", "value": "draft"}
    #   ]
    # }

JSON to Domain Conversion
=========================

Convert JSON format back to OpenERP/Odoo domains:

.. code-block:: python

    from ooquery import convert_to_domain

    # Simple AND query
    query = {
        'combinator': 'and',
        'rules': [
            {'field': 'name', 'operator': '=', 'value': 'John'},
            {'field': 'age', 'operator': '>', 'value': 18}
        ]
    }
    domain = convert_to_domain(query)
    # [('name', '=', 'John'), ('age', '>', 18)]

    # OR query with binary expression
    query = {
        'combinator': 'or',
        'rules': [
            {'field': 'state', 'operator': '=', 'value': 'open'},
            {'field': 'state', 'operator': '=', 'value': 'draft'}
        ]
    }
    domain = convert_to_domain(query)
    # ['|', ('state', '=', 'open'), ('state', '=', 'draft')]

    # Round-trip conversion
    original_domain = ['|', ('name', 'ilike', 'john%'), ('email', 'ilike', 'john%')]
    json_query = convert_from_domain(original_domain)
    back_to_domain = convert_to_domain(json_query)
    # back_to_domain == original_domain
