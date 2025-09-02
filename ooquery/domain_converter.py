# coding=utf-8
"""
Domain to JSON converter module.

This module provides functionality to convert OpenERP/Odoo domains 
(arrays of tuples) to JSON format, similar to the TypeScript implementation
in gisce/ooquery-ts.
"""

from __future__ import absolute_import

# Operator mapping to convert OpenERP/Odoo operators to more standard ones
OPERATOR_MAP = {
    '=': '=',
    '!=': '!=',
    '<>': '!=',
    '>': '>',
    '<': '<',
    '>=': '>=',
    '<=': '<=',
    'like': 'like',
    'not like': 'not like',
    'ilike': 'contains',
    'not ilike': '!contains',
    '=like': 'like',
    '=ilike': 'contains',
    'in': 'in',
    'not in': '!in',
}


def convert_from_domain(domain):
    """
    Convert an OpenERP/Odoo domain to JSON format.
    
    Args:
        domain (list): Domain array containing tuples and operators
        
    Returns:
        dict: JSON structure with combinator and rules
        
    Example:
        >>> convert_from_domain([('name', '=', 'John')])
        {'combinator': 'and', 'rules': [{'field': 'name', 'operator': '=', 'value': 'John'}]}
        
        >>> convert_from_domain(['|', ('name', '=', 'John'), ('age', '>', 18)])
        {'combinator': 'or', 'rules': [
            {'field': 'name', 'operator': '=', 'value': 'John'},
            {'field': 'age', 'operator': '>', 'value': 18}
        ]}
    """
    if not domain:
        return {'combinator': 'and', 'rules': []}
        
    result = _parse_domain_stack(domain)
    return _optimize_query(result)


def _parse_domain_stack(domain):
    """Parse domain using stack-based approach."""
    stack = []
    
    for element in reversed(domain):  # Process in reverse to handle prefix operators
        if element == '|':
            # OR operator - pop two operands and create OR rule
            if len(stack) < 2:
                raise ValueError("Invalid domain: OR operator needs two operands")
            left = stack.pop()
            right = stack.pop()
            stack.append({
                'combinator': 'or',
                'rules': [left, right]
            })
        elif element == '&':
            # AND operator - pop two operands and create AND rule  
            if len(stack) < 2:
                raise ValueError("Invalid domain: AND operator needs two operands")
            left = stack.pop()
            right = stack.pop()
            stack.append({
                'combinator': 'and',
                'rules': [left, right]
            })
        elif isinstance(element, (list, tuple)):
            # Regular condition tuple
            stack.append(_process_element(element))
    
    # Combine remaining stack elements with AND (reverse to maintain order)
    if len(stack) == 0:
        return {'combinator': 'and', 'rules': []}
    elif len(stack) == 1:
        result = stack[0]
        # If it's a simple rule, wrap it in a query
        if 'field' in result:
            return {'combinator': 'and', 'rules': [result]}
        return result
    else:
        # Multiple rules left, combine with AND and reverse to maintain original order
        return {'combinator': 'and', 'rules': list(reversed(stack))}


def _process_element(element):
    """Process a single domain element into a rule."""
    if isinstance(element, (list, tuple)):
        if len(element) != 3:
            raise ValueError("Invalid condition tuple: {}".format(element))
            
        field, domain_operator, value = element
        
        # Convert operator using mapping (keep original operator if not found)
        operator = OPERATOR_MAP.get(domain_operator, domain_operator)
        
        return {
            'field': field,
            'operator': operator,
            'value': value
        }
    else:
        raise ValueError("Unknown element: {}".format(element))


def _optimize_query(query):
    """Optimize query by flattening unnecessary nesting."""
    if not isinstance(query, dict) or 'rules' not in query:
        return query
        
    rules = query['rules']
    
    # If only one rule, return it directly if it's a query
    if len(rules) == 1:
        rule = rules[0]
        if isinstance(rule, dict) and 'combinator' in rule:
            return rule
        # Otherwise keep the single rule in the query
        return query
    
    # Flatten rules with same combinator
    optimized_rules = []
    for rule in rules:
        if (isinstance(rule, dict) and 
            'combinator' in rule and 
            rule['combinator'] == query['combinator']):
            # Same combinator - flatten the rules
            optimized_rule = _optimize_query(rule)
            if 'rules' in optimized_rule:
                optimized_rules.extend(optimized_rule['rules'])
            else:
                optimized_rules.append(optimized_rule)
        else:
            optimized_rules.append(rule)
    
    return {
        'combinator': query['combinator'],
        'rules': optimized_rules
    }