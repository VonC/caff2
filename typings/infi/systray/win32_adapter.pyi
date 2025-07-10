import ctypes
import ctypes.wintypes
from _typeshed import Incomplete

RegisterWindowMessage: Incomplete
LoadCursor: Incomplete
LoadIcon: Incomplete
LoadImage: Incomplete
RegisterClass: Incomplete
CreateWindowEx: Incomplete
UpdateWindow: Incomplete
DefWindowProc: Incomplete
GetSystemMetrics: Incomplete
InsertMenuItem: Incomplete
PostMessage: Incomplete
PostQuitMessage: Incomplete
SetMenuDefaultItem: Incomplete
GetCursorPos: Incomplete
SetForegroundWindow: Incomplete
TrackPopupMenu: Incomplete
CreatePopupMenu: Incomplete
CreateCompatibleDC: Incomplete
GetDC: Incomplete
CreateCompatibleBitmap: Incomplete
GetSysColorBrush: Incomplete
FillRect: Incomplete
DrawIconEx: Incomplete
SelectObject: Incomplete
DeleteDC: Incomplete
DestroyWindow: Incomplete
GetModuleHandle: Incomplete
GetMessage: Incomplete
TranslateMessage: Incomplete
DispatchMessage: Incomplete
Shell_NotifyIcon: Incomplete
DestroyIcon: Incomplete
NIM_ADD: int
NIM_MODIFY: int
NIM_DELETE: int
NIF_ICON: int
NIF_MESSAGE: int
NIF_TIP: int
MIIM_ID: int
MIIM_SUBMENU: int
MIIM_STRING: int
MIIM_BITMAP: int
WM_DESTROY: int
WM_CLOSE: int
WM_COMMAND: int
WM_USER: int
WM_LBUTTONDBLCLK: int
WM_RBUTTONUP: int
WM_LBUTTONUP: int
WM_NULL: int
CS_VREDRAW: int
CS_HREDRAW: int
IDC_ARROW: int
COLOR_WINDOW: int
WS_OVERLAPPED: int
WS_SYSMENU: int
CW_USEDEFAULT: int
LR_LOADFROMFILE: int
LR_DEFAULTSIZE: int
IMAGE_ICON: int
IDI_APPLICATION: int
TPM_LEFTALIGN: int
SM_CXSMICON: int
SM_CYSMICON: int
COLOR_MENU: int
DI_NORMAL: int
WPARAM = ctypes.wintypes.WPARAM
LPARAM = ctypes.wintypes.LPARAM
HANDLE: Incomplete
LRESULT = ctypes.c_long
LRESULT = ctypes.c_longlong
SZTIP_MAX_LENGTH: int
LOCALE_ENCODING: Incomplete

def encode_for_locale(s): ...
POINT = ctypes.wintypes.POINT
RECT = ctypes.wintypes.RECT
MSG = ctypes.wintypes.MSG
LPFN_WNDPROC: Incomplete

class WNDCLASS(ctypes.Structure): ...
class MENUITEMINFO(ctypes.Structure): ...
class NOTIFYICONDATA(ctypes.Structure): ...

def PackMENUITEMINFO(text: Incomplete | None = None, hbmpItem: Incomplete | None = None, wID: Incomplete | None = None, hSubMenu: Incomplete | None = None): ...
def LOWORD(w): ...
def PumpMessages() -> None: ...
def NotifyData(hWnd: int = 0, uID: int = 0, uFlags: int = 0, uCallbackMessage: int = 0, hIcon: int = 0, szTip: str = ''): ...
