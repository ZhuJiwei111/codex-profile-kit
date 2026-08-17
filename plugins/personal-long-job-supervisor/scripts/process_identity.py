#!/usr/bin/env python3
"""Cross-platform PID/start identity for Linux and macOS."""

from __future__ import annotations

import ctypes
import os
from pathlib import Path
import sys


class ProcessIdentityError(RuntimeError):
    pass


def _linux_identity(pid: int) -> dict | None:
    try:
        raw = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    except OSError as error:
        raise ProcessIdentityError(f"cannot inspect process {pid}: {error}") from error
    _, separator, tail = raw.rpartition(")")
    fields = tail.strip().split() if separator else []
    if len(fields) < 20:
        raise ProcessIdentityError(f"invalid /proc identity for process {pid}")
    return {"pid": pid, "start_ticks": int(fields[19]), "state_code": fields[0]}


class _ProcBSDInfo(ctypes.Structure):
    _fields_ = [
        ("pbi_flags", ctypes.c_uint32),
        ("pbi_status", ctypes.c_uint32),
        ("pbi_xstatus", ctypes.c_uint32),
        ("pbi_pid", ctypes.c_uint32),
        ("pbi_ppid", ctypes.c_uint32),
        ("pbi_uid", ctypes.c_uint32),
        ("pbi_gid", ctypes.c_uint32),
        ("pbi_ruid", ctypes.c_uint32),
        ("pbi_rgid", ctypes.c_uint32),
        ("pbi_svuid", ctypes.c_uint32),
        ("pbi_svgid", ctypes.c_uint32),
        ("rfu_1", ctypes.c_uint32),
        ("pbi_comm", ctypes.c_char * 16),
        ("pbi_name", ctypes.c_char * 32),
        ("pbi_nfiles", ctypes.c_uint32),
        ("pbi_pgid", ctypes.c_uint32),
        ("pbi_pjobc", ctypes.c_uint32),
        ("e_tdev", ctypes.c_uint32),
        ("e_tpgid", ctypes.c_uint32),
        ("pbi_nice", ctypes.c_int32),
        ("pbi_start_tvsec", ctypes.c_uint64),
        ("pbi_start_tvusec", ctypes.c_uint64),
    ]


def _darwin_identity(pid: int) -> dict | None:
    try:
        library = ctypes.CDLL("/usr/lib/libproc.dylib", use_errno=True)
    except OSError as error:
        raise ProcessIdentityError(f"cannot load macOS libproc: {error}") from error
    library.proc_pidinfo.argtypes = [
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_uint64,
        ctypes.c_void_p,
        ctypes.c_int,
    ]
    library.proc_pidinfo.restype = ctypes.c_int
    info = _ProcBSDInfo()
    size = ctypes.sizeof(info)
    written = library.proc_pidinfo(pid, 3, 0, ctypes.byref(info), size)
    if written == 0:
        error_number = ctypes.get_errno()
        if error_number in (0, 3):
            return None
        raise ProcessIdentityError(
            f"cannot inspect process {pid} through macOS libproc: errno {error_number}"
        )
    if written != size or int(info.pbi_pid) != pid:
        raise ProcessIdentityError(f"invalid macOS process identity for process {pid}")
    state_code = {1: "I", 2: "R", 3: "S", 4: "T", 5: "Z"}.get(
        int(info.pbi_status), "X"
    )
    start_ticks = int(info.pbi_start_tvsec) * 1_000_000 + int(
        info.pbi_start_tvusec
    )
    if start_ticks <= 0:
        raise ProcessIdentityError(f"invalid macOS start time for process {pid}")
    return {"pid": pid, "start_ticks": start_ticks, "state_code": state_code}


def process_identity(pid: int | None = None) -> dict | None:
    pid = int(pid or os.getpid())
    if sys.platform.startswith("linux"):
        return _linux_identity(pid)
    if sys.platform == "darwin":
        return _darwin_identity(pid)
    raise ProcessIdentityError(f"unsupported process identity platform: {sys.platform}")


def require_process_identity(pid: int | None = None) -> dict:
    identity = process_identity(pid)
    if identity is None:
        raise ProcessIdentityError(f"process identity is unavailable for {pid}")
    return identity


def main() -> int:
    try:
        identity = require_process_identity()
    except ProcessIdentityError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"process identity available: pid={identity['pid']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
