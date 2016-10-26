#/usr/bin/env bash

mnt="/code"
build_cmd='
cd /code/ims-cpp/build &&\
cmake -DCMAKE_BUILD_TYPE=Release .. &&\
make -B -j8 ms_cffi && cd /code && rm -r dist/*;
source activate py2; python setup.py bdist_wheel;
source activate py3; python setup.py bdist_wheel;
source activate py3; for fn in `ls dist/*.whl`; do auditwheel repair $fn; done
'

image=devtoolset-3

docker build -t $image ims-cpp && mkdir -p ims-cpp/build &&\
    echo $build_cmd &&\
    docker run -v `pwd`:$mnt $image /bin/bash -c "$build_cmd"
