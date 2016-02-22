#/usr/bin/env bash

cd ims-cpp && mkdir -p build && cd build &&\
    cmake -DCMAKE_C_COMPILER=gcc-5 -DCMAKE_CXX_COMPILER=g++-5 -DCMAKE_BUILD_TYPE=Release .. &&\
    make ms_cffi && cd ../../ &&\
    python setup.py bdist_wheel
