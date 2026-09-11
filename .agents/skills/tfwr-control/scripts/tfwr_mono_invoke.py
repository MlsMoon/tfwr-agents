#!/usr/bin/env python3
"""Load TfwrRunMain.dll into the live TFWR Mono runtime and call Load()."""

from __future__ import annotations

import ctypes
import struct
import sys
from ctypes import wintypes
from pathlib import Path

PROCESS_RIGHTS = 0x043A
MEM_COMMIT = 0x1000
MEM_RESERVE = 0x2000
PAGE_EXECUTE_READWRITE = 0x40
LIST_MODULES_ALL = 0x03

EXPORTS = (
    "mono_get_root_domain",
    "mono_thread_attach",
    "mono_image_open_from_data",
    "mono_assembly_load_from_full",
    "mono_assembly_get_image",
    "mono_class_from_name",
    "mono_class_get_method_from_name",
    "mono_runtime_invoke",
)

kernel32 = ctypes.windll.kernel32
psapi = ctypes.windll.psapi

kernel32.OpenProcess.restype = wintypes.HANDLE
kernel32.VirtualAllocEx.restype = wintypes.LPVOID
kernel32.CreateRemoteThread.restype = wintypes.HANDLE


def _err(label: str) -> None:
    raise OSError(f"{label}: {ctypes.WinError(kernel32.GetLastError())}")


def alloc_write(handle: int, data: bytes) -> int:
    ptr = kernel32.VirtualAllocEx(handle, None, max(len(data), 8), MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE)
    if not ptr:
        _err("VirtualAllocEx")
    written = ctypes.c_size_t()
    if not kernel32.WriteProcessMemory(handle, ctypes.c_void_p(ptr), data, len(data), ctypes.byref(written)):
        _err("WriteProcessMemory")
    return int(ptr)


def alloc_cstr(handle: int, text: str) -> int:
    return alloc_write(handle, text.encode("utf-8") + b"\x00")


def read_i64(handle: int, addr: int) -> int:
    buf = ctypes.create_string_buffer(8)
    read = ctypes.c_size_t()
    if not kernel32.ReadProcessMemory(handle, ctypes.c_void_p(addr), buf, 8, ctypes.byref(read)):
        _err("ReadProcessMemory")
    return struct.unpack_from("<q", buf.raw)[0]


def read_i32(handle: int, addr: int) -> int:
    buf = ctypes.create_string_buffer(4)
    read = ctypes.c_size_t()
    if not kernel32.ReadProcessMemory(handle, ctypes.c_void_p(addr), buf, 4, ctypes.byref(read)):
        _err("ReadProcessMemory")
    return struct.unpack_from("<i", buf.raw)[0]


def assemble64(function: int, ret_ptr: int, args: list[int], attach_fn: int | None, domain: int) -> bytes:
    code = bytearray()

    def mov_reg(rex: int, opcode: int, value: int) -> None:
        code.extend(bytes((rex, opcode)))
        code.extend(struct.pack("<Q", value & 0xFFFFFFFFFFFFFFFF))

    code.extend(b"\x48\x83\xEC\x28")
    if attach_fn:
        mov_reg(0x48, 0xB8, attach_fn)
        mov_reg(0x48, 0xB9, domain)
        code.extend(b"\xFF\xD0")
    mov_reg(0x48, 0xB8, function)
    if len(args) > 0:
        mov_reg(0x48, 0xB9, args[0])
    if len(args) > 1:
        mov_reg(0x48, 0xBA, args[1])
    if len(args) > 2:
        mov_reg(0x49, 0xB8, args[2])
    if len(args) > 3:
        mov_reg(0x49, 0xB9, args[3])
    code.extend(b"\xFF\xD0")
    code.extend(b"\x48\x83\xC4\x28")
    mov_reg(0x49, 0xBB, ret_ptr)
    code.extend(b"\x49\x89\x03")
    code.append(0xC3)
    return bytes(code)


def remote_call(handle: int, function: int, args: list[int], attach_fn: int | None, domain: int) -> int:
    ret_ptr = alloc_write(handle, b"\x00" * 8)
    stub = assemble64(function, ret_ptr, args, attach_fn, domain)
    code_ptr = alloc_write(handle, stub)
    thread = kernel32.CreateRemoteThread(handle, None, 0, ctypes.c_void_p(code_ptr), None, 0, None)
    if not thread:
        _err("CreateRemoteThread")
    wait = kernel32.WaitForSingleObject(thread, 15000)
    kernel32.CloseHandle(thread)
    if wait != 0:
        raise TimeoutError("remote mono call timed out")
    return read_i64(handle, ret_ptr)


def find_mono(handle: int) -> tuple[int, str]:
    mods = (ctypes.c_void_p * 1024)()
    needed = wintypes.DWORD()
    if not psapi.EnumProcessModulesEx(handle, ctypes.byref(mods), ctypes.sizeof(mods), ctypes.byref(needed), LIST_MODULES_ALL):
        _err("EnumProcessModulesEx")
    count = needed.value // ctypes.sizeof(ctypes.c_void_p)
    name = ctypes.create_unicode_buffer(1024)
    path = ctypes.create_unicode_buffer(1024)
    for i in range(count):
        module = mods[i]
        if not module:
            continue
        name.value = ""
        psapi.GetModuleBaseNameW(handle, ctypes.c_void_p(module), name, 1024)
        if name.value.lower() != "mono-2.0-bdwgc.dll":
            continue
        psapi.GetModuleFileNameExW(handle, ctypes.c_void_p(module), path, 1024)
        return int(module), path.value
    raise SystemExit("mono-2.0-bdwgc.dll not loaded")


def load_exports(remote_base: int, disk_path: str) -> dict[str, int]:
    import pefile

    pe = pefile.PE(disk_path, fast_load=True)
    pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_EXPORT"]])
    found: dict[str, int] = {}
    for symbol in pe.DIRECTORY_ENTRY_EXPORT.symbols:
        if not symbol.name:
            continue
        name = symbol.name.decode("ascii")
        if name in EXPORTS:
            found[name] = remote_base + symbol.address
    missing = [name for name in EXPORTS if name not in found]
    if missing:
        raise SystemExit("missing mono exports: " + ", ".join(missing))
    return found


def invoke(pid: int, dll_path: Path, class_name: str = "TfwrRunMain", method_name: str = "Load") -> int:
    handle = kernel32.OpenProcess(PROCESS_RIGHTS, False, pid)
    if not handle:
        _err("OpenProcess")
    try:
        mono_base, mono_path = find_mono(handle)
        exports = load_exports(mono_base, mono_path)
        domain = remote_call(handle, exports["mono_get_root_domain"], [], None, 0)
        if domain == 0:
            raise SystemExit("mono_get_root_domain returned 0")
        attach = exports["mono_thread_attach"]
        assembly = dll_path.read_bytes()
        status = alloc_write(handle, b"\x00\x00\x00\x00")
        image = remote_call(
            handle,
            exports["mono_image_open_from_data"],
            [alloc_write(handle, assembly), len(assembly), 1, status],
            attach,
            domain,
        )
        if image == 0 or read_i32(handle, status) != 0:
            raise SystemExit(f"mono_image_open_from_data failed status={read_i32(handle, status)}")
        fake = alloc_cstr(handle, f"TfwrRunMain-{dll_path.stat().st_mtime_ns}.dll")
        loaded = remote_call(
            handle,
            exports["mono_assembly_load_from_full"],
            [image, fake, status, 0],
            attach,
            domain,
        )
        if loaded == 0 or read_i32(handle, status) != 0:
            raise SystemExit(f"mono_assembly_load_from_full failed status={read_i32(handle, status)}")
        image2 = remote_call(handle, exports["mono_assembly_get_image"], [loaded], attach, domain)
        klass = remote_call(
            handle,
            exports["mono_class_from_name"],
            [image2, alloc_cstr(handle, ""), alloc_cstr(handle, class_name)],
            attach,
            domain,
        )
        if klass == 0:
            raise SystemExit(f"class not found: {class_name}")
        method = remote_call(
            handle,
            exports["mono_class_get_method_from_name"],
            [klass, alloc_cstr(handle, method_name), 0],
            attach,
            domain,
        )
        if method == 0:
            raise SystemExit(f"method not found: {method_name}")
        exc = alloc_write(handle, b"\x00" * 8)
        remote_call(handle, exports["mono_runtime_invoke"], [method, 0, 0, exc], attach, domain)
        if read_i64(handle, exc) != 0:
            raise SystemExit("mono_runtime_invoke threw")
        print(f"invoked {class_name}.{method_name} pid={pid}")
        return 0
    finally:
        kernel32.CloseHandle(handle)


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    pid = int(argv[argv.index("--pid") + 1]) if "--pid" in argv else 0
    default_dll = Path(__file__).with_name("tfwr-invoke") / "bin" / "TfwrBoot.dll"
    if not default_dll.is_file():
        default_dll = Path(__file__).with_name("tfwr-invoke") / "bin" / "TfwrRunMain.dll"
    dll = Path(argv[argv.index("--dll") + 1]) if "--dll" in argv else default_dll
    if pid <= 0:
        raise SystemExit("need --pid")
    if not dll.is_file():
        raise SystemExit(f"payload missing: {dll}")
    return invoke(pid, dll)


if __name__ == "__main__":
    sys.exit(main())
