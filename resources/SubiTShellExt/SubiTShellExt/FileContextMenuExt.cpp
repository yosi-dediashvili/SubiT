#include "FileContextMenuExt.h"
#include <strsafe.h>
#include <Shlwapi.h>
#include "resource.h"

#pragma comment(lib, "shlwapi.lib")

extern HINSTANCE g_DllModuleHInstance;
extern long g_cDllRef;

#define IDM_DISPLAY             0  // The command's identifier offset

FileContextMenuExt::FileContextMenuExt(void) : m_cRef(1), 
	m_pszMenuText(L"&SubiT"),
	m_pszVerb("SubiT_ExecuteFromContextMenuHandler"),
	m_pwszVerb(L"SubiT_ExecuteFromContextMenuHandler"),
	m_pwszVerbCanonicalName(L"SubiT"),
	m_pwszVerbHelpText(L"Download subtitle for the selected files."),
	m_subit_mode_parameter(L"-mode"),
	m_subit_dirs_parameter(L"-dirs"),
	m_subit_files_parameter(L"-files"),
	m_subit_exeuctable_name(L"SubiT.exe")
{
	InterlockedIncrement(&g_cDllRef);

	m_hSubitBmp = LoadImage(
		g_DllModuleHInstance, 
		MAKEINTRESOURCE(IDB_SUBIT_BMP),
		IMAGE_BITMAP, 
		NULL, 
		NULL, 
		LR_DEFAULTSIZE | LR_LOADTRANSPARENT | LR_LOADMAP3DCOLORS);
}

FileContextMenuExt::~FileContextMenuExt(void)
{
	if (m_hSubitBmp)
	{
		DeleteObject(m_hSubitBmp);
		m_hSubitBmp = NULL;
	}

	InterlockedDecrement(&g_cDllRef);
}


void FileContextMenuExt::OnVerbDisplayFileName(HWND hWnd)
{
	this->_buildSubitParameters();

	LPWSTR subit_path = new WCHAR[MAX_PATH];
	if (!_get_subit_executable_path(subit_path)){
		MessageBox(
			hWnd, 
			L"The executable file of SubiT is missing from SubiT's root directory.",
			L"SubiT.exe is missing", 
			MB_OK | MB_ICONERROR);
		return;
	}

	LPWSTR subit_dir = new WCHAR[sizeof(subit_path) / sizeof(WCHAR) + sizeof(WCHAR)];
	StringCchCopy(subit_dir, sizeof(subit_path) / sizeof(WCHAR) + sizeof(WCHAR), subit_path);

	PathRemoveFileSpec(subit_dir);
	
	STARTUPINFO subit_startup_info;
	ZeroMemory(&subit_startup_info, sizeof(subit_startup_info));
	subit_startup_info.cb = sizeof(subit_startup_info);

	PROCESS_INFORMATION subit_process_info;
	ZeroMemory(&subit_process_info, sizeof(subit_process_info));

	const LPWSTR subit_cmd_line = 
		const_cast<const LPWSTR>(this->m_subit_paramter_to_pass.c_str());

	CreateProcess(
		subit_path,
		subit_cmd_line,
		NULL,
		NULL,
		FALSE,
		NULL,
		NULL,
		subit_dir, 
		&subit_startup_info,
		&subit_process_info);
	
	DWORD subit_exit_code;
	LPWSTR error_title = L"SubiT Failed";

	if (!GetExitCodeProcess(subit_process_info.hProcess, &subit_exit_code)){
		DWORD last_error = GetLastError();
		LPTSTR error = NULL;
		FormatMessage(
			FORMAT_MESSAGE_FROM_SYSTEM | 
			FORMAT_MESSAGE_ALLOCATE_BUFFER | 
			FORMAT_MESSAGE_IGNORE_INSERTS,
			NULL,
			last_error,
			MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT),
			(LPTSTR)&error,
			0,
			NULL);
		if (NULL != error){
			MessageBox(
				hWnd, 
				error, 
				error_title, 
				MB_OK | MB_ICONERROR);
		}
		else {
			MessageBox(
				hWnd, 
				L"SubiT failed and we can't even get the failure reason.", 
				error_title, 
				MB_OK | MB_ICONERROR);
		}
	}
	else{
		if(subit_exit_code != STILL_ACTIVE){			
			LPTSTR error_message;
			FormatMessage(
				FORMAT_MESSAGE_FROM_SYSTEM | 
				FORMAT_MESSAGE_ALLOCATE_BUFFER | 
				FORMAT_MESSAGE_IGNORE_INSERTS,
				NULL,
				subit_exit_code,
				MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT),
				(LPTSTR)&error_message,
				0,
				NULL);
			
			LPWSTR message;
			if(NULL == error_message){
				message = L"Calling SubiT resulted in an unknown error.";
			}
			else{
				std::wstring message_string;
				message_string += L"Calling SubiT resulted in an error: \r\n";
				message_string += error_message;
				message = const_cast<LPWSTR>(message_string.c_str());
			}

			MessageBox(hWnd, message, error_title, MB_OK | MB_ICONERROR);
		}
	}
}


#pragma region IUnknown

// Query to the interface the component supported.
IFACEMETHODIMP FileContextMenuExt::QueryInterface(REFIID riid, void **ppv)
{
	static const QITAB qit[] = 
	{
		QITABENT(FileContextMenuExt, IContextMenu),
		QITABENT(FileContextMenuExt, IShellExtInit), 
		{ 0 },
	};
	return QISearch(this, qit, riid, ppv);
}

// Increase the reference count for an interface on an object.
IFACEMETHODIMP_(ULONG) FileContextMenuExt::AddRef()
{
	return InterlockedIncrement(&m_cRef);
}

// Decrease the reference count for an interface on an object.
IFACEMETHODIMP_(ULONG) FileContextMenuExt::Release()
{
	ULONG cRef = InterlockedDecrement(&m_cRef);
	if (0 == cRef)
	{
		delete this;
	}

	return cRef;
}

#pragma endregion


#pragma region IShellExtInit

// Initialize the context menu handler.
IFACEMETHODIMP FileContextMenuExt::Initialize(
	LPCITEMIDLIST pidlFolder, 
	LPDATAOBJECT pDataObj, 
	HKEY hKeyProgID)
{
	if (NULL == pDataObj)
	{
		return E_INVALIDARG;
	}

	HRESULT hr = E_FAIL;

	FORMATETC fe = { CF_HDROP, NULL, DVASPECT_CONTENT, -1, TYMED_HGLOBAL };
	STGMEDIUM stm;

	// The pDataObj pointer contains the objects being acted upon. In this 
	// example, we get an HDROP handle for enumerating the selected files and 
	// folders.
	if (SUCCEEDED(pDataObj->GetData(&fe, &stm))) {
		// Get an HDROP handle.
		HDROP hDrop = static_cast<HDROP>(GlobalLock(stm.hGlobal));
		if (hDrop != NULL) {
			// When DragQueryFile recieves 0xFFFFFFFF as the file id, it 
			// returns the number of files or dirs that was selected.
			UINT number_of_files = DragQueryFile(hDrop, 0xFFFFFFFF, NULL, 0);
			
			for (UINT i_path = 0; i_path < number_of_files; i_path++) {
				// When DragQueryFile recieves any other file id, it returns 
				// the number of characters that was stored in the file name
				// buffer that was passed to it.
				WCHAR * current_path = new WCHAR[MAX_PATH];
				if (NULL != DragQueryFile(hDrop, i_path, current_path, MAX_PATH))
					if (PathIsDirectory(current_path))
						this->m_subit_dirs.push_back(current_path);
					// We're passing SubiT all the files that passed to us. 
					// You should notice that these files are not movie 
					// files for sure because if the user selects other 
					// file types along with movie files, and right-clicks 
					// them when the mouse is over a movie file, and not 
					// other file, then we will apear in the context menu 
					// (SubiT will later filter out the files that are not 
					// movie files).
					else this->m_subit_files.push_back(current_path);
			}			
			hr = ERROR_SUCCESS;
			GlobalUnlock(stm.hGlobal);
		}
		ReleaseStgMedium(&stm);
	}
	// If any value other than S_OK is returned from the method, the context 
	// menu item is not displayed.
	return hr;
}

#pragma endregion


#pragma region IContextMenu

//
//   FUNCTION: FileContextMenuExt::QueryContextMenu
//
//   PURPOSE: The Shell calls IContextMenu::QueryContextMenu to allow the 
//            context menu handler to add its menu items to the menu. It 
//            passes in the HMENU handle in the hmenu parameter. The 
//            indexMenu parameter is set to the index to be used for the 
//            first menu item that is to be added.
//
IFACEMETHODIMP FileContextMenuExt::QueryContextMenu(
	HMENU hMenu, UINT indexMenu, UINT idCmdFirst, UINT idCmdLast, UINT uFlags)
{
	// If uFlags include CMF_DEFAULTONLY then we should not do anything.
	if (CMF_DEFAULTONLY & uFlags)
	{
		return MAKE_HRESULT(SEVERITY_SUCCESS, 0, USHORT(0));
	}
	
	MENUITEMINFO subit_menu_item = { sizeof(subit_menu_item) };
	subit_menu_item.fMask = MIIM_STRING | MIIM_ID | MIIM_BITMAP;
	subit_menu_item.wID = idCmdFirst;
	subit_menu_item.dwTypeData = m_pszMenuText;
	subit_menu_item.hbmpItem = (HBITMAP)m_hSubitBmp;

	if (!InsertMenuItem(hMenu, indexMenu, TRUE, &subit_menu_item))
	{
		return HRESULT_FROM_WIN32(GetLastError());
	}

	// Add a separator.
	MENUITEMINFO sep = { sizeof(sep) };
	sep.fMask = MIIM_TYPE;
	sep.fType = MFT_SEPARATOR;
	if (!InsertMenuItem(hMenu, indexMenu + 1, TRUE, &sep))
	{
		return HRESULT_FROM_WIN32(GetLastError());
	}

	// We pass the menu sum of item + the separator is the return value
	return MAKE_HRESULT(SEVERITY_SUCCESS, 0, 2);
}

BOOL FileContextMenuExt::_get_subit_executable_path(WCHAR subit_path[MAX_PATH])
{
	LPWSTR current_path = new WCHAR[MAX_PATH];
	if(NULL == GetModuleFileName(g_DllModuleHInstance, current_path, MAX_PATH)){
		return FALSE;
	}

	// The dll should be in: <subit_root>\Settings\Associators\WinAssociator\[32\64]\<dll_name>
	// In order to get to SubiT's root directory, we need to go 5 directories up.

	for (int dirs_to_go_up = 5; dirs_to_go_up > 0; dirs_to_go_up--){
		PathRemoveFileSpec(current_path);
	}

	if(NULL != PathCombine(subit_path, current_path, m_subit_exeuctable_name)){
		return PathFileExists(subit_path);
	}

	return FALSE;
}

void FileContextMenuExt::_add_str_to_parameter_list(const wchar_t * str)
{
	this->m_subit_paramter_to_pass += str;
}

inline std::wstring _format_parameter(
	LPWSTR str, 
	BOOL add_spaces, 
	BOOL add_quotation_marks)
{
	std::wstring wstr;
	if (add_spaces)
		wstr += L" ";
	if (add_quotation_marks)
		wstr += L"\"";

	wstr += str;

	if (add_quotation_marks)
		wstr += L"\"";
	if (add_spaces)
		wstr += L" ";

	return wstr;
}

LPWSTR FileContextMenuExt::_buildSubitParameters()
{
	// Write the mode parameter.
	_add_str_to_parameter_list(
		_format_parameter(this->m_subit_mode_parameter, TRUE, FALSE).c_str());
	_add_str_to_parameter_list(
		_format_parameter(L"BY-CONFIG", TRUE, FALSE).c_str());

	// Write the files parameter
	if (!this->m_subit_files.empty()){
		_add_str_to_parameter_list(
			_format_parameter(this->m_subit_files_parameter, TRUE, FALSE).c_str());
		for(std::list<LPWSTR>::iterator i_file = this->m_subit_files.begin(); 
			i_file != this->m_subit_files.end();
			i_file++){
			_add_str_to_parameter_list(
				_format_parameter((*i_file), TRUE, TRUE).c_str());
		}
	}

	// Write the dirs parameter
	if (!this->m_subit_dirs.empty()){
		_add_str_to_parameter_list(
			_format_parameter(this->m_subit_dirs_parameter, TRUE, FALSE).c_str());
		for(std::list<LPWSTR>::iterator i_dir = this->m_subit_dirs.begin(); 
			i_dir != this->m_subit_dirs.end();
			i_dir++) {
			_add_str_to_parameter_list(
				_format_parameter((*i_dir), TRUE, TRUE).c_str());
		}
	}

	return const_cast<LPWSTR>(this->m_subit_paramter_to_pass.c_str());
}

//
//   FUNCTION: FileContextMenuExt::InvokeCommand
//
//   PURPOSE: This method is called when a user clicks a menu item to tell 
//            the handler to run the associated command. The lpcmi parameter 
//            points to a structure that contains the needed information.
//
IFACEMETHODIMP FileContextMenuExt::InvokeCommand(LPCMINVOKECOMMANDINFO pici)
{
	BOOL fUnicode = FALSE;

	// Determine which structure is being passed in, CMINVOKECOMMANDINFO or 
	// CMINVOKECOMMANDINFOEX based on the cbSize member of lpcmi. Although 
	// the lpcmi parameter is declared in Shlobj.h as a CMINVOKECOMMANDINFO 
	// structure, in practice it often points to a CMINVOKECOMMANDINFOEX 
	// structure. This struct is an extended version of CMINVOKECOMMANDINFO 
	// and has additional members that allow Unicode strings to be passed.
	if (pici->cbSize == sizeof(CMINVOKECOMMANDINFOEX))
	{
		if (pici->fMask & CMIC_MASK_UNICODE)
		{
			fUnicode = TRUE;
		}
	}

	// Determines whether the command is identified by its offset or verb.
	// There are two ways to identify commands:
	// 
	//   1) The command's verb string 
	//   2) The command's identifier offset
	// 
	// If the high-order word of lpcmi->lpVerb (for the ANSI case) or 
	// lpcmi->lpVerbW (for the Unicode case) is nonzero, lpVerb or lpVerbW 
	// holds a verb string. If the high-order word is zero, the command 
	// offset is in the low-order word of lpcmi->lpVerb.

	// For the ANSI case, if the high-order word is not zero, the command's 
	// verb string is in lpcmi->lpVerb. 
	if (!fUnicode && HIWORD(pici->lpVerb))
	{
		// Is the verb supported by this context menu extension?
		if (StrCmpIA(pici->lpVerb, m_pszVerb) == 0)
		{
			OnVerbDisplayFileName(pici->hwnd);
		}
		else
		{
			// If the verb is not recognized by the context menu handler, it 
			// must return E_FAIL to allow it to be passed on to the other 
			// context menu handlers that might implement that verb.
			return E_FAIL;
		}
	}

	// For the Unicode case, if the high-order word is not zero, the 
	// command's verb string is in lpcmi->lpVerbW. 
	else if (fUnicode && HIWORD(((CMINVOKECOMMANDINFOEX*)pici)->lpVerbW))
	{
		// Is the verb supported by this context menu extension?
		if (StrCmpIW(((CMINVOKECOMMANDINFOEX*)pici)->lpVerbW, m_pwszVerb) == 0)
		{
			OnVerbDisplayFileName(pici->hwnd);
		}
		else
		{
			// If the verb is not recognized by the context menu handler, it 
			// must return E_FAIL to allow it to be passed on to the other 
			// context menu handlers that might implement that verb.
			return E_FAIL;
		}
	}

	// If the command cannot be identified through the verb string, then 
	// check the identifier offset.
	else
	{
		// Is the command identifier offset supported by this context menu 
		// extension?
		if (LOWORD(pici->lpVerb) == IDM_DISPLAY)
		{
			OnVerbDisplayFileName(pici->hwnd);
		}
		else
		{
			// If the verb is not recognized by the context menu handler, it 
			// must return E_FAIL to allow it to be passed on to the other 
			// context menu handlers that might implement that verb.
			return E_FAIL;
		}
	}

	return S_OK;
}


//
//   FUNCTION: CFileContextMenuExt::GetCommandString
//
//   PURPOSE: If a user highlights one of the items added by a context menu 
//            handler, the handler's IContextMenu::GetCommandString method is 
//            called to request a Help text string that will be displayed on 
//            the Windows Explorer status bar. This method can also be called 
//            to request the verb string that is assigned to a command. 
//            Either ANSI or Unicode verb strings can be requested. This 
//            example only implements support for the Unicode values of 
//            uFlags, because only those have been used in Windows Explorer 
//            since Windows 2000.
//
IFACEMETHODIMP FileContextMenuExt::GetCommandString(
	UINT_PTR idCommand, 
	UINT uFlags, 
	UINT *pwReserved, 
	LPSTR pszName, 
	UINT cchMax)
{
	HRESULT hr = E_INVALIDARG;


	switch (uFlags)
	{
		case GCS_HELPTEXTW:
			// Only useful for pre-Vista versions of Windows that have a 
			// Status bar.
			hr = StringCchCopy(reinterpret_cast<PWSTR>(pszName), cchMax, 
				m_pwszVerbHelpText);
			break;

		case GCS_VERBW:
			// GCS_VERBW is an optional feature that enables a caller to 
			// discover the canonical name for the verb passed in through 
			// idCommand.
			hr = StringCchCopy(reinterpret_cast<PWSTR>(pszName), cchMax, 
				m_pwszVerbCanonicalName);
			break;

		default:
			hr = S_OK;
	}

	// If the command (idCommand) is not supported by this context menu 
	// extension handler, return E_INVALIDARG.

	return hr;
}

#pragma endregion