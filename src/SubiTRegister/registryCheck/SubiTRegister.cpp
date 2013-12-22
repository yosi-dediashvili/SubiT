// registryCheck.cpp : Defines the entry point for the console application.
//

#include "stdafx.h"
#include "Shlwapi.h"
#include <iostream>
#include "Winreg.h"
#include <fstream>
#include <windows.h>
#include <string>

typedef LONG NTSTATUS;

#ifndef STATUS_SUCCESS
#define STATUS_SUCCESS ((NTSTATUS)0x00000000L)
#endif

#ifndef STATUS_BUFFER_TOO_SMALL
#define STATUS_BUFFER_TOO_SMALL ((NTSTATUS)0xC0000023L)
#endif

#define REGISTER_ARGUMENT	L"-register"
#define UNREGISTER_ARGUMENT L"-unregister"
#define REG_MAX_PATH 16512


//====================================================================
//Function taken from the net -> so much code for just getting the path 
//of the given key...
//====================================================================
std::wstring GetKeyPathFromKKEY(HKEY key)
{
	std::wstring keyPath;
	if (key != NULL)
	{
		HMODULE dll = LoadLibrary(L"ntdll.dll");
		if (dll != NULL) {
			typedef DWORD (__stdcall *NtQueryKeyType)(
				HANDLE  KeyHandle,
				int KeyInformationClass,
				PVOID  KeyInformation,
				ULONG  Length,
				PULONG  ResultLength);

			NtQueryKeyType func = reinterpret_cast<NtQueryKeyType>(::GetProcAddress(dll, "NtQueryKey"));

			if (func != NULL) {
				DWORD size = 0;
				DWORD result = 0;
				result = func(key, 3, 0, 0, &size);
				if (result == STATUS_BUFFER_TOO_SMALL)
				{
					size = size + 2;
					wchar_t* buffer = new (std::nothrow) wchar_t[size/sizeof(wchar_t)]; // size is in bytes
					if (buffer != NULL)
					{
						result = func(key, 3, buffer, size, &size);
						if (result == STATUS_SUCCESS)
						{
							buffer[size / sizeof(wchar_t)] = L'\0';
							keyPath = std::wstring(buffer + 2);
						}

						delete[] buffer;
					}
				}
			}

			FreeLibrary(dll);
		}
	}
	return keyPath;
}

void printUsage()
{
	printf(
"Usage: SubiTRegister.exe [-register/-unregister] [.ext] [SubiT.exe path]\n\
------------------------\n\n\
Use this program to register/unregister one extension from the registry");

	getchar();
}

//====================================================================
//Will retrieve the relevant Key for registration -> function from the api
//====================================================================
HKEY getRelevantKey(LPCTSTR extKey)
{
	wprintf(L"Quering for extension: %s\n", extKey);
	HKEY key = NULL;
	LONG ret = ERROR_SUCCESS;
	ret = AssocQueryKey(ASSOCF_INIT_IGNOREUNKNOWN, ASSOCKEY_CLASS, LPCTSTR(extKey), NULL, &key);
	if (ret == ERROR_SUCCESS) 
		wprintf(L"Key path for %p is '%s'.\n", key, GetKeyPathFromKKEY(key).c_str());
	else
		wprintf(L"Can't find key!\n");

	wprintf( L"Done!\n" );
	return key;
}

int _tmain(int argc, _TCHAR* argv[])
{
	wprintf(L"=====================================================\n");
	//====================================================================================================
	//====================================================================================================
	//We start with os version - Currently supports only vista and greater, because of the RegDeleteTree
	//Function (Need to look at SHDeleteKey
	//OSVERSIONINFO osVersionInfo;
	//ZeroMemory(&osVersionInfo, sizeof(OSVERSIONINFO));
	//osVersionInfo.dwOSVersionInfoSize = sizeof(OSVERSIONINFO);
	//GetVersionEx(&osVersionInfo);
	////If os is lower the vista (vista is major = 6 & minor = 0)
	//if (osVersionInfo.dwMajorVersion <= 5)
	//{
	//	std::cout << "Currently Supports only Windows Vista and greater!\n";
	//	return 0;
	//}
	//std::cout << "OS is Fine...\n";
	//====================================================================================================
	//====================================================================================================


	//We will execute only if we 3-4 arguments
	if (argc >= 3 && argc < 5 && (	StrCmp(LPCWSTR(argv[1]), REGISTER_ARGUMENT) || 
									StrCmp(LPCWSTR(argv[1]), UNREGISTER_ARGUMENT)))
	{
		HKEY key = getRelevantKey(argv[2]);
		if (key == NULL) std::cout << "Can't retrieve key!\n";
		else
		{
			try
			{
				//====================================================================
				//Handle registation of one extension
				//====================================================================
				if ( 0 == StrCmp(argv[1], REGISTER_ARGUMENT) && argc == 4) //including SubiT.exe path
				{
					//We check to see if the path to subit.exe is real
					FILE * sFile;
					_wfopen_s(&sFile, LPWSTR(argv[3]), L"r");

					if (NULL != sFile)
					{
						fclose(sFile);
						std::cout << "SubiT.exe Exists!" << std::endl;
						std::cout << "Register..." << std::endl;
						//We create the key to the default_value under shell\subit\command
						HKEY subitKey = NULL;
						HRESULT subitResult = RegCreateKeyEx(	key, L"shell\\SubiT\\command", 
																NULL, NULL, NULL, KEY_ALL_ACCESS, NULL, &subitKey, NULL);
						std::cout << "Created Keys!" << std::endl;
						if (subitKey != NULL)
						{
							WCHAR data[REG_MAX_PATH];
							swprintf(data, L"\"%s\" \"\%%1\"", argv[3]); 
							RegSetValueEx(subitKey, NULL, NULL, REG_SZ, LPBYTE(data), REG_MAX_PATH);
							std::cout << "Created Value!" << std::endl;
							RegCloseKey(subitKey);
						}
					}
					else
					{
						std::cout << "SubiT.exe File is missing" << std::endl;
						return 0;
					}
				}
				//====================================================================
				//Handle registration removal of one extension
				//====================================================================
				else if ( 0 == StrCmp(argv[1], UNREGISTER_ARGUMENT) ) //we don't need SubiT.exe path
				{
					std::cout << "Unregister...\n";
					//HRESULT result = RegDeleteTree(key, L"shell\\SubiT"); //Will delete all the subTrees either
					HRESULT result = SHDeleteKey(key, L"shell\\SubiT");
					if (SUCCEEDED(result))
					{
						std::cout << "Deleted Successfuly!" << std::endl;
					}
					else
					{
						std::cout << "Failed Deleting: " << result << std::endl;
					}
				}
		
				RegCloseKey(key);
			}
			catch (...)
			{
				std::cout << "Exception!" << std::endl;
				RegCloseKey(key);
			}
			wprintf(L"=====================================================\n");
		}
	}
	else
	{
		printUsage();
	}

	return 0;
}