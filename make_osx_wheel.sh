#/usr/bin/env bash

# the official distribution from python.org should be used instead of the system one,
# see reasons here: https://github.com/MacPython/wiki/wiki/Spinning-wheels

rm -rf dist &&\
cd ims-cpp && mkdir -p build && cd build &&\
    cmake -DCMAKE_C_COMPILER=gcc-5 -DCMAKE_CXX_COMPILER=g++-5 -DCMAKE_BUILD_TYPE=Release .. &&\
    make ms_cffi && cd ../../ &&\
    /usr/local/bin/python setup.py bdist_wheel &&\
    delocate-wheel dist/cpyMSpec*.whl
