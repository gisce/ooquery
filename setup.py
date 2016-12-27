from setuptools import setup, find_packages

setup(
    name='ooquery',
    version='0.5.1',
    packages=find_packages(),
    url='https://github.com/gisce/ooquery',
    license='MIT',
    author='GISCE-TI, S.L.',
    install_requires=[
        'python-sql'
    ],
    author_email='devel@gisce.net',
    description='OpenObject Query Parser',
)
