import os, sys

sys.path.insert(0, '../')

class Mock(object):
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        return Mock()

    @classmethod
    def __getattr__(cls, name):
        if name in ('__file__', '__path__'):
            return '/dev/null'
        else:
            return Mock()

MOCK_MODULES = ['cffi']
for mod_name in MOCK_MODULES:
    sys.modules[mod_name] = Mock()

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.viewcode']

source_suffix = '.rst'
master_doc = 'index'

project = u'cpyMSpec'
copyright = u'2016, Alexandrov Team'

sys.path.insert(0, '../cpyMSpec')
from utils import VERSION
version = release = VERSION

exclude_patterns = ['_build']
pygments_style = 'sphinx'
