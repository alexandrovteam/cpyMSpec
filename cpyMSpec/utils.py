import platform
import os.path
import cffi

def full_filename(fn):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), fn))

def shared_lib(name):
    suffixes = {'Windows': 'dll', 'Linux': 'so', 'Darwin': 'dylib'}
    return 'lib' + name + '.' + suffixes[platform.system()]

def init_ffi():
    ffi = cffi.FFI()
    ffi.cdef(open(full_filename("ims.h")).read())
    return ffi

def load_shared_lib(ffi):
    return ffi.dlopen(full_filename(shared_lib("ms_cffi")))

VERSION = "0.3.1"
