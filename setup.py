
import setuptools
import shutil
import sys
import os

# Copy CPython extension and required usvfs binaries before packaging module
if 'win_amd64' in sys.argv:
    print('Building package for win_amd64')
    binaries = (
        'python-extension/build/Release/x64/_usvfs_dll.pyd',
        'python-extension/usvfs/bin/usvfs_x64.dll',
        'python-extension/usvfs/bin/usvfs_proxy_x64.exe',
        'python-extension/usvfs/bin/usvfs_proxy_x86.exe'
    )
elif 'win32' in sys.argv:
    print('Building package for win32')
    binaries = (
        'python-extension/build/Release/Win32/_usvfs_dll.pyd',
        'python-extension/usvfs/bin/usvfs_x86.dll',
        'python-extension/usvfs/bin/usvfs_proxy_x64.exe',
        'python-extension/usvfs/bin/usvfs_proxy_x86.exe'
    )
else:
    print('Please specify target platform for package (x64/x86) in command line parameters')
    sys.exit(99)

copied = []

print('Copying required binaries...')
for fpath in binaries:
    copied.append(shutil.copy(fpath, 'python-module/usvfs'))  # Copy binaries, save destination path for cleanup

print('Build Python package...')


with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='py-usvfs',
    version='0.1.1',
    author='pwssnk',
    author_email='',
    description='Python bindings for the userspace virtual filesystem (usvfs) library',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/pwssnk/py-usvfs',
    package_dir={'': 'python-module'},
    packages=setuptools.find_packages(where='python-module'),
    include_package_data=True,
    package_data={
        'usvfs': ['*.dll', '*.exe', '*.pyd'],
    },
    zip_safe=False,
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: System :: Filesystems'
    ],
)

print('Cleaning previously copied binaries..')

for fpath in copied:
    os.remove(fpath)
