****************
OpenObject Query
****************

.. image:: https://drone.io/github.com/gisce/ooquery/status.png
  :target: https://drone.io/github.com/gisce/ooquery/latest

Parsers OpenObjectes queries like:

.. code-block:: python

  search_params = [
    ('foo', '=', 'bar'),
    '|',
    ('test', '=' 0)
    ('test0, '=' False)
  ]
