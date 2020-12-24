import sys
from setuptools import setup, find_packages

install_requires = ["isodate>=0.6.0","urllib3","joblib"]

if sys.version_info >= (3, 6):
    install_requires.append('pandas>=0.23')
    install_requires.append('numpy>=1.14.3')
elif sys.version_info < (3, 6) and sys.version_info > (3, ):
    install_requires.append("pandas<1.0")
    install_requires.append("numpy<1.17")
    install_requires.append("kiwisolver<=1.2")
else:
    install_requires.append("pandas>=0.23,<0.25")
    install_requires.append("numpy<1.17")
    install_requires.append("pyparsing<3")
    install_requires.append("zipp<3")
    install_requires.append("kiwisolver<=1.1")

if sys.argv[1] == 'develop':
    install_requires.append("deepdiff<3.3.0")
    if sys.version_info < (3, 6):
        install_requires.append("pytest<5.0.0")
    else:
        # Should not be needed, as per
        # https://docs.pytest.org/en/stable/py27-py34-deprecation.html
        # Perhaps old version of pip causes this?
        install_requires.append("pytest")

# version is modified by misc/version.py (executed from Makefile). Do not edit.
setup(
    name='hapiclient',
    version='0.1.9b0',
    author='Bob Weigel',
    author_email='rweigel@gmu.edu',
    packages=find_packages(),
    url='http://pypi.python.org/pypi/hapiclient/',
    license='LICENSE.txt',
    description='Heliophysics API',
    long_description=open('README.rst').read(),
    install_requires=install_requires
)
