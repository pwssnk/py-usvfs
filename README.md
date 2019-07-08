# py-usvfs
Python bindings for the userspace virtual filesystem ([usvfs](https://github.com/ModOrganizer2/usvfs/)) library

### What is usvfs?
To quote the devs:
>USVFS (short for User Space Virtual File System) aims to allow windows applications to create file or directory links that are visible to only a select set of processes. It does so by using api hooking to fool file access functions into discovering/opening files that are in fact somewhere else

usvfs was originally written by [TanninOne](https://github.com/TanninOne/usvfs) as a part of [ModOrganizer](https://github.com/TanninOne/modorganizer), a mod manager application for various pc games (notably Bethesda titles). Development of ModOrganizer and usvfs was continued by the [ModOrganizer2](https://github.com/ModOrganizer2) team. 
usvfs is a core component of ModOrganizer. It is what allows ModOrganizer to easily install and uninstall mods without having to constantly move gigabytes of data on disk, and what gives it control over what happens when multiple mods override the same file.

However, usvfs was designed to also be usable as a standalone library. That's great, because this kind of functionality has a variety of interesting applications.

### What is py-usvfs?
usvfs is written in C++. It needs to be, because it needs to perform low level tasks like hooking Windows API I/O function calls and injecting processes. I saw use in usvfs for some personal projects, but I usually prefer to work in higher level languages -- Python first and foremost. py-usvfs aims to make that possible.

py-usvfs is two things:
a. Python bindings for the usvfs dll functionality, in the form of a pybind11 CPython extension
b. A Python wrapper module that provides convenient, hopefully more Pythonic abstractions for that low level functionality

Basically, it's intended to allow to use usvfs in python (a) and make using it less of a pain (b).

### Can I use this in a production environment?
Can you? Well, I'm not your mother. Should you? Probably not. usvfs is finicky, not always reliable and poorly documented. py-usvfs is no different. Caveat emptor.

Proper documentation for py-usvfs is on my to-do list, although it doesn't help that usvfs itself lacks proper documentation. For now, you'll have to resort to source code peeping.

## Requirements
Because usvfs works by hooking Windows API I/O function calls, it only runs on Windows machines. Consequently, py-usvfs only runs on Windows as well.
Becuase py-usvfs exposes the functionality in `usvfs_[x86|x64].dll` via a CPython extension, it will only run on the official CPython implementation of Python. 

The requirements therefore are:
* Windows OS (win32 or win-amd64)
* CPython 3.7.x (32-bits or 64-bits)


## Installation
### Install pre-built packages using pip
Pre-built Python packages are available from [PyPI](https://pypi.org/). Use pip to install.

```shell
pip install py-usvfs
```

Once installed, a Python module named `usvfs` will be available.

### Build it yourself
Alternatively, you can build the required components from source code. No detailed instructions given, but these are the basics steps:
1. Get usvfs source code from https://github.com/ModOrganizer2/usvfs/ 
2. Build `usvfs_dll` in Release/win32 and Release/x64 configurations using MSVC
3. Place the .dll files (`usvfs_x86.dll`, `usvfs_x64.dll`) in `python-extension/usvfs/bin`, place the .lib files (`usvfs_x86.lib`, `usvfs_x64.lib`) in `python-extension/usvfs/lib`, and place the usvfs proxy exe's (`usvfs_proxy_x64.exe`, `usvfs_proxy_x86.exe`) in `python-extension/usvfs/bin` (Note that even if you are only building for a single platform, you will alwyas need both the 32-bits and 64-bits usvfs_proxy exe's)
4. Build `python-extension` in Release/win32 and Release/x64 configurations using MSVC
5. Run `./build-wheels.bat` to build Python wheel packages for 64-bits and 32-bits CPython
6. You can now install the .whl files in `dist/` using `pip install [wheelname].whl`


## Basic usage
Suppose we have the following folder structure in our current working directory, and we wish to trick a program into thinking the contents of `src/` are located at `dest/`.

```
[current working directory]/
 |
 +-- src/
 |   |-- source1.txt
 |   |-- source2.txt
 |   |
 |   +-- subfolder/
 |       |-- source3.txt
 |
 +-- dest/
```

```python
import usvfs

# Define a virtual directory link rule
vdir = usvfs.VirtualDirectory('src/', 'dest/')  # If a process runnning 
                                                # in the vfs tries to access
                                                # dest/*, it will be redirected to src/*

# By default, py-usvfs links directories recursively, i.e. all underlying files 
# and directories of the source directory are linked automatically
# If this behaviour is undesired, you can unset the recursive link flag:
# vdir.link_recursively = False
# All link flags defined by usvfs can be set/unset in this way, but only 
# if they are relevant to the context (e.g. link_recursively is 
# only available for VirtualDirectory links, not VirtualFile links)

# Define our vfs layout
vfs_map = usvfs.Mapping()    # Create a vfs mapping. This is a collection 
                             # of virtual link rules that can be applied to the vfs
vfs_map.link(vdir)           # Add any VirtualDirectory and/or VirtualFile rules like this

# Set up the vfs
vfs = usvfs.UserspaceVFS()   # Create a usvfs controller with default instance name and configuration
vfs.initialize()             # Initialize it
vfs.set_mapping(vfs_map)     # Apply mapping

# Now we can start a process in the vfs
vfs.run_process('notepad.exe')  # Executable path + any command line arguments. 
                                # Optionally, you can specify a working directory as the second argument 
                                # (default = current working directory of your Python program)                                

# Usvfs will launch a usvfs_proxy process with the appropriate bitness, then 
# start and inject the specified process
# If you browse to dest/ in notepad, you should see the contents of src/
# If you then browse to dest/ in explorer, you will see that there are actually no files there!

# When you're done, be sure to clean up
vfs.close()
# You can do this whenever you want. If the process you started 
# hasn't finished yet, the usvfs_proxy will stay alive until it does
```

The Python wrapper classes hide some of the uglier usvfs wrangling in a clean, relatively easy to use API. If you want more low level access, you can call the usvfs dll (semi-)directly by accessing the functions defined in the `usvfs.dll` module.

```python
import usvfs  # Note that you cannot import usvfs.dll directly

# Access dll functions, properties, structs like this:
usvfs.dll.LINKFLAG_MONITORCHANGES
usvfs.dll.LogLevel
usvfs.dll.USVFSParameters()
usvfs.dll.CreateVFS(...)
# etc...
```
This exposes most functions, structs and properties exported by `usvfs_[x86|x64].dll` (but not the debugging stuff). The function signatures in Python are similar to those in the usvfs C++ headers, but you can pass basic Python types as arguments and you don't have to deal with buffer `wchar[]`'s. See the [usvfs header file](https://github.com/pwssnk/py-usvfs/blob/master/python-extension/usvfs/include/usvfs.h) for a list of the available functions and a (not particularly useful) explanation of what they do.

The exception here is `usvfs.dll.CreateProcessHooked()`. In C/C++ calls directly to the usvfs dll, you would have to pass a bunch of Windows API nonsense to the function and deal with Windows handles. The py-usvfs CPython extension takes care of that for you, because (a) it's convenient and (b) exposing all the required Windows API stuff to Python would be a pain. The downside is that you don't have easy access to the newly spawned process status and input/output via Windows handles.
`CreateProcessHooked()` in py-usvfs takes two arguments: a `str` containing executable path and any command line arguments to pass to it, and a `str` with a path to the intended working directory for the new process.


## License
(c) 2019 pwssnk -- Code available under GPL v3 license