#from distutils.core import setup
from setuptools import setup, find_packages
import sys

install_requires = ["numpy>=1.14.3",
                    "pandas>=0.23.*,<=0.24.*",
                    'matplotlib>=2.2.2;python_version>"3.5"',
                    'matplotlib<3.0;python_version<"3.5"',
                    "isodate>=0.6.0"]

if sys.argv[1] == 'develop':
    install_requires.append("deepdiff<3.3.0")
    install_requires.append("pytest")

# version is modified by misc/setversion.py. See Makefile.
setup(
    name='hapiclient',
    version='0.0.9b0',
    author='Bob Weigel',
    author_email='rweigel@gmu.edu',
    packages=find_packages(),
    url='http://pypi.python.org/pypi/hapiclient/',
    license='LICENSE.txt',
    description='Heliophysics API',
    long_description=open('README.rst').read(),
    install_requires=install_requires
)































