
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

    :param real_path: Path to a real file or directory on disk. Relative paths will be converted to absolute paths
    using os.path.abspath().
    :type real_path: str

    :param virtual_path: Destination path at which real_path will be accessible in the vfs. Relative paths will be
    converted to absolute paths using os.path.abspath().
    :type virtual_path: str

    :param is_directory: Set to True if real_path points to a directory, set to False otherwise
    :type is_directory: bool

    :param link_flags: (unsigned) int bitflag (optional, default=0)
    :type link_flags: int
    """

    def __init__(self, real_path, virtual_path, is_directory, link_flags=0):
        self.real_path = os.path.abspath(real_path)
        self.virtual_path = os.path.abspath(virtual_path)
        self._is_directory = is_directory
        self.link_flags = link_flags

    @property
    def link_fail_if_exists(self):
        """
        Equivalent of LINKFLAG_FAILIFEXISTS.

        If this flag is set, linking fails in case of an error.

        Setting this property will automatically update link_flags property to the appropriate bitflag value.

        Getter
        :return: bool indicating whether flag is set
        :rtype: bool

        Setter
        :param value: True to set flag, False to unset flag
        :type value: bool
        """

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
        """
        Equivalent of LINKFLAG_CREATETARGET.

        If this flag is set, file creation (including move or copy) operations to
        the destination will be redirected to the source. Only one createtarget can be set for a destination folder
        so this flag will replace the previous create target. If  different create-target have been set for an element
        and one of its ancestors, the inner-most create-target is used.

        Setting this property will automatically update link_flags property to the appropriate bitflag value.


        Getter
        :return: bool indicating whether flag is set
        :rtype: bool

        Setter
        :param value: True to set flag, False to unset flag
        :type value: bool
        """

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
        """
        Indicates whether this VirtualLink object represents a directory (True) or a file (False).

        Property cannot be set after initialization.

        :return: bool indicating whether the VirtualLink object represents a directory or a file
        :rtype: bool
        """

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
    Use this to map a path to a real file on disk to a virtual path in the VFS. Processes running in the VFS that try
    to access the virtual path, will be redirected to the real path.

    :param real_path: Path to a real file on disk. Relative paths will be converted to absolute paths
    using os.path.abspath().
    :type real_path: str

    :param virtual_path: Destination path at which real_path will be accessible in the vfs. Relative paths will be
    converted to absolute paths using os.path.abspath().
    :type virtual_path: str
    """

    def __init__(self, real_path, virtual_path):
        super().__init__(real_path=real_path,
                         virtual_path=virtual_path,
                         is_directory=False)


class VirtualDirectory(_VirtualLink):
    """
    Class that represents a virtual link rule for a directory.
    Use this to map a path to a real directory on disk to a virtual path in the VFS. Files contained and subdirectories
    contained in the directory are linked recursively by default. (To disable recursive linking, set link_recursively
    property to False). Processes running in the VFS that try to access the virtual path, will be redirected to the real
    path.

    :param real_path: Path to a real directory on disk. Relative paths will be converted to absolute paths
    using os.path.abspath().
    :type real_path: str

    :param virtual_path: Destination path at which real_path will be accessible in the vfs. Relative paths will be
    converted to absolute paths using os.path.abspath().
    :type virtual_path: str
    """

    def __init__(self, real_path, virtual_path):
        super().__init__(real_path=real_path,
                         virtual_path=virtual_path,
                         is_directory=True)

        self.link_recursively = True

    @property
    def link_recursively(self):
        """
        Equivalent of LINKFLAG_RECURSIVE.

        If this flag is set, files and subdirectories are linked recursively.

        Setting this property will automatically update link_flags property to the appropriate bitflag value.


        Getter
        :return: bool indicating whether flag is set
        :rtype: bool

        Setter
        :param value: True to set flag, False to unset flag
        :type value: bool
        """

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
        """
        Equivalent of LINKFLAG_MONITORCHANGES.

        If this flag is set, changes to the source directory (real_path) after the link operation will be updated in
        the virtual filesystem.

        Setting this property will automatically update link_flags property to the appropriate bitflag value.


        Getter
        :return: bool indicating whether flag is set
        :rtype: bool

        Setter
        :param value: True to set flag, False to unset flag
        :type value: bool
        """

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
        """
        Add a virtual link rule to the vfs mapping instructions.

        :param virtual_link: a virtual link object
        :type virtual_link: Union[VirtualFile, VirtualDirectory, _VirtualLink]
        """

        if virtual_link.is_directory:
            self._dirs.append(virtual_link)
        else:
            self._files.append(virtual_link)

    def directories(self):
        """
        Generator that returns all virtual directory links that have been specified in this mapping.

        :return: previously registered VirtualDirectory objects
        :rtype: Iterable[VirtualDirectory]
        """

        for d in self._dirs:
            yield d

    def files(self):
        """
        Generator that returns all virtual file links that have been specified in this mapping.

        :return: previously registered VirtualFile objects
        :rtype: Iterable[VirtualFile]
        """

        for f in self._files:
            yield f


class UserspaceVFS:
    """
    Class representing a virtual filesystem.

    UserspaceVFS is a pseudo-singleton, in the sense that is does not allow more than instance of the class to use
    a given instance name. This is because usvfs uses these as a unique identifier.

    :param instance_name: the instance name which usvfs uses internally, which has a maximum length of 64 characters
    (optional, default='pyusvfs_instance')
    :type instance_name: str

    :param debug_mode: whether to initialze usvfs in debugging mode (optional, default=False)
    :type debug_mode: bool

    :param log_level: level of detail for usvfs library internal logging (optional, default=LogLevel.ERROR)
    :type log_level: usvfs.dll.LogLevel

    :param crash_dumps_type: type of crash dump in case of usvfs library crash(optional, default=CrashDumpsType.NONE)
    :type crash_dumps_type: usvfs.dll.CrashDumpsType

    :param crash_dump_path: path to file for saving crash dump contents (optional, default='')
    :type crash_dump_path: str

    :raises USVFSException: if there is a possible conflict between usvfs instance names, or if instance name exceeds
    the maximum length of 64 characters.
    """

    _instance_names = []

    # 'Internal' methods
    def __init__(self, instance_name='pyusvfs_instance', debug_mode=False, log_level=dll.LogLevel.ERROR,
                 crash_dumps_type=dll.CrashDumpsType.NONE, crash_dump_path=''):

        if instance_name in self._instance_names:
            raise USVFSException('A usvfs instance with that instance name already exists!')
        else:
            self._instance_names.append(instance_name)

        if len(instance_name) > 64:
            raise USVFSException('Instance names may not exceed 64 characters')

        self._initialized = False

        self._parameters = dll.USVFSParameters()

        dll.USVFSInitParameters(self._parameters, instance_name, debug_mode, log_level, crash_dumps_type,
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
        """
        Initialize the virtual filesystem instance.

        :raises USVFSException: if the vfs is already initialized, or if vfs fails to initialize
        """

        if self._initialized:
            raise USVFSException('VFS is already initialized')
        else:
            dll.InitLogging(self._parameters.debugMode)  # If debug_mode is True, log to console. (No separate setting)
            success = dll.CreateVFS(self._parameters)

            if success:
                self._initialized = True
            else:
                raise USVFSException('Failed to initialize VFS - try enabling debugging')

    def close(self):
        """
        Disconnect from the usvfs dll and clean up any active hooks.

        :raises USVFSException: if vfs is not initialized
        """
        if not self._initialized:
            raise USVFSException('VFS is not initialized')
        else:
            dll.DisconnectVFS()
            self._initialized = False

    def is_active_instance(self):
        """
        Indicates whether this virtual filesystem instance is the one that is currently connected to the usvfs library.
        The usvfs dll can spawn multiple vfs instances, but you can only be connected as a controller to one instance
        at a time.

        :return: bool indicating whether this vfs instance is currently the active instance
        :rtype: bool
        """

        if not self._initialized:
            return False

        return dll.GetCurrentVFSName().startswith(self.instance_name)

    def set_mapping(self, mapping):
        """
        Apply a virtual link mapping to the vfs.

        :param mapping: a Mapping object specifying the virtual link mapping
        :type mapping: Mapping

        :raises USVFSException: if vfs is not initialized
        """

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
        """
        Clear existing virtual link mapping.

        :raises USVFSException: if vfs is not initialized
        """

        if not self._initialized:
            raise USVFSException('VFS is not initialized')

        self._ensure_active_instance()

        dll.ClearVirtualMappings()

    def blacklist_executable(self, executable_name):
        """
        Blacklists the given executable, so it doesn't get exposed to the virtual file system.
        This is useful if a vfs-exposed process launches a child process that should not run in the vfs.

        :param executable_name: the name of the executable to blacklist
        :type executable_name: str
        """

        self._ensure_active_instance()
        dll.BlacklistExecutable(executable_name)

    def clear_blacklist(self):
        """
        Clear any previously blacklisted executables.
        """

        self._ensure_active_instance()
        dll.ClearExecutableBlacklist()

    def force_load_lib(self, process_name, library_path):
        """
        Force load the a library when the given process is started in the vfs (and injected by usvfs).

        :param process_name: the name of the process to force load the library into
        :type process_name: str

        :param library_path: path to the library. relative paths will be converted to absolute paths using
        os.path.abspath()
        :type library_path: str
        """

        libpath = os.path.abspath(library_path)

        self._ensure_active_instance()

        dll.ForceLoadLibrary(process_name, libpath)

    def clear_force_loads(self):
        """
        Clear any previously specified library force load instructions.
        """

        self._ensure_active_instance()
        dll.ClearLibraryForceLoads()

    def run_process(self, command_line, working_directory=os.getcwd()):
        """
        Start a process (command line style) that is exposed the virtual filesystem.

        :param command_line: a single string containing the path to the executable and, optionally, command line
        arguments to pass to the program
        :type command_line: str

        :param working_directory: path to the intended working directory for the process (optional, default=os.getcwd())
        :type working_directory: str

        :raises USVFSException: if usvfs failed to launch the process
        """

        working_directory = os.path.abspath(working_directory)

        self._ensure_active_instance()

        success = dll.CreateProcessHooked(command_line, working_directory)

        if not success:
            raise USVFSException('Failed to start process - try enabling debugging')

    def get_active_processes(self):
        """
        Get a list of processes that are currently running in the vfs by process id.

        :return: a list containing the process id's of processes running in the vfs
        :rtype: list[int]
        """

        self._ensure_active_instance()

        return dll.GetVFSProcessList()

    @property
    def instance_name(self):
        """
        Get the instance name of this virtual filesystem.

        Property cannot be set after initialization.

        :return:
        """

        return self._parameters.instanceName

    @property
    def initialized(self):
        """
        Indicates whether the virtual filesystem has been initialized.

        Property cannot be set by user.

        :return: bool indicating whether the vfs has been initialized
        :rtype: bool
        """

        return self._initialized
