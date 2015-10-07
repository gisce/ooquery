from setuptools import setup, find_packages

setup(
    name='ooquery',
    version='0.1.1',
    packages=find_packages(exclude=('tests', )),
    url='https://github.com/gisce/ooquery',
    license='MIT',
    author='GISCE-TI, S.L.',
    author_email='devel@gisce.net',
    description='OpenObject Query Parser',
    test_suite='tests'
)
