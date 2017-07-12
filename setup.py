import os
from distutils.core import setup

from setuptools import setup, find_packages
here = os.path.abspath(os.path.dirname(__file__))

setup(
    name='cmdtwiddler',
    version='1.2.0',
    description='Small wrapper for twiddler to add and remove supervisor processes on the fly from the command line',
    author='Bouke Nederstigt',
    author_email='bouke@tapp.cafe',
    url='https://github.com/TabsterApp/CMDTwiddler',
    download_url='https://github.com/TabsterApp/CMDTwiddler/archive/1.0.1.tar.gz',
    keywords=['supervisor', 'twiddler', 'command line'],
    classifiers=[],
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),

    install_requires=[
        "scriptine==0.2.1",
        "supervisor_twiddler==1.0.0",
        "hypothesis==3.12.0"
    ],
    entry_points={
        'console_scripts': ['cmdtwiddler=cmdtwiddler.cmdtwiddler:main']
    }
)
