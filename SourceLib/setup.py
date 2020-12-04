try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='SourceLib',
    description='Python implementation of Valve Source Dedicated Server Query/RCON/Log protocols.',
    version="0.0.1",
    author='',
    author_email='',
    url='https://github.com/frostschutz/SourceLib',
    packages=['SourceLib'],
    package_dir = {'SourceLib': '.'}
)