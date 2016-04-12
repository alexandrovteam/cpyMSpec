#/usr/bin/env bash

mnt="/code"
build_cmd="
cd $mnt/ims-cpp/build &&\
cmake -DCMAKE_BUILD_TYPE=Release .. &&\
make -B -j8 ms_cffi && cd $mnt && rm -r dist/*;
source activate py2; python setup.py bdist_wheel;
source activate py3; auditwheel repair dist/cpyMSpec*.whl
"

image=devtoolset-3

docker build -t $image ims-cpp && mkdir -p ims-cpp/build &&\
    echo $build_cmd &&\
    docker run -v `pwd`:$mnt $image /bin/bash -c "$build_cmd"
