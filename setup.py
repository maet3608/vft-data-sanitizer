from setuptools import setup, find_packages

import vds

setup(
    name='vds',
    version=vds.__version__,
    url='https://github.com/maet3608/vft-data-sanitizer',
    author='Stefan Maetschke',
    author_email='stefan.maetschke@gmail.com',
    description='Remove sensitive information from visual field test data',
    packages=find_packages(),
    install_requires=[],
)
