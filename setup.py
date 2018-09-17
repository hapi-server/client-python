from distutils.core import setup
import sys

Version = '0.0.4'

if sys.version_info[0] >= 3:
    install_requires = ["numpy>=1.14.3","pandas==0.23.0","matplotlib>=2.2.2"]
else:
    install_requires = ["numpy>=1.14.3","pandas==0.23.0","matplotlib>=2.2.2"]

setup(
    name='hapiclient',
    version=Version,
    author='Bob Weigel',
    author_email='rweigel@gmu.edu',
    packages=['hapiclient'],
    url='http://pypi.python.org/pypi/hapiclient/',
    license='LICENSE.txt',
    description='Heliophysics API',
    long_description=open('README.txt').read(),
    install_requires=install_requires
)