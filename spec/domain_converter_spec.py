# coding=utf-8
from ooquery.domain_converter import convert_from_domain

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