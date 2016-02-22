from setuptools import setup, find_packages
from distutils.core import Extension
from shutil import copyfile
import os

# before building the wheel, CMake must be run manually from cpp/build;

import sys
sys.path.insert(0, "cpyMSpec")
from utils import shared_lib

shared_lib_filename = shared_lib('ms_cffi')

# I couldn't make setup() to copy files in a non-trivial way, is it possible?
extra_files = {
    os.path.join('ims-cpp', 'build', shared_lib_filename):
    os.path.join('cpyMSpec', shared_lib_filename),

    os.path.join('ims-cpp', 'cffi', 'ims.h'):
    os.path.join('cpyMSpec', 'ims.h')
}

for src, dst in extra_files.items():
    copyfile(src, dst)

setup(
    name='cpyMSpec',
    version='0.0.1',
    author='Artem Tarasov',
    author_email='artem.tarasov@embl.de',
    url='https://github.com/alexandrovteam/cpyMSpec',
    license='Apache 2.0',
    description='isotope pattern calculator for small molecules',
    packages=find_packages(where='.'),
    package_data={'cpyMSpec': [shared_lib_filename, 'ims.h']},
    setup_requires=['wheel>=0.27.0'],
    install_requires=['cffi>=1.0'],

    # force bdist_wheel to believe it's a platform-specific wheel
    ext_modules=[Extension('cpyMSpec._dummy', sources=['dummy.c'])],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
    ]
)

for dst in extra_files.values():
    os.remove(dst)
