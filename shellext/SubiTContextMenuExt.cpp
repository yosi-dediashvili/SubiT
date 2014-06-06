#include "SubiTContextMenuExt.h"
#include <strsafe.h>
#include <Shlwapi.h>
#include "resource.h"

#pragma comment(lib, "shlwapi.lib")

extern HINSTANCE g_DllModuleHInstance;
extern long g_DllRefCount;

#define IDM_DISPLAY             0  // The command's identifier offset

SubiTContextMenuExt::SubiTContextMenuExt(void) : 
	m_cRef(1),
	_subit_bmp_handle(NULL),
	_got_subit_executable_path(false)
{
	InterlockedIncrement(&g_DllRefCount);

	_storeSubiTPath();
	_storeSubiTBitmap();
}

SubiTContextMenuExt::~SubiTContextMenuExt(void)
{
	if (_subit_bmp_handle)
	{
		DeleteObject(_subit_bmp_handle);
		_subit_bmp_handle = NULL;
	}

	InterlockedDecrement(&g_DllRefCount);
}

void SubiTContextMenuExt::_storeSubiTBitmap() {
	_subit_bmp_handle = static_cast<HBITMAP>(LoadImage(
		g_DllModuleHInstance,
		MAKEINTRESOURCE(IDB_SUBIT_BMP),
		IMAGE_BITMAP,
		NULL,
		NULL,
		LR_DEFAULTSIZE | LR_LOADTRANSPARENT | LR_LOADMAP3DCOLORS));
}

void SubiTContextMenuExt::_storeSubiTPath() {

	WCHAR current_path[MAX_PATH];
	if (NULL == GetModuleFileName(
		g_DllModuleHInstance, current_path, MAX_PATH)){

		this->_got_subit_executable_path = false;
		return;
	}

	// The dll should be in: <subit_root>\Settings\Associators\WinAssociator\-
	// [32\64]\<dll_name>. In order to get to SubiT's root directory, we need 
	// to go 5 directories up.
	for (int dirs_to_go_up = 5; dirs_to_go_up > 0; --dirs_to_go_up){
		PathRemoveFileSpec(current_path);
	}

	if (NULL != PathCombine(
		this->_subit_executable_path,
		current_path,
		SUBIT_EXECUTABLE_NAME.c_str())){

		// Mark as "got" only if the path realy exists.
		this->_got_subit_executable_path =
			PathFileExists(this->_subit_executable_path);
	}
	// Copy the path to the dir's variable.
	StringCchCopy(
		this->_subit_dir_path, MAX_PATH, this->_subit_executable_path);
	
	// And remove the file name.
	PathRemoveFileSpec(this->_subit_dir_path);
}

void SubiTContextMenuExt::_storeSelectedPaths(HDROP hDrop) {
	
	// First, clear the old content of the vectors.
	this->_selected_files.clear();
	this->_selected_dirs.clear();

	// When DragQueryFile recieves 0xFFFFFFFF as the file id, it 
	// returns the number of files or dirs that was selected.
	UINT number_of_paths = DragQueryFile(hDrop, 0xFFFFFFFF, NULL, 0);

	for (UINT i = 0; i < number_of_paths; ++i) {
		// When DragQueryFile recieves any other file id, it returns 
		// the number of characters that was stored in the file name
		// buffer that was passed to it.
		WCHAR current_path[MAX_PATH];
		if (NULL != DragQueryFile(hDrop, i, current_path, MAX_PATH)) {
			if (PathIsDirectory(current_path)) {
				this->_selected_dirs.push_back(current_path);
			}
			else {
				this->_selected_files.push_back(current_path);
			}
		}
	}
}

inline wstring _format_parameter(
	const wstring & str,
	BOOL add_spaces,
	BOOL add_quotation_marks)
{
	wstring wstr;
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

inline void _add_paths_to_parameters_if_not_empty(
	wstring & parameters,
	const wstring & param_name,
	const vector<wstring> & paths) {

	if (!paths.empty()) {
		parameters += _format_parameter(param_name, TRUE, FALSE);
		for (auto path : paths) {
			// Enclose each path with quotation_marks
			parameters += _format_parameter(path, TRUE, TRUE);
		}
	}
}

wstring SubiTContextMenuExt::_buildSubitParameters()
{
	wstring parameters;

	// Write the mode parameter.
	parameters += _format_parameter(this->SUBIT_MODE_PARAM, TRUE, FALSE);
	parameters += _format_parameter(L"BY-CONFIG", TRUE, FALSE);

	// Write the files parameter
	_add_paths_to_parameters_if_not_empty(
		parameters, this->SUBIT_FILES_PARAM, this->_selected_files);
	// Write the dirs parameter
	_add_paths_to_parameters_if_not_empty(
		parameters, this->SUBIT_DIRS_PARAM, this->_selected_dirs);

	return parameters;
}

void SubiTContextMenuExt::_executeSubiT(HWND hWnd)
{
	// If we failed to get the path to SubiT.
	if (!this->_got_subit_executable_path) {
		MessageBox(
			hWnd,
			L"The executable file of SubiT is missing from SubiT's root directory.",
			L"SubiT.exe is missing",
			MB_OK | MB_ICONERROR);
	}

	wstring subit_params = this->_buildSubitParameters();
	vector<WCHAR> subit_params_vector(subit_params.begin(), subit_params.end());

	STARTUPINFO subit_startup_info;
	ZeroMemory(&subit_startup_info, sizeof(subit_startup_info));
	subit_startup_info.cb = sizeof(subit_startup_info);

	PROCESS_INFORMATION subit_process_info;
	ZeroMemory(&subit_process_info, sizeof(subit_process_info));
	
	// Execute the process.
	CreateProcess(
		this->_subit_executable_path,
		&subit_params_vector[0],
		NULL,
		NULL,
		FALSE,
		NULL,
		NULL,
		this->_subit_dir_path,
		&subit_startup_info,
		&subit_process_info);

	DWORD subit_exit_code;
	
	// If the error is not "success" or SubiT stopped running.
	if (!GetExitCodeProcess(subit_process_info.hProcess, &subit_exit_code) ||
		subit_exit_code != STILL_ACTIVE) {

		DWORD last_error = GetLastError();
		LPTSTR error_message = NULL;
		// Exract the error message
		FormatMessage(
			FORMAT_MESSAGE_FROM_SYSTEM |
			FORMAT_MESSAGE_ALLOCATE_BUFFER |
			FORMAT_MESSAGE_IGNORE_INSERTS,
			NULL,
			last_error,
			MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT),
			(LPTSTR)&error_message,
			0,
			NULL);

		// Format it.
		wstring our_error_message;
		if (NULL != error_message) {
			our_error_message = L"Calling SubiT resulted in an error: \r\n";
			our_error_message += error_message;
		}
		else {
			our_error_message = L"Calling SubiT resulted in an unknown error.";
		}

		// Show the error.
		MessageBox(
			hWnd, 
			our_error_message.c_str(),
			L"SubiT Failed",
			MB_OK | MB_ICONERROR);
		// Free the error message buffer.
		LocalFree(error_message);
	}
}

#pragma region IUnknown

// Query to the interface the component supported.
IFACEMETHODIMP SubiTContextMenuExt::QueryInterface(REFIID riid, void **ppv)
{
	static const QITAB qit[] = 
	{
		QITABENT(SubiTContextMenuExt, IContextMenu),
		QITABENT(SubiTContextMenuExt, IShellExtInit), 
		{ 0 },
	};
	return QISearch(this, qit, riid, ppv);
}

// Increase the reference count for an interface on an object.
IFACEMETHODIMP_(ULONG) SubiTContextMenuExt::AddRef()
{
	return InterlockedIncrement(&m_cRef);
}

// Decrease the reference count for an interface on an object.
IFACEMETHODIMP_(ULONG) SubiTContextMenuExt::Release()
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

IFACEMETHODIMP SubiTContextMenuExt::Initialize(
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
			this->_storeSelectedPaths(hDrop);
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
//   FUNCTION: SubiTContextMenuExt::QueryContextMenu
//
//   PURPOSE: The Shell calls IContextMenu::QueryContextMenu to allow the 
//            context menu handler to add its menu items to the menu. It 
//            passes in the HMENU handle in the hmenu parameter. The 
//            indexMenu parameter is set to the index to be used for the 
//            first menu item that is to be added.
//
IFACEMETHODIMP SubiTContextMenuExt::QueryContextMenu(
	HMENU hMenu, UINT indexMenu, UINT idCmdFirst, UINT idCmdLast, UINT uFlags)
{
	// If uFlags include CMF_DEFAULTONLY then we should not do anything.
	if (CMF_DEFAULTONLY & uFlags)
	{
		return MAKE_HRESULT(SEVERITY_SUCCESS, 0, USHORT(0));
	}
	
	// Construct the menu item.
	MENUITEMINFO subit_menu_item = { sizeof(subit_menu_item) };
	subit_menu_item.fMask = MIIM_STRING | MIIM_ID | MIIM_BITMAP;
	subit_menu_item.wID = idCmdFirst;
	// It's OK to cast away the const. The pointer is not const only because 
	// the genericness of the structure. In our case, the dwTypeData is not 
	// going to be touched.
	subit_menu_item.dwTypeData = \
		const_cast<wchar_t *>(this->SUBIT_MENU_TEXT.c_str());
	subit_menu_item.hbmpItem = _subit_bmp_handle;

	// Try to insert it to the ContextMenu.
	if (!InsertMenuItem(hMenu, indexMenu, TRUE, &subit_menu_item))
	{
		return HRESULT_FROM_WIN32(GetLastError());
	}

	// And, add a separator right after us.
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



//
//   FUNCTION: SubiTContextMenuExt::InvokeCommand
//
//   PURPOSE: This method is called when a user clicks a menu item to tell 
//            the handler to run the associated command. The lpcmi parameter 
//            points to a structure that contains the needed information.
//
IFACEMETHODIMP SubiTContextMenuExt::InvokeCommand(LPCMINVOKECOMMANDINFO pici)
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
		if (StrCmpIA(pici->lpVerb, this->SUBIT_COMMAND_NAME_A.c_str()) == 0)
		{
			_executeSubiT(pici->hwnd);
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
		if (StrCmpIW(((CMINVOKECOMMANDINFOEX*)pici)->lpVerbW, 
			this->SUBIT_COMMAND_NAME.c_str()) == 0)
		{
			_executeSubiT(pici->hwnd);
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
			_executeSubiT(pici->hwnd);
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
//   FUNCTION: SubiTContextMenuExt::GetCommandString
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
IFACEMETHODIMP SubiTContextMenuExt::GetCommandString(
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
				this->SUBIT_HELP_TEXT.c_str());
			break;

		case GCS_VERBW:
			// GCS_VERBW is an optional feature that enables a caller to 
			// discover the canonical name for the verb passed in through 
			// idCommand.
			hr = StringCchCopy(reinterpret_cast<PWSTR>(pszName), cchMax, 
				this->SUBIT_CAONICAL_NAME.c_str());
			break;

		default:
			hr = S_OK;
	}

	// If the command (idCommand) is not supported by this context menu 
	// extension handler, return E_INVALIDARG.

	return hr;
}

#pragma endregion