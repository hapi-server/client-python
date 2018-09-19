#from distutils.core import setup
from setuptools import setup
import sys

# version is modified by misc/setversion.py. See Makefile.
setup(
    name='hapiclient',
    version='0.0.2',
    author='Bob Weigel',
    author_email='rweigel@gmu.edu',
    packages=['hapiclient'],
    url='http://pypi.python.org/pypi/hapiclient/',
    license='LICENSE.txt',
    description='Heliophysics API',
    long_description=open('README.txt').read(),
    install_requires=["numpy>=1.14.3","pandas==0.23.0","matplotlib>=2.2.2"]
)








