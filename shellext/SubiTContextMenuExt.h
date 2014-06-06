#pragma once

#include <windows.h>
#include <shlobj.h>     // For IShellExtInit and IContextMenu
#include <vector>
#include <string>
#include <iostream>

using namespace std;

/*
	The class handles the operation of adding SubiT menu item to the ContextMenu 
	whenever the ContextMenu is displayed.

	The call flow is as followed:
		1. When the users select some items in the explorer, and decide to open
		the context menu (right click), the Initialize() function gets called.
		2. Right after that, the QueryContextMenu is called. That's where we 
		insert SubiT's menu item to the CotnextMenu.
		3. Whenever our menu item get hovered by the mouse pointer, the Get-
		CommandString is called.
		4. When (and if) the user clicks on our menu item, the InvokeCommand 
		gets called.

	We're passing SubiT all the files that passed to us. These files are not 
	necessarily movie files because if the user selects other file types along 
	with movie files, and right clicks them when the mouse is over a movie 
	file, and not other file, then we will apear in the context menu. SubiT 
	will later filter out the files that are not movie files.
*/
class SubiTContextMenuExt : public IShellExtInit, public IContextMenu
{
public:
	// IUnknown
	IFACEMETHODIMP QueryInterface(REFIID riid, void **ppv);
	IFACEMETHODIMP_(ULONG) AddRef();
	IFACEMETHODIMP_(ULONG) Release();

	/*
		IShellExtInit. In our case, this function gets called when one or more
		items in the explorer was selected, and the ContextMenu is about to be
		diplayed for those items (The user right clicked after selecting them).

		This is where we catch the selected files and directories.
	*/
	IFACEMETHODIMP Initialize(
		LPCITEMIDLIST pidlFolder, LPDATAOBJECT pDataObj, HKEY hKeyProgID);

	/*
		This function gets called before the ContextMenu is displayed, and it's
		used in order to add items to the ContextMenu. In our case, that is 
		where we add SubiT to the ContextMenu.
	*/
	IFACEMETHODIMP QueryContextMenu(
		HMENU hMenu, UINT indexMenu, UINT idCmdFirst, UINT idCmdLast, UINT uFlags);

	/*
		This function gets called when the user clicks on an item in the Conte-
		xtMenu. This is the place where we check whether he clicked on our item
		or on another item. If it turs out the SubiT's item was clicked, we 
		call the _executeSubiT() function.
	*/
	IFACEMETHODIMP InvokeCommand(
		LPCMINVOKECOMMANDINFO pici);

	/*
		This function get called when our item in the ContextMenu gets hovered 
		by the mouse pointer. It's used in order to display some help messages
		in the status bar (udner Windows XP and below).
	*/
	IFACEMETHODIMP GetCommandString(
		UINT_PTR idCommand, UINT uFlags, UINT *pwReserved, LPSTR pszName, UINT cchMax);
	
	SubiTContextMenuExt(void);

protected:
	~SubiTContextMenuExt(void);

private:
	// Reference count of component.
	long m_cRef;

	const wstring SUBIT_EXECUTABLE_NAME = L"SubiT.exe";
	const wstring SUBIT_FILES_PARAM = L"-files";
	const wstring SUBIT_DIRS_PARAM = L"-dirs";
	const wstring SUBIT_MODE_PARAM = L"-mode";
	// Displayed under Windows XP and below when our menu item get hovered by
	// the mouse pointer.
	const wstring SUBIT_HELP_TEXT = L"Download subtitle for the selected files";
	const wstring SUBIT_CAONICAL_NAME = L"SubiT";
	// Our CommandID string.
	const wstring SUBIT_COMMAND_NAME  = L"SubiT_ExecuteFromContextMenuHandler";
	const string SUBIT_COMMAND_NAME_A = "SubiT_ExecuteFromContextMenuHandler";
	// The text that will be displayed in the ContextMenu item.
	const wstring SUBIT_MENU_TEXT = L"SubiT";

	// Handle to the Bitmap image of SubiT's ContextMenu item.
	HBITMAP _subit_bmp_handle;

	// When the Initialize function get called, these vectors get filled with 
	// the selected paths. And, when InvokeCommand get called, the vectors are
	// used in order to construct the parameter for SubiT.
	vector<wstring> _selected_files;
	vector<wstring> _selected_dirs;

	// The path to the SubiT.exe. 
	WCHAR _subit_executable_path[MAX_PATH];
	// The path to SubiT's directory.
	WCHAR _subit_dir_path[MAX_PATH];
	// True if we managed to locate the executable.
	BOOL _got_subit_executable_path;
	/*
		Perform the task of executing SubiT with the right arguments based on
		the ContextMenu's handle passed to it. We're executing SubiT from 
		SubiT's directory as the CurrentDirectory.
	*/
	void _executeSubiT(HWND hWnd);

	/*
		The function received an HDROP object, and extract all the paths that
		it contains within it, and storing them in the _selected_files and 
		_selected_dirs vector.
	*/
	void _storeSelectedPaths(HDROP hDrop);

	/*
		Constructs the parameters that should be passed to SubiT's executable.
		The parameter will be returned as a one long string.
	*/
	wstring _buildSubitParameters();


	/*
		The function will try to get the path of SubiT.exe file. If the file is
		missing from the assumed path, the function sets the _got_subit_execut-
		able_path to false, otherwise, the _subit_executable_path will contain
		the full path to the executable, and _got_subit_executable_path will be
		set to true. The function also set (on success) the _subit_dir_path.
	*/
	void _storeSubiTPath();

	void _storeSubiTBitmap();
};