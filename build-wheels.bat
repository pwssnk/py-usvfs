@echo off

python setup.py bdist_wheel --plat-name win32 --python-tag cp37
python setup.py bdist_wheel --plat-name win_amd64 --python-tag cp37

:clean
set "reply=y"
set /p "reply=Clean build files? [y|n]: "
if /i not "%reply%" == "y" goto :end

echo Remove build directory...
RMDIR /S /Q "build"

echo Remove egg-info...
RMDIR /S /Q "python-module\\py_usvfs.egg-info"

:end
echo ** DONE **
PAUSE