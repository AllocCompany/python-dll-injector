import sys
import psutil
from ctypes import*

PAGE_EXECUTE_READWRITE = 0x40
PAGE_READWRITE = 0x04
THREAD_ID = c_ulong(0)

def get_process_id(process_name):
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'].lower() == process_name.lower():
                return proc.info['pid']
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None

def get_external_load_library(krnl32):
    get_kernel32_base_address = krnl32.GetModuleHandleA("kernel32.dll")
    if(get_kernel32_base_address != 0):
            get_load_library_address = krnl32.GetProcAddress(get_kernel32_base_address, "LoadLibraryA")
            if(get_load_library_address != 0):
                return get_load_library_address


def inject_module(pid,module_path):
    print(" [ * ] Prepiring image for mapping")
    image_sizeof = len(module_path)
    kernel_32_dll = windll.kernel32
    proc_handle = kernel_32_dll.OpenProcess( 0x00F0000 | 0x00100000 | 0xFFF , False, int(pid) )
    print(" [ * ] Allocating virtual memory")
    arg_address = kernel_32_dll.VirtualAllocEx(proc_handle, 0, image_sizeof, 0x1000 | 0x2000, PAGE_EXECUTE_READWRITE)
    print(" [ * ] Getting external address")
    load_library_address = get_external_load_library(kernel_32_dll)
    print(" [ * ] Creating thread")
    kernel_32_dll.CreateRemoteThread(proc_handle, None, 0, load_library_address, arg_address, 0, byref(THREAD_ID))
    print(" [ * ] Dll injected !")

if __name__ == "__main__":
    process_name = input("[ * ] Enter proccess name -> ")
    proocess_id = get_process_id(process_name)
    if(proocess_id != 0):
            module_path = "C:\\module.dll"
            print("[ * ] Proccess ID -> ",proocess_id)
            print("[ * ] Dll path -> ",module_path)
            inject_module(proocess_id,module_path)
    else:
         print(" [ ! ] Process not found !")
