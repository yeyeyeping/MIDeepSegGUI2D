import sys, os
from os.path import pardir

def get_root_dir():
    return os.path.abspath((os.path.join(__file__, pardir, pardir, pardir)))
def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(get_root_dir(), relative_path)