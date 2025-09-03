# coding=utf-8
from ooquery.domain_converter import convert_from_domain, convert_to_domain

from expects import *
from mamba import *


with description('The domain converter'):
    with description('when converting simple domains'):
        with it('should convert empty domain'):
            result = convert_from_domain([])
            expect(result).to(equal({
                'combinator': 'and',
                'rules': []
            }))
            
        with it('should convert single condition'):
            result = convert_from_domain([('name', '=', 'John')])
            expect(result).to(equal({
                'combinator': 'and',
                'rules': [
                    {'field': 'name', 'operator': '=', 'value': 'John'}
                ]
            }))
            
        with it('should convert multiple AND conditions (implicit)'):
            result = convert_from_domain([
                ('state', '=', 'open'),
                ('partner_id.name', '=', 'Pepito')
            ])
            expect(result).to(equal({
                'combinator': 'and',
                'rules': [
                    {'field': 'state', 'operator': '=', 'value': 'open'},
                    {'field': 'partner_id.name', 'operator': '=', 'value': 'Pepito'}
                ]
            }))
            
    with description('when converting OR domains'):
        with it('should convert simple OR condition'):
            result = convert_from_domain([
                '|',
                ('name', '=', 'John'),
                ('age', '>', 18)
            ])
            expect(result).to(equal({
                'combinator': 'or',
                'rules': [
                    {'field': 'name', 'operator': '=', 'value': 'John'},
                    {'field': 'age', 'operator': '>', 'value': 18}
                ]
            }))
            
        with it('should convert mixed OR and AND conditions'):
            result = convert_from_domain([
                '|',
                ('state', '=', 'open'),
                ('state', '=', 'draft'),
                ('active', '=', True)
            ])
            expect(result).to(equal({
                'combinator': 'and',
                'rules': [
                    {
                        'combinator': 'or',
                        'rules': [
                            {'field': 'state', 'operator': '=', 'value': 'open'},
                            {'field': 'state', 'operator': '=', 'value': 'draft'}
                        ]
                    },
                    {'field': 'active', 'operator': '=', 'value': True}
                ]
            }))
            
    with description('when converting explicit AND domains'):
        with it('should convert explicit AND condition'):
            result = convert_from_domain([
                '&',
                ('name', '=', 'John'),
                ('age', '>', 18)
            ])
            expect(result).to(equal({
                'combinator': 'and',
                'rules': [
                    {'field': 'name', 'operator': '=', 'value': 'John'},
                    {'field': 'age', 'operator': '>', 'value': 18}
                ]
            }))
            
    with description('when converting complex domains'):
        with it('should handle nested OR conditions'):
            result = convert_from_domain([
                '|',
                '|',
                ('state', '=', 'open'),
                ('state', '=', 'draft'),
                ('state', '=', 'pending')
            ])
            expect(result).to(equal({
                'combinator': 'or',
                'rules': [
                    {'field': 'state', 'operator': '=', 'value': 'open'},
                    {'field': 'state', 'operator': '=', 'value': 'draft'},
                    {'field': 'state', 'operator': '=', 'value': 'pending'}
                ]
            }))
            
    with description('when converting different operators'):
        with it('should handle various comparison operators'):
            result = convert_from_domain([
                ('age', '>', 18),
                ('salary', '>=', 1000),
                ('name', 'ilike', 'john%'),
                ('tags', 'in', ['important', 'urgent'])
            ])
            expect(result).to(equal({
                'combinator': 'and',
                'rules': [
                    {'field': 'age', 'operator': '>', 'value': 18},
                    {'field': 'salary', 'operator': '>=', 'value': 1000},
                    {'field': 'name', 'operator': 'contains', 'value': 'john%'},
                    {'field': 'tags', 'operator': 'in', 'value': ['important', 'urgent']}
                ]
            }))
            
        with it('should handle not equal operators'):
            result = convert_from_domain([
                ('state', '!=', 'cancelled'),
                ('state', '<>', 'deleted')
            ])
            expect(result).to(equal({
                'combinator': 'and',
                'rules': [
                    {'field': 'state', 'operator': '!=', 'value': 'cancelled'},
                    {'field': 'state', 'operator': '!=', 'value': 'deleted'}
                ]
            }))


with description('The domain converter to_domain'):
    with description('when converting empty or invalid queries'):
        with it('should handle empty query'):
            result = convert_to_domain({})
            expect(result).to(equal([]))
            
        with it('should handle None query'):
            result = convert_to_domain(None)
            expect(result).to(equal([]))
            
        with it('should handle query with empty rules'):
            result = convert_to_domain({'combinator': 'and', 'rules': []})
            expect(result).to(equal([]))
            
    with description('when converting simple AND queries'):
        with it('should convert single rule'):
            query = {
                'combinator': 'and',
                'rules': [
                    {'field': 'name', 'operator': '=', 'value': 'John'}
                ]
            }
            result = convert_to_domain(query)
            expect(result).to(equal([('name', '=', 'John')]))
            
        with it('should convert multiple AND rules'):
            query = {
                'combinator': 'and',
                'rules': [
                    {'field': 'name', 'operator': '=', 'value': 'John'},
                    {'field': 'age', 'operator': '>', 'value': 18}
                ]
            }
            result = convert_to_domain(query)
            expect(result).to(equal([
                ('name', '=', 'John'),
                ('age', '>', 18)
            ]))
            
    with description('when converting OR queries'):
        with it('should convert simple OR query'):
            query = {
                'combinator': 'or',
                'rules': [
                    {'field': 'name', 'operator': '=', 'value': 'John'},
                    {'field': 'age', 'operator': '>', 'value': 18}
                ]
            }
            result = convert_to_domain(query)
            expect(result).to(equal([
                '|', ('name', '=', 'John'), ('age', '>', 18)
            ]))
            
        with it('should convert multiple OR rules with binary grouping'):
            query = {
                'combinator': 'or',
                'rules': [
                    {'field': 'state', 'operator': '=', 'value': 'open'},
                    {'field': 'state', 'operator': '=', 'value': 'draft'},
                    {'field': 'state', 'operator': '=', 'value': 'pending'}
                ]
            }
            result = convert_to_domain(query)
            expect(result).to(equal([
                '|', '|', ('state', '=', 'open'), ('state', '=', 'draft'), ('state', '=', 'pending')
            ]))
            
    with description('when converting operator mappings'):
        with it('should convert contains operator'):
            query = {
                'combinator': 'and',
                'rules': [
                    {'field': 'name', 'operator': 'contains', 'value': 'john'}
                ]
            }
            result = convert_to_domain(query)
            expect(result).to(equal([('name', 'ilike', 'john')]))
            
        with it('should convert not contains operator'):
            query = {
                'combinator': 'and',
                'rules': [
                    {'field': 'name', 'operator': '!contains', 'value': 'john'}
                ]
            }
            result = convert_to_domain(query)
            expect(result).to(equal([('name', 'not ilike', 'john')]))
            
        with it('should convert in operator'):
            query = {
                'combinator': 'and',
                'rules': [
                    {'field': 'state', 'operator': 'in', 'value': ['open', 'draft']}
                ]
            }
            result = convert_to_domain(query)
            expect(result).to(equal([('state', 'in', ['open', 'draft'])]))
            
        with it('should convert not in operator'):
            query = {
                'combinator': 'and',
                'rules': [
                    {'field': 'state', 'operator': '!in', 'value': ['cancelled', 'deleted']}
                ]
            }
            result = convert_to_domain(query)
            expect(result).to(equal([('state', 'not in', ['cancelled', 'deleted'])]))
            
        with it('should handle in operator with string value'):
            query = {
                'combinator': 'and',
                'rules': [
                    {'field': 'state', 'operator': 'in', 'value': 'open, draft, pending'}
                ]
            }
            result = convert_to_domain(query)
            expect(result).to(equal([('state', 'in', ['open', 'draft', 'pending'])]))
            
    with description('when converting nested queries'):
        with it('should convert nested AND query within OR'):
            query = {
                'combinator': 'or',
                'rules': [
                    {'field': 'name', 'operator': '=', 'value': 'John'},
                    {
                        'combinator': 'and',
                        'rules': [
                            {'field': 'age', 'operator': '>', 'value': 18},
                            {'field': 'city', 'operator': '=', 'value': 'Barcelona'}
                        ]
                    }
                ]
            }
            result = convert_to_domain(query)
            expect(result).to(equal([
                '|', ('name', '=', 'John'), ('age', '>', 18), ('city', '=', 'Barcelona')
            ]))
            
        with it('should convert nested OR query within AND'):
            query = {
                'combinator': 'and',
                'rules': [
                    {'field': 'active', 'operator': '=', 'value': True},
                    {
                        'combinator': 'or',
                        'rules': [
                            {'field': 'state', 'operator': '=', 'value': 'open'},
                            {'field': 'state', 'operator': '=', 'value': 'draft'}
                        ]
                    }
                ]
            }
            result = convert_to_domain(query)
            expect(result).to(equal([
                ('active', '=', True),
                '|', ('state', '=', 'open'), ('state', '=', 'draft')
            ]))
            
    with description('when handling round-trip conversions'):
        with it('should maintain consistency for simple AND domain'):
            original_domain = [('name', '=', 'John'), ('age', '>', 18)]
            json_query = convert_from_domain(original_domain)
            result_domain = convert_to_domain(json_query)
            expect(result_domain).to(equal(original_domain))
            
        with it('should maintain consistency for simple OR domain'):
            original_domain = ['|', ('name', '=', 'John'), ('age', '>', 18)]
            json_query = convert_from_domain(original_domain)
            result_domain = convert_to_domain(json_query)
            expect(result_domain).to(equal(original_domain))
            
        with it('should maintain consistency for complex nested OR domain'):
            original_domain = ['|', '|', ('state', '=', 'open'), ('state', '=', 'draft'), ('state', '=', 'pending')]
            json_query = convert_from_domain(original_domain)
            result_domain = convert_to_domain(json_query)
            expect(result_domain).to(equal(original_domain))
            
        with it('should maintain consistency for mixed AND/OR domain'):
            original_domain = [
                ('active', '=', True),
                '|', ('state', '=', 'open'), ('state', '=', 'draft'),
                ('partner_id', '!=', False)
            ]
            json_query = convert_from_domain(original_domain)
            result_domain = convert_to_domain(json_query)
            expect(result_domain).to(equal(original_domain))
            
        with it('should maintain consistency for complex prefix notation'):
            original_domain = [
                '|', '&', ('name', 'ilike', 'John'), ('age', '>', 18),
                '&', ('city', '=', 'Barcelona'), ('active', '=', True)
            ]
            json_query = convert_from_domain(original_domain)
            result_domain = convert_to_domain(json_query)
            expect(result_domain).to(equal(original_domain))