#define NOMINMAX

#include <string>
#include <vector>
#include <Windows.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "usvfs.h"
#include "usvfsparameters.h"


namespace py = pybind11;
using namespace std;


/*
	usvfs wrapper functions
*/
void PyClearVirtualMappings()
{
	ClearVirtualMappings();
}

bool PyVirtualLinkFile(const wstring& source, const wstring& destination, unsigned int flags)
{
	return (bool)VirtualLinkFile(source.c_str(), destination.c_str(), flags);
}

bool PyVirtualLinkDirectoryStatic(const wstring& source, const wstring& destination, unsigned int flags)
{
	return (bool)VirtualLinkDirectoryStatic(source.c_str(), destination.c_str(), flags);
}

bool PyConnectVFS(const USVFSParameters& parameters)
{
	return (bool)ConnectVFS(&parameters);
}

bool PyCreateVFS(const USVFSParameters& parameters)
{
	return (bool)CreateVFS(&parameters);
}

void PyDisconnectVFS()
{
	DisconnectVFS();
}

string PyGetCurrentVFSName()
{
	char buf[64];
	size_t bufSize = sizeof(buf);

	GetCurrentVFSName(buf, bufSize);

	string ret(buf, bufSize);

	// Remove trailing null bytes
	ret.erase(find(ret.begin(), ret.end(), '\0'), ret.end());

	return ret;
}

vector<unsigned long> PyGetVFSProcessList()
{
	unsigned long processes[64];		// 64 should be enough... right? Who would need that many processes?
	size_t count = sizeof(processes);	// Shoud be 64 always, but whatever

	GetVFSProcessList(&count, processes);

	vector<unsigned long> ret(processes, processes + count);

	return ret;
}

bool PyCreateProcessHooked(wstring& commandLineArguments, wstring& fullPathToWorkingDir)
{
	/*
		Paramaters for usvfs' CreateProcessHooked are the same as Windows' CreateProcess. See:
		https://docs.microsoft.com/en-us/windows/desktop/api/processthreadsapi/nf-processthreadsapi-createprocessa
		https://docs.microsoft.com/nl-nl/windows/desktop/ProcThread/creating-processes

		!!! WARNING: STARTUPINFO and PROCESS_INFORMATION Handles MUST be closed with CloseHandle when they are no longer needed !!!
	*/

	STARTUPINFO si;
	ZeroMemory(&si, sizeof(si));
	si.cb = sizeof(si);

	PROCESS_INFORMATION pi;
	ZeroMemory(&pi, sizeof(pi));
	

	BOOL result = CreateProcessHooked(
		NULL,                                               // LPCWSTR lpApplicationName
		&commandLineArguments[0], // <- that's disgusting   // LPWSTR lpCommandLine
		NULL,                                               // LPSECURITY_ATTRIBUTES lpProcessAttributes
		NULL,                                               // lPSECURITY_ATTRIBUTES lpThreadAttribute
		FALSE,                                              // BOOL bInheritHandles
		CREATE_BREAKAWAY_FROM_JOB,                          // WORD dwCreationFlags
		NULL,                                               // LPVOID lpEnvironment
		fullPathToWorkingDir.c_str(),                       // LPCWSTR lpCurrentDirectory
		&si,                                                // LPSTARTUPINFOW lpStartupInfo
		&pi                                                 // LPPROCESS_INFORMATION lpProcessInformation
	);

	// Close handles right away, won't be using them
	CloseHandle(si.hStdError);
	CloseHandle(si.hStdInput);
	CloseHandle(si.hStdOutput);
	
	CloseHandle(pi.hThread);
	CloseHandle(pi.hProcess);

	return (bool)result;
}

void PyBlacklistExecutable(const wstring& executableName)
{
	vector<wchar_t> buffer(executableName.begin(), executableName.end());
	buffer.push_back(NULL); // Null-terminated buffer

	BlacklistExecutable(buffer.data());
}

void PyClearExecutableBlacklist()
{
	ClearExecutableBlacklist();
}

void PyForceLoadLibrary(const wstring& processName, const wstring& libraryPath)
{
	vector<wchar_t> pBuf(processName.begin(), processName.end());
	pBuf.push_back(NULL);	// Null-terminated buffer
	vector<wchar_t> lBuf(libraryPath.begin(), libraryPath.end());
	lBuf.push_back(NULL);	// Null-terminated buffer

	ForceLoadLibrary(pBuf.data(), lBuf.data());
}

void PyClearLibraryForceLoads()
{
	ClearLibraryForceLoads();
}

void PyUVFSInitParameters(USVFSParameters& params, const string& instanceName, bool debugMode, LogLevel logLevel,
						  CrashDumpsType crashDumpsType, const string& crashDumpsPath)
{
	USVFSInitParameters(&params, instanceName.c_str(), debugMode, logLevel, crashDumpsType, crashDumpsPath.c_str());
}

void PyInitLogging(bool toLocal = false)
{
	InitLogging(toLocal);
}


/*
	Export Python module
*/
PYBIND11_MODULE(_usvfs_dll, m) {
	m.doc() = "Python bindings for the userspace virtual file system (usvfs) dll library.";

	// Export LogLevel enum
	py::enum_<LogLevel>(m, "LogLevel")
		.value("INFO", LogLevel::Info)
		.value("DEBUG", LogLevel::Debug)
		.value("ERROR", LogLevel::Error)
		.value("WARNING", LogLevel::Warning);

	// Export CrashDumptsType enum
	py::enum_<CrashDumpsType>(m, "CrashDumpsType")
		.value("FULL", CrashDumpsType::Full)
		.value("MINI", CrashDumpsType::Mini)
		.value("DATA", CrashDumpsType::Data)
		.value("NONE", CrashDumpsType::None);

	// Export USVFSParameters struct
	py::class_<USVFSParameters>(m, "USVFSParameters")
		.def(py::init<>())
		.def_readonly("instanceName", &USVFSParameters::instanceName)
		.def_readonly("currentSHMName", &USVFSParameters::currentSHMName)
		.def_readonly("currentInverseSHMName", &USVFSParameters::currentInverseSHMName)
		.def_readonly("debugMode", &USVFSParameters::debugMode)
		.def_readonly("logLevel", &USVFSParameters::logLevel)
		.def_readonly("crashDumpsType", &USVFSParameters::crashDumpsType)
		.def_readonly("crashDumpsPath", &USVFSParameters::crashDumpsPath);

	// Export functions
	m.def("USVFSInitParameters", &PyUVFSInitParameters, py::arg("parameters"), py::arg("instanceName"), 
		  py::arg("debugMode"), py::arg("logLevel"), py::arg("crashDumpsType"), py::arg("crashDumpsPath"));

	m.def("InitLogging", &PyInitLogging, py::arg("toLocal"));

	m.def("CreateVFS", &PyCreateVFS, py::arg("parameters"));

	m.def("ConnectVFS", &PyConnectVFS, py::arg("parameters"));

	m.def("DisconnectVFS", &PyDisconnectVFS);

	m.def("VirtualLinkDirectoryStatic", &PyVirtualLinkDirectoryStatic, py::arg("source"),
		  py::arg("destination"), py::arg("flags") = 0);

	m.def("VirtualLinkFile", &PyVirtualLinkFile, py::arg("source"),
		py::arg("destination"), py::arg("flags") = 0);

	m.def("ClearVirtualMappings", &PyClearVirtualMappings);

	m.def("CreateProcessHooked", &PyCreateProcessHooked, py::arg("commandLineArgs"),
		   py::arg("fullPathToWorkingDir"));
		   
	m.def("GetCurrentVFSName", &PyGetCurrentVFSName);

	m.def("GetVFSProcessList", &PyGetVFSProcessList);

	m.def("BlacklistExecutable", &PyBlacklistExecutable, py::arg("executableName"));

	m.def("ClearExecutableBlacklist", &PyClearExecutableBlacklist);

	m.def("ForceLoadLibrary", &PyForceLoadLibrary,
		  py::arg("processName"), py::arg("libraryPath"));

	m.def("ClearLibraryForceLoads", &PyClearLibraryForceLoads);

	// Export flag constants
	m.attr("LINKFLAG_FAILIFEXISTS") = LINKFLAG_FAILIFEXISTS;
	m.attr("LINKFLAG_CREATETARGET") = LINKFLAG_CREATETARGET;
	m.attr("LINKFLAG_MONITORCHANGES") = LINKFLAG_MONITORCHANGES;
	m.attr("LINKFLAG_RECURSIVE") = LINKFLAG_RECURSIVE;
}