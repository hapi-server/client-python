#from distutils.core import setup
from setuptools import setup, find_packages
import sys

install_requires = ["hapiplotserver==0.0.1","numpy>=1.14.3","pandas==0.23.0","matplotlib>=2.2.2","isodate>=0.6.0"]

if sys.argv[1] == 'develop':
    install_requires.append("deepdiff")

# version is modified by misc/setversion.py. See Makefile.
setup(
    name='hapiclient',
    version='0.0.7',
    author='Bob Weigel',
    author_email='rweigel@gmu.edu',
    packages=find_packages(),
    url='http://pypi.python.org/pypi/hapiclient/',
    license='LICENSE.txt',
    description='Heliophysics API',
    long_description=open('README.rst').read(),
    install_requires=install_requires
)

























