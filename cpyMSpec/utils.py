import platform
import os.path

def full_filename(fn):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), fn))

def shared_lib(name):
    suffixes = {'Windows': 'dll', 'Linux': 'so', 'Darwin': 'dylib'}
    return 'lib' + name + '.' + suffixes[platform.system()]

VERSION="0.2.0"
