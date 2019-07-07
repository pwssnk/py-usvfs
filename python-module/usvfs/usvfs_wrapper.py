
import os.path
import usvfs._usvfs_dll as dll


class USVFSException(Exception):
    """
    Generic exception for errors related to the usvfs library.
    """

    pass


class _VirtualLink:
    """
    Base class for virtual link rules.
    """

    def __init__(self, real_path, virtual_path, is_directory, link_flags=0):
        self.real_path = os.path.abspath(real_path)
        self.virtual_path = os.path.abspath(virtual_path)
        self._is_directory = is_directory
        self.link_flags = link_flags

    @property
    def link_fail_if_exists(self):
        return (self.link_flags & dll.LINKFLAG_FAILIFEXISTS) != 0

    @link_fail_if_exists.setter
    def link_fail_if_exists(self, value):
        if type(value) is not bool:
            raise TypeError('Property must be a bool')

        if self.link_fail_if_exists == value:
            return  # Link flag is already set to value!

        if value:
            self.link_flags |= dll.LINKFLAG_FAILIFEXISTS    # Set flag
        else:
            self.link_flags &= ~dll.LINKFLAG_FAILIFEXISTS   # Unset flag

    @property
    def redirect_create(self):
        return (self.link_flags & dll.LINKFLAG_CREATETARGET) != 0

    @redirect_create.setter
    def redirect_create(self, value):
        if type(value) is not bool:
            raise TypeError('Property must be a bool')

        if self.redirect_create == value:
            return  # Link flag is already set to value!

        if value:
            self.link_flags |= dll.LINKFLAG_CREATETARGET    # Set flag
        else:
            self.link_flags &= ~dll.LINKFLAG_CREATETARGET   # Unset flag

    @property
    def is_directory(self):
        return self._is_directory

    @is_directory.setter
    def is_directory(self, value):
        # Don't allow setting in subclass, so user can't mess it up
        if not isinstance(self, type(_VirtualLink)):
            raise AttributeError('Property is_directory cannot be set')

        if type(value) is not bool:
            raise TypeError('Property must be a bool')

        self._is_directory = value


class VirtualFile(_VirtualLink):
    """
    Class that represents a virtual link rule for a file.
    Use this to map a path to a real file on disk to a virtual path in the VFS.
    Processes running in the VFS that try to access the virtual path, will be redirected to the real path.
    """

    def __init__(self, real_path, virtual_path):
        super().__init__(real_path=real_path,
                         virtual_path=virtual_path,
                         is_directory=False)


class VirtualDirectory(_VirtualLink):
    """
    Class that represents a virtual link rule for a directory.
    Use this to map a path to a real directory (optionally including subdirectories) on disk to a virtual
    path in the VFS.
    Processes running in the VFS that try to access the virtual path, will be redirected to the real path.
    """

    def __init__(self, real_path, virtual_path):
        super().__init__(real_path=real_path,
                         virtual_path=virtual_path,
                         is_directory=True)

        self.link_recursively = True

    @property
    def link_recursively(self):
        return (self.link_flags & dll.LINKFLAG_RECURSIVE) != 0

    @link_recursively.setter
    def link_recursively(self, value):
        if type(value) is not bool:
            raise TypeError('Property must be a bool')

        if self.link_recursively == value:
            return  # Link flag is already set to value!

        if value:
            self.link_flags |= dll.LINKFLAG_RECURSIVE  # Set flag
        else:
            self.link_flags &= ~dll.LINKFLAG_RECURSIVE  # Unset flag

    @property
    def monitor_changes(self):
        return (self.link_flags & dll.LINKFLAG_MONITORCHANGES) != 0

    @monitor_changes.setter
    def monitor_changes(self, value):
        if type(value) is not bool:
            raise TypeError('Property must be a bool')

        if self.monitor_changes == value:
            return  # Link flag is already set to value!

        if value:
            self.link_flags |= dll.LINKFLAG_MONITORCHANGES  # Set flag
        else:
            self.link_flags &= ~dll.LINKFLAG_MONITORCHANGES  # Unset flag


class Mapping:
    """
    Class that represents a collection of virtual link rules.
    This is used to define layout (redirection tree) of a VFS using UserspaceVFS.set_mapping(mapping).
    """

    def __init__(self):
        self._dirs = []
        self._files = []

    def link(self, virtual_link):
        if virtual_link.is_directory:
            self._dirs.append(virtual_link)
        else:
            self._files.append(virtual_link)

    def directories(self):
        for d in self._dirs:
            yield d

    def files(self):
        for f in self._files:
            yield f


class UserspaceVFS:
    _instance_names = []

    # 'Internal' methods
    def __init__(self, instance_name='pyusvfs_instance', debug_mode=False, log_level=dll.LogLevel.ERROR,
                 crash_dump_type=dll.CrashDumpsType.NONE, crash_dump_path=''):

        if instance_name in self._instance_names:
            raise USVFSException('A usvfs instance with that instance name already exists!')
        else:
            self._instance_names.append(instance_name)

        self._initialized = False

        self._parameters = dll.USVFSParameters()

        dll.USVFSInitParameters(self._parameters, instance_name, debug_mode, log_level, crash_dump_type,
                                crash_dump_path)

    def __del__(self):
        if self._initialized:
            dll.DisconnectVFS()  # Ensure DLL cleanup gets called

    def _ensure_active_instance(self):
        if not self.is_active_instance():
            # We are not the active instance -- try to reconnect
            if not dll.ConnectVFS(self._parameters):
                raise USVFSException('Could not connect to VFS')

    # 'Public' methods
    def initialize(self):
        if self._initialized:
            raise USVFSException('VFS is already initialized')
        else:
            dll.InitLogging(self._parameters.debugMode)  # If debug_mode is True, log to console. (No separate setting)
            success = dll.CreateVFS(self._parameters)

            if success:
                self._initialized = True
            else:
                raise USVFSException('Failed to initialize VFS - try enabling debugging')

    def set_mapping(self, mapping):
        if not isinstance(mapping, Mapping):
            raise TypeError('Argument for parameter \'mapping\' must be an instance of Mapping class')

        if not self._initialized:
            raise USVFSException('VFS is not initialized')

        self._ensure_active_instance()

        # Clear any existing mappings
        dll.ClearVirtualMappings()

        # Apply new mappings
        for d in mapping.directories():
            success = dll.VirtualLinkDirectoryStatic(d.real_path, d.virtual_path, d.link_flags)

            if not success:
                raise USVFSException('''Failed to link virtual directory\nreal path: {}\nvirtual path: {}\nflags: {}'''
                                     .format(d.real_path, d.virtual_path, d.link_flags))

        for f in mapping.files():
            success = dll.VirtualLinkFile(f.real_path, f.virtual_path, f.link_flags)

            if not success:
                raise USVFSException('''Failed to link virtual file\nreal path: {}\nvirtual path: {}\nflags: {}'''
                                     .format(f.real_path, f.virtual_path, f.link_flags))

    def clear_mapping(self):
        if not self._initialized:
            raise USVFSException('VFS is not initialized')

        self._ensure_active_instance()

        dll.ClearVirtualMappings()

    def run_process(self, command_line, working_directory=os.getcwd()):
        working_directory = os.path.abspath(working_directory)

        self._ensure_active_instance()

        success = dll.CreateProcessHooked(command_line, working_directory)

        if not success:
            raise USVFSException('Failed to start process - try enabling debugging')

    def close(self):
        if not self._initialized:
            raise USVFSException('VFS is not initialized')
        else:
            dll.DisconnectVFS()
            self._initialized = False

    def is_active_instance(self):
        if not self._initialized:
            return False

        return dll.GetCurrentVFSName().startswith(self.instance_name)

    @property
    def instance_name(self):
        return self._parameters.instanceName

    @property
    def initialized(self):
        return self._initialized
