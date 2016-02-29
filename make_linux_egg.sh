#/usr/bin/env bash

mnt="/code"
build_cmd="cd $mnt/build && cmake -DCMAKE_BUILD_TYPE=Release .. && make -B -j8 ms_cffi"
image=devtoolset-3

cd ims-cpp && docker build -t $image . && mkdir -p build &&\
    echo $build_cmd &&\
    docker run -v `pwd`:$mnt $image /bin/bash -c "$build_cmd" &&\
    cd .. && python setup.py bdist_egg
