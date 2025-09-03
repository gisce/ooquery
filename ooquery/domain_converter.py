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

# Inverse operator mapping to convert JSON operators back to OpenERP/Odoo operators
INVERSE_OPERATOR_MAP = {
    '=': '=',
    '!=': '!=',
    '>': '>',
    '<': '<',
    '>=': '>=',
    '<=': '<=',
    'like': 'like',
    'not like': 'not like',
    'contains': 'ilike',
    '!contains': 'not ilike',
    'in': 'in',
    '!in': 'not in',
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
            # Check if it's a nested domain or a condition tuple
            if len(element) > 0 and element[0] in ('|', '&'):
                # It's a nested domain, parse it recursively
                stack.append(_parse_domain_stack(element))
            else:
                # It's a condition tuple
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


def convert_to_domain(query):
    """
    Convert a JSON query structure to an OpenERP/Odoo domain.
    
    Args:
        query (dict): JSON structure with combinator and rules
        
    Returns:
        list: OpenERP/Odoo domain array
        
    Example:
        >>> convert_to_domain({'combinator': 'and', 'rules': [
        ...     {'field': 'name', 'operator': '=', 'value': 'John'}
        ... ]})
        [('name', '=', 'John')]
        
        >>> convert_to_domain({'combinator': 'or', 'rules': [
        ...     {'field': 'name', 'operator': '=', 'value': 'John'},
        ...     {'field': 'age', 'operator': '>', 'value': 18}
        ... ]})
        ['|', ('name', '=', 'John'), ('age', '>', 18)]
    """
    if not query or not isinstance(query, dict):
        return []
        
    rules = query.get('rules', [])
    if not rules:
        return []

    combinator = query.get('combinator', 'and')
    
    if combinator == 'and':
        # For AND, return a flat list combining all rules
        result = []
        for rule in rules:
            processed = _process_rule(rule)
            if (isinstance(processed, list) and len(processed) > 0 and 
                all(isinstance(item, (tuple, str)) for item in processed)):
                # It's a domain list, extend result with its elements
                result.extend(processed)
            else:
                result.append(processed)
        return result
    else:
        # For OR, build binary expression with prefix notation
        return _build_binary_expression('|', rules)


def _process_rule(rule):
    """Process a single rule into a domain tuple or sub-domain."""
    if not isinstance(rule, dict):
        raise ValueError("Rule must be a dictionary: {}".format(rule))
    
    if 'rules' in rule:
        # It's a nested query, convert recursively
        nested_domain = convert_to_domain(rule)
        # For AND queries, we want to return individual tuples, not a nested list
        # For OR queries, we return the list as-is since it has operators
        if (isinstance(nested_domain, list) and len(nested_domain) > 0 and 
            nested_domain[0] not in ('|', '&')):
            # It's an AND domain (list of tuples), return as individual tuples
            # This will be handled by the caller to flatten properly
            return nested_domain
        return nested_domain
    
    # It's a simple rule
    if 'field' not in rule or 'operator' not in rule or 'value' not in rule:
        raise ValueError("Rule must have field, operator and value: {}".format(rule))
    
    field = rule['field']
    json_operator = rule['operator']
    value = rule['value']
    
    # Convert operator using inverse mapping
    domain_operator = INVERSE_OPERATOR_MAP.get(json_operator, json_operator)
    
    # Special handling for 'in' operator with string values
    if domain_operator == 'in' and isinstance(value, str):
        value = [v.strip() for v in value.split(',')]
    
    return (field, domain_operator, value)


def _build_binary_expression(operator, rules):
    """Build binary expression for OR operations using flat prefix notation."""
    if len(rules) == 0:
        return []
    
    if len(rules) == 1:
        processed = _process_rule(rules[0])
        # If it's an AND list (no operators), flatten it
        if (isinstance(processed, list) and len(processed) > 0 and 
            all(isinstance(item, tuple) for item in processed)):
            return processed
        return processed
    
    # For OpenERP/Odoo domains, use flat prefix notation
    # Multiple OR: ['|', '|', rule1, rule2, rule3]
    # Not nested like ['|', ['|', rule1, rule2], rule3]
    result = []
    
    # Add n-1 operators for n rules (prefix notation)
    for i in range(len(rules) - 1):
        result.append(operator)
    
    # Add all processed rules
    for rule in rules:
        processed_rule = _process_rule(rule)
        if (isinstance(processed_rule, list) and len(processed_rule) > 0 and 
            all(isinstance(item, tuple) for item in processed_rule)):
            # It's an AND domain (list of tuples), add each tuple separately
            result.extend(processed_rule)
        else:
            result.append(processed_rule)
    
    return result


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