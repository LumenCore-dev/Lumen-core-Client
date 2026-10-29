from pathlib import Path
import ctypes as c
from ctypes import wintypes as w
import re,os,sys
root=Path(r'D:\Halo4-Server')
dia_dir=os.add_dll_directory(r'C:\Program Files\Microsoft Visual Studio\2022\Community\DIA SDK\bin\amd64')
dia=c.WinDLL(r'C:\Program Files\Microsoft Visual Studio\2022\Community\DIA SDK\bin\amd64\msdia140.dll')
dbg=c.WinDLL(r'C:\Program Files (x86)\Windows Kits\10\Debuggers\x64\dbghelp.dll',use_last_error=True);kernel=c.WinDLL('kernel32')
kernel.GetCurrentProcess.restype=w.HANDLE
process=kernel.GetCurrentProcess()
dbg.SymInitializeW.argtypes=[w.HANDLE,w.LPCWSTR,w.BOOL];dbg.SymInitializeW.restype=w.BOOL
dbg.SymSetOptions(0x10|0x2|0x4)
callback_type=c.WINFUNCTYPE(w.BOOL,w.HANDLE,w.ULONG,c.c_ulonglong,c.c_ulonglong)
@callback_type
def callback(proc,action,data,context):
    if action==0x10000000:print(c.string_at(data).decode(errors='replace').strip())
    return False
dbg.SymRegisterCallback64.argtypes=[w.HANDLE,callback_type,c.c_ulonglong]
assert dbg.SymInitializeW(process,str(root/'Source/build/deadlock'),False)
dbg.SymRegisterCallback64(process,callback,0)
dbg.SymSetOptions(0x80000016)
dbg.SymLoadModuleExW.argtypes=[w.HANDLE,w.HANDLE,w.LPCWSTR,w.LPCWSTR,c.c_ulonglong,w.DWORD,c.c_void_p,w.DWORD];dbg.SymLoadModuleExW.restype=c.c_ulonglong
base=0x10000000
loaded=dbg.SymLoadModuleExW(process,None,str(root/'Source/build/deadlock/Halo4NativeClient.exe'),None,base,0xc20000,None,0)
print('loaded',hex(loaded), 'error',c.get_last_error())
assert loaded
class Symbol(c.Structure):
    _fields_=[('SizeOfStruct',w.ULONG),('TypeIndex',w.ULONG),('Reserved',c.c_ulonglong*2),('Index',w.ULONG),('Size',w.ULONG),('ModBase',c.c_ulonglong),('Flags',w.ULONG),('Value',c.c_ulonglong),('Address',c.c_ulonglong),('Register',w.ULONG),('Scope',w.ULONG),('Tag',w.ULONG),('NameLen',w.ULONG),('MaxNameLen',w.ULONG),('Name',c.c_char*1)]
class Line(c.Structure):
    _fields_=[('SizeOfStruct',w.DWORD),('Key',c.c_void_p),('LineNumber',w.DWORD),('FileName',c.c_char_p),('Address',c.c_ulonglong)]
dbg.SymFromAddr.argtypes=[w.HANDLE,c.c_ulonglong,c.POINTER(c.c_ulonglong),c.POINTER(Symbol)];dbg.SymFromAddr.restype=w.BOOL
dbg.SymGetLineFromAddr64.argtypes=[w.HANDLE,c.c_ulonglong,c.POINTER(w.DWORD),c.POINTER(Line)];dbg.SymGetLineFromAddr64.restype=w.BOOL
trace_path=Path(sys.argv[1]) if len(sys.argv)>1 else root/'reports/deadlock-repro-20261016/cpp-stacks.txt'
for row in trace_path.read_text().splitlines()[-3:]:
    original=int(re.search(r'base=([0-9A-F]+)',row)[1],16)
    print('STACK')
    for text in row.split()[2:]:
        address=int(text,16)-original+base
        buf=c.create_string_buffer(2048);symbol=c.cast(buf,c.POINTER(Symbol));symbol.contents.SizeOfStruct=c.sizeof(Symbol);symbol.contents.MaxNameLen=1900;offset=c.c_ulonglong()
        if not dbg.SymFromAddr(process,address,c.byref(offset),symbol):
            if base<=address<base+0x1000000:print(hex(address),'symbol lookup error',c.get_last_error())
            continue
        name=c.string_at(c.addressof(buf)+Symbol.Name.offset,symbol.contents.NameLen).decode(errors='replace')
        line=Line();line.SizeOfStruct=c.sizeof(Line);displacement=w.DWORD()
        source=''
        if dbg.SymGetLineFromAddr64(process,address,c.byref(displacement),c.byref(line)):source=f' {line.FileName.decode(errors="replace")}:{line.LineNumber}'
        print(f'{text} {name}+{offset.value:x}{source}')
