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
       def fk_function(table):
           return get_foreign_keys(cursor, table)

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
