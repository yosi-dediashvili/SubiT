#pragma once

#include <windows.h>
#include <shlobj.h>     // For IShellExtInit and IContextMenu
#include <list>
#include <string>
#include <iostream>

typedef std::list<WCHAR> wchar_wstring;

class FileContextMenuExt : public IShellExtInit, public IContextMenu
{
public:
	// IUnknown
	IFACEMETHODIMP QueryInterface(REFIID riid, void **ppv);
	IFACEMETHODIMP_(ULONG) AddRef();
	IFACEMETHODIMP_(ULONG) Release();

	// IShellExtInit
	IFACEMETHODIMP Initialize(LPCITEMIDLIST pidlFolder, LPDATAOBJECT pDataObj, HKEY hKeyProgID);

	// IContextMenu
	IFACEMETHODIMP QueryContextMenu(HMENU hMenu, UINT indexMenu, UINT idCmdFirst, UINT idCmdLast, UINT uFlags);
	IFACEMETHODIMP InvokeCommand(LPCMINVOKECOMMANDINFO pici);
	IFACEMETHODIMP GetCommandString(UINT_PTR idCommand, UINT uFlags, UINT *pwReserved, LPSTR pszName, UINT cchMax);
	
	FileContextMenuExt(void);

protected:
	~FileContextMenuExt(void);

private:
	// Reference count of component.
	long m_cRef;

	// The method that handles the "display" verb.
	void OnVerbDisplayFileName(HWND hWnd);

	// The function will build the parameter that should be passed to SubiT's
	// executable (by using the values in m_subit_files and m_subit_dirs), and 
	// return them.
	LPWSTR _buildSubitParameters();

	void _add_str_to_parameter_list(const wchar_t *);

	// The function will try to get the path of SubiT.exe file. If the file is
	// missing from the assumed path, the function return False, Otherwise, the
	// function will return True, and the path will be stored in the subit_path
	// parameter.
	BOOL _get_subit_executable_path(WCHAR subit_path[MAX_PATH]);

	LPWSTR m_subit_exeuctable_name;
	LPWSTR m_pszMenuText;
	HANDLE m_hSubitBmp;
	PCSTR m_pszVerb;
	PCWSTR m_pwszVerb;
	PCSTR m_pszVerbCanonicalName;
	PCWSTR m_pwszVerbCanonicalName;
	PCSTR m_pszVerbHelpText;
	PCWSTR m_pwszVerbHelpText;

	std::list<LPWSTR> m_subit_files;
	std::list<LPWSTR> m_subit_dirs;

	LPWSTR m_subit_mode_parameter;
	LPWSTR m_subit_dirs_parameter;
	LPWSTR m_subit_files_parameter; 

	std::wstring m_subit_paramter_to_pass;
};