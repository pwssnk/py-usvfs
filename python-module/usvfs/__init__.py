
"""
Python bindings for the userspace virtual filesystem (usvfs) library.
"""


from .usvfs_wrapper import USVFSException, VirtualFile, VirtualDirectory, Mapping, UserspaceVFS, dll

__all__ = (
    'dll',
    'USVFSException',
    'VirtualDirectory',
    'VirtualFile',
    'Mapping',
    'UserspaceVFS'
)


__author__ = 'pwssnk'
__copyright__ = 'Copyright 2019, pwssnk'
__credits__ = ['pwssnk', 'Usvfs developers']
__license__ = 'GPLv3'
__version__ = '0.2.0'
__maintainer__ = 'pwssnk'
__email__ = ''
__status__ = 'Development'
