****************
OpenObject Query
****************

Parsers OpenObjectes queries like:

..code-block: python

  search_params = [
    ('foo', '=', 'bar'),
    '|',
    ('test', '=' 0)
    ('test0, '=' False)
  ]
