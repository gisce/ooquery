from ooquery.expression import Expression, InvalidExpressionException
from sql.operators import *

from expects import *


with description('Creating an expression'):
    with context('if is an invalid expression'):
        with it('must raise an InvalidExpressionException'):
            def callback():
                Expression(('a',))

            expect(callback).to(raise_error(InvalidExpressionException))

    with context('if is a valid expresion'):
        with it('not sould fail'):
            exp = Expression(('a', '=', 'b'))
            expect(exp.expression).to(equal(Equal('a', 'b')))

    with context('if has an invalid operand'):
        with it('must raise an exception'):
            def callback():
                Expression(('a', '!!=', 'b'))

            expect(callback).to(raise_error(
                ValueError, 'Operator !!= is not supported'
            ))

    with context('testing if is a valid expression'):
        with it('must return true if is a valid expression'):
            is_exp = Expression.is_expression(('a', '=', 'b'))
            expect(is_exp).to(be_true)
        with it('must return false if is an invalid expression'):
            is_exp = Expression.is_expression(('a', '='))
            expect(is_exp).to(be_false)
