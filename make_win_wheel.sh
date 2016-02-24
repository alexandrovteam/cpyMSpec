#/usr/bin/env bash

# this script should be run in MINGW32 shell (from MSYS2)

CC=gcc
CXX=g++
PYTHON=C:/Python27/python.exe

cd ims-cpp && mkdir -p build && cd build &&\
    cmake -DCMAKE_C_COMPILER=${CC} -DCMAKE_CXX_COMPILER=${CXX} -DCMAKE_BUILD_TYPE=Release -G "MSYS Makefiles" .. &&\
    make ms_cffi && cd ../../ &&\
    ${PYTHON} setup.py bdist_wheel
