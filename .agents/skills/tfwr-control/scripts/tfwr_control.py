#!/usr/bin/env python3
"""Watch TFWR output, send in-game hotkeys, extract the public script API."""

from __future__ import annotations

import argparse
import ctypes
import json
import os
import re
import subprocess
import sys
import time
from ctypes import wintypes
from datetime import datetime, timezone
from pathlib import Path

STEAM_APP_ID = "2060160"
DEFAULT_GAME = Path(r"D:\Program Files (x86)\Steam\steamapps\common\The Farmer Was Replaced")
WINDOW_HINTS = ("The Farmer Was Replaced", "编程农场")
MAIN_MARK = "TFWR_RUN_MAIN"

STATUS_PREFIXES = (
    ("boot main", "info", "main 已启动农场圈"),
    ("dino", "info", "恐龙摘帽：苹果数 步数"),
    ("sun_tier", "info", "向日葵开始收一个花瓣档"),
    ("sun_wait", "wait", "当前最大档还没熟；应施肥催熟，不要放锁补种"),
    ("sun_unlock", "info", "向日葵放锁，下一波可以换作物"),
    ("sun_skip", "info", "向日葵表不齐，跳过连收"),
    ("cactus_skip", "info", "仙人掌已齐却还没排好"),
    ("maze:", "info", "迷宫停机原因"),
)

USER32 = ctypes.windll.user32 if os.name == "nt" else None
KERNEL32 = ctypes.windll.kernel32 if os.name == "nt" else None
VK_F5 = 0x74
VK_SHIFT = 0x10
VK_CONTROL = 0x11
VK_MENU = 0x12
VK_ESCAPE = 0x1B
VK_F = 0x46
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004
INPUT_KEYBOARD = 1
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
PW_RENDERFULLCONTENT = 2
ULONG_PTR = ctypes.c_ulonglong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_ulong


class KEYBDINPUT(ctypes.Structure):
    _fields_ = (
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    )


class MOUSEINPUT(ctypes.Structure):
    _fields_ = (
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    )


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = (
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    )


class INPUTUNION(ctypes.Union):
    _fields_ = (("ki", KEYBDINPUT), ("mi", MOUSEINPUT), ("hi", HARDWAREINPUT))


class INPUT(ctypes.Structure):
    _fields_ = (("type", wintypes.DWORD), ("union", INPUTUNION))


def find_save_root(start: Path | None = None) -> Path:
    env = os.environ.get("TFWR_SAVE")
    if env:
        return Path(env)
    here = start or Path.cwd()
    for candidate in (here, *here.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / "Saves" / "Save0").is_dir():
            return candidate
    script_dir = Path(__file__).resolve()
    for candidate in script_dir.parents:
        if (candidate / "AGENTS.md").is_file() and (candidate / "Saves" / "Save0").is_dir():
            return candidate
    raise SystemExit("找不到存档根（需要 AGENTS.md 和 Saves/Save0）")


def parse_game_root_from_log(player_log: Path) -> Path | None:
    if not player_log.is_file():
        return None
    text = player_log.read_text(encoding="utf-8", errors="ignore")
    match = re.search(r"Mono path\[0\] = '([^']+)'", text)
    if not match:
        return None
    managed = Path(match.group(1))
    data = managed.parent
    if data.name.endswith("_Data"):
        return data.parent
    return None


def find_game_root(save_root: Path) -> Path:
    env = os.environ.get("TFWR_GAME")
    if env and Path(env).is_dir():
        return Path(env)
    from_log = parse_game_root_from_log(save_root / "Player.log")
    if from_log and from_log.is_dir():
        return from_log
    if DEFAULT_GAME.is_dir():
        return DEFAULT_GAME
    raise SystemExit("找不到游戏安装目录。可设环境变量 TFWR_GAME")


def iter_error_files(game_root: Path) -> list[Path]:
    strings = game_root / "TheFarmerWasReplaced_Data" / "StreamingAssets" / "Languages" / "ZH" / "Strings"
    files = []
    for name in ("execute_errors.txt", "parse_errors.txt", "warnings.txt"):
        path = strings / name
        if path.is_file():
            files.append(path)
    return files


def load_error_needles(game_root: Path | None) -> list[tuple[str, str, str]]:
    needles: list[tuple[str, str, str]] = []
    if game_root is None:
        return needles
    for path in iter_error_files(game_root):
        kind = "parse" if "parse" in path.name else "warning" if "warning" in path.name else "execute"
        for raw in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = raw.strip()
            if not line.startswith("@error_"):
                continue
            if " = " not in line:
                continue
            key, body = line.split(" = ", 1)
            key = key[1:]
            text = re.sub(r"\{[0-9]+\}", " ", body)
            text = re.sub(r"`[^`]+`", " ", text)
            text = re.sub(r"\s+", " ", text).strip()
            if len(text) < 8:
                continue
            needles.append((key, kind, text[:48]))
    needles.sort(key=lambda item: -len(item[2]))
    return needles


def classify_line(line: str, needles: list[tuple[str, str, str]]) -> dict:
    stripped = line.strip()
    if not stripped:
        return {"severity": "empty", "code": "empty", "line": line, "hint": ""}
    for prefix, severity, hint in STATUS_PREFIXES:
        if stripped.startswith(prefix):
            return {"severity": severity, "code": prefix.rstrip(":"), "line": stripped, "hint": hint}
    for key, kind, needle in needles:
        if needle and needle in stripped:
            return {"severity": "error", "code": key, "line": stripped, "hint": kind}
    if any(token in stripped for token in ("从未被定义", "不存在具有此名称的模块", "语法错误", "缩进", "报错", "Error", "Traceback")):
        return {"severity": "error", "code": "unlisted", "line": stripped, "hint": "interpreter"}
    return {"severity": "unknown", "code": "unknown", "line": stripped, "hint": "未识别，先当日志"}


def parse_output(save_root: Path, game_root: Path | None) -> dict:
    output = save_root / "output.txt"
    text = ""
    if output.is_file():
        text = output.read_text(encoding="utf-8", errors="replace")
    needles = load_error_needles(game_root)
    lines = text.splitlines()
    events = [classify_line(line, needles) for line in lines if line.strip()]
    errors = [item for item in events if item["severity"] == "error"]
    waits = [item for item in events if item["severity"] == "wait"]
    report = {
        "ok": len(errors) == 0,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "output_path": str(output),
        "line_count": len(lines),
        "error_count": len(errors),
        "wait_count": len(waits),
        "events": events,
        "errors": errors,
        "waits": waits,
    }
    return report


def write_report(save_root: Path, report: dict) -> tuple[Path, Path]:
    dest = save_root / ".agents" / "error-iter"
    dest.mkdir(parents=True, exist_ok=True)
    json_path = dest / "last.json"
    md_path = dest / "last.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# TFWR output",
        "",
        f"- 时间：{report['generated_at']}",
        f"- 行数：{report['line_count']}",
        f"- 解释器/解析错误：{report['error_count']}",
        f"- 等待类日志：{report['wait_count']}",
        "",
    ]
    if report["errors"]:
        lines.append("## 必须修")
        for item in report["errors"]:
            lines.append(f"- `{item['code']}` {item['line']}")
        lines.append("")
    if report["waits"]:
        lines.append("## 等待（不是红字）")
        for item in report["waits"]:
            lines.append(f"- {item['line']} — {item['hint']}")
        lines.append("")
    if report["events"]:
        lines.append("## 全部")
        for item in report["events"]:
            lines.append(f"- [{item['severity']}] `{item['code']}` {item['line']}")
        lines.append("")
    else:
        lines.append("output.txt 是空的。空文件不能当成没报错。")
        lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, md_path


def cmd_parse(save_root: Path, game_root: Path | None) -> int:
    report = parse_output(save_root, game_root)
    json_path, md_path = write_report(save_root, report)
    print(md_path.read_text(encoding="utf-8"), end="")
    print(f"JSON: {json_path}")
    if report["error_count"]:
        return 2
    return 0


def cmd_watch(save_root: Path, game_root: Path | None) -> int:
    output = save_root / "output.txt"
    last = None
    print(f"watching {output}")
    while True:
        stamp = None
        if output.is_file():
            stat = output.stat()
            stamp = (stat.st_mtime_ns, stat.st_size)
        if stamp != last:
            last = stamp
            cmd_parse(save_root, game_root)
            print("---")
        time.sleep(0.5)


def enum_windows() -> list[tuple[int, str]]:
    if USER32 is None:
        return []
    found: list[tuple[int, str]] = []

    @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    def callback(hwnd, _lp):
        if USER32.IsWindowVisible(hwnd):
            length = USER32.GetWindowTextLengthW(hwnd)
            buf = ctypes.create_unicode_buffer(length + 1)
            USER32.GetWindowTextW(hwnd, buf, length + 1)
            title = buf.value
            if title:
                found.append((int(hwnd), title))
        return True

    USER32.EnumWindows(callback, 0)
    return found


def process_image(hwnd: int) -> str:
    if USER32 is None:
        return ""
    pid = ctypes.c_ulong()
    USER32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    if pid.value == 0:
        return ""
    kernel32 = ctypes.windll.kernel32
    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    handle = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid.value)
    if not handle:
        return ""
    try:
        buf = ctypes.create_unicode_buffer(32768)
        size = ctypes.c_ulong(len(buf))
        if kernel32.QueryFullProcessImageNameW(handle, 0, buf, ctypes.byref(size)):
            return buf.value
    finally:
        kernel32.CloseHandle(handle)
    return ""


def find_game_hwnd() -> tuple[int, str] | None:
    windows = enum_windows()
    for hwnd, title in windows:
        if any(hint.lower() in title.lower() for hint in WINDOW_HINTS):
            return hwnd, title
    for hwnd, title in windows:
        image = process_image(hwnd).replace("/", "\\").lower()
        if image.endswith("thefarmerwasreplaced.exe"):
            return hwnd, title or image
    return None


def require_game() -> tuple[int, str]:
    found = find_game_hwnd()
    if found is None:
        raise SystemExit("没找到游戏窗口。先开游戏并进到存档编辑器。")
    return found


def focus_hwnd(hwnd: int) -> None:
    if USER32 is None or KERNEL32 is None:
        return
    USER32.ShowWindow(hwnd, 9)
    fg = USER32.GetForegroundWindow()
    cur_tid = KERNEL32.GetCurrentThreadId()
    fg_tid = USER32.GetWindowThreadProcessId(fg, None)
    target_tid = USER32.GetWindowThreadProcessId(hwnd, None)
    if fg_tid:
        USER32.AttachThreadInput(cur_tid, fg_tid, True)
    if target_tid and target_tid != fg_tid:
        USER32.AttachThreadInput(cur_tid, target_tid, True)
    USER32.keybd_event(VK_MENU, 0, 0, 0)
    USER32.keybd_event(VK_MENU, 0, KEYEVENTF_KEYUP, 0)
    USER32.BringWindowToTop(hwnd)
    USER32.SetForegroundWindow(hwnd)
    if fg_tid:
        USER32.AttachThreadInput(cur_tid, fg_tid, False)
    if target_tid and target_tid != fg_tid:
        USER32.AttachThreadInput(cur_tid, target_tid, False)
    time.sleep(0.18)


def send_key(vk: int, down: bool) -> None:
    if USER32 is None:
        raise SystemExit("热键只在 Windows 上可用")
    inp = INPUT()
    inp.type = INPUT_KEYBOARD
    inp.union.ki.wVk = vk
    inp.union.ki.wScan = 0
    inp.union.ki.dwFlags = 0 if down else KEYEVENTF_KEYUP
    inp.union.ki.time = 0
    inp.union.ki.dwExtraInfo = 0
    USER32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))


def tap(vk: int) -> None:
    send_key(vk, True)
    time.sleep(0.03)
    send_key(vk, False)


def combo(modifiers: tuple[int, ...], vk: int) -> None:
    for key in modifiers:
        send_key(key, True)
        time.sleep(0.02)
    tap(vk)
    time.sleep(0.02)
    for key in reversed(modifiers):
        send_key(key, False)
        time.sleep(0.02)


def type_text(text: str) -> None:
    if USER32 is None:
        raise SystemExit("热键只在 Windows 上可用")
    for ch in text:
        inp = INPUT()
        inp.type = INPUT_KEYBOARD
        inp.union.ki.wVk = 0
        inp.union.ki.wScan = ord(ch)
        inp.union.ki.dwFlags = KEYEVENTF_UNICODE
        inp.union.ki.time = 0
        inp.union.ki.dwExtraInfo = 0
        USER32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))
        inp.union.ki.dwFlags = KEYEVENTF_UNICODE | KEYEVENTF_KEYUP
        USER32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))
        time.sleep(0.012)


def error_iter_dir(save_root: Path) -> Path:
    dest = save_root / ".agents" / "error-iter"
    dest.mkdir(parents=True, exist_ok=True)
    return dest


def capture_hwnd(hwnd: int, dest: Path) -> Path:
    try:
        import win32con
        import win32gui
        import win32ui
        from PIL import Image
    except ImportError as exc:
        raise SystemExit(f"截图需要 pywin32 和 Pillow：{exc}") from exc
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    width = max(1, right - left)
    height = max(1, bottom - top)
    hwnd_dc = win32gui.GetWindowDC(hwnd)
    src_dc = win32ui.CreateDCFromHandle(hwnd_dc)
    mem_dc = src_dc.CreateCompatibleDC()
    bitmap = win32ui.CreateBitmap()
    bitmap.CreateCompatibleBitmap(src_dc, width, height)
    mem_dc.SelectObject(bitmap)
    USER32.PrintWindow(hwnd, mem_dc.GetSafeHdc(), PW_RENDERFULLCONTENT)
    info = bitmap.GetInfo()
    bits = bitmap.GetBitmapBits(True)
    image = Image.frombuffer(
        "RGB",
        (info["bmWidth"], info["bmHeight"]),
        bits,
        "raw",
        "BGRX",
        0,
        1,
    )
    dest.parent.mkdir(parents=True, exist_ok=True)
    image.save(dest)
    win32gui.DeleteObject(bitmap.GetHandle())
    mem_dc.DeleteDC()
    src_dc.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwnd_dc)
    return dest


def cmd_screenshot(save_root: Path, name: str = "game-view") -> int:
    hwnd, title = require_game()
    focus_hwnd(hwnd)
    dest = error_iter_dir(save_root) / f"{name}.png"
    capture_hwnd(hwnd, dest)
    print(f"screenshot {title} -> {dest}")
    return 0


def emit_hotkey(action: str) -> None:
    if action == "play":
        tap(VK_F5)
    elif action == "stop":
        combo((VK_SHIFT,), VK_F5)
    elif action == "pause":
        combo((VK_CONTROL,), VK_F5)
    elif action == "search":
        combo((VK_CONTROL,), VK_F)
    else:
        raise SystemExit(f"未知热键 {action}")


def send_hotkey(action: str) -> None:
    hwnd, title = require_game()
    focus_hwnd(hwnd)
    emit_hotkey(action)
    print(f"{action} -> {title}")


def invoke_dir() -> Path:
    return Path(__file__).resolve().parent / "tfwr-invoke"


def ensure_invoke_built() -> tuple[Path, Path]:
    root = invoke_dir()
    exe = root / "bin" / "tfwr-invoke.exe"
    dll = root / "bin" / "TfwrBoot.dll"
    if not dll.is_file():
        dll = root / "bin" / "TfwrRunMain.dll"
    if exe.is_file() and dll.is_file() and dll.stat().st_mtime >= (root / "TfwrRunMain.cs").stat().st_mtime:
        return exe, dll
    payload = subprocess.run(
        ["dotnet", "build", str(root / "TfwrRunMain.csproj"), "-c", "Release"],
        check=False,
        capture_output=True,
        text=True,
    )
    injector = subprocess.run(
        ["dotnet", "build", str(root / "TfwrInjector.csproj"), "-c", "Release"],
        check=False,
        capture_output=True,
        text=True,
    )
    if payload.returncode != 0 or injector.returncode != 0 or not exe.is_file() or not dll.is_file():
        raise SystemExit(
            "编译 tfwr-invoke 失败。\n"
            + (payload.stdout or "")
            + (payload.stderr or "")
            + (injector.stdout or "")
            + (injector.stderr or "")
        )
    return exe, dll


ITEM_VALUE = {
    "hay": 2,
    "wood": 8,
    "carrot": 40,
    "pumpkin": 80,
    "power": 40,
    "cactus": 80,
    "bone": 80,
    "weird_substance": 80,
    "gold": 80,
    "water": 0,
    "fertilizer": 0,
}


def game_pid() -> int:
    found = find_game_hwnd()
    if found is None:
        raise SystemExit("没找到游戏窗口。先开游戏并进到存档。")
    pid = ctypes.c_ulong()
    USER32.GetWindowThreadProcessId(found[0], ctypes.byref(pid))
    if not pid.value:
        raise SystemExit("拿不到游戏进程 PID")
    return int(pid.value)


def invoke_game_command(save_root: Path, command: str, wait: float = 1.2) -> int:
    dest = error_iter_dir(save_root)
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "run-target.txt").write_text(command, encoding="utf-8")
    _exe, dll = ensure_invoke_built()
    invoke_py = Path(__file__).resolve().parent / "tfwr_mono_invoke.py"
    cmd = [sys.executable, str(invoke_py), "--pid", str(game_pid()), "--dll", str(dll)]
    print(f"invoke {command}")
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        print(f"tfwr-invoke exit {result.returncode}")
        return result.returncode
    time.sleep(wait)
    log_path = dest / "run-main-invoke.log"
    if log_path.is_file():
        lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
        if lines:
            print(lines[-1])
    return 0


def wealth_of(items: dict) -> dict:
    parts = {}
    total = 0.0
    for name, qty in items.items():
        value = ITEM_VALUE.get(name)
        if value is None:
            continue
        score = float(qty) * value
        parts[name] = {"qty": float(qty), "value": value, "wealth": score}
        total += score
    return {"total": total, "parts": parts}


def write_snapshot_report(save_root: Path, snap: dict) -> Path:
    dest = error_iter_dir(save_root)
    wealth = wealth_of(snap.get("items") or {})
    prev_path = dest / "snapshot-prev.json"
    prev = None
    if prev_path.is_file():
        try:
            prev = json.loads(prev_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            prev = None
    lines = [
        "# TFWR runtime snapshot",
        "",
        f"- 时间：{snap.get('taken_at')}",
        f"- 执行中：{snap.get('executing')}",
        f"- 模拟秒：{snap.get('sim_seconds')}",
        f"- TimeFactor：{snap.get('time_factor')}",
        f"- 田：{snap.get('world_x')}x{snap.get('world_y')}",
        f"- 资产合计：{wealth['total']:.0f}",
        "",
    ]
    sim = snap.get("sim") or {}
    if sim:
        lines.extend(
            [
                "## 效率",
                "",
                f"- SpeedFactor：{sim.get('speed_factor')}",
                f"- 无人机：{sim.get('drone_count')}",
                f"- UsedPower：{sim.get('used_power')}",
                f"- 暂停：{sim.get('paused')} 单步：{sim.get('step_by_step')}",
                f"- 当前节点：{sim.get('current_node')}",
                "",
            ]
        )
        drones = sim.get("drones") or []
        if drones:
            lines.append("无人机位置：")
            for drone in drones:
                lines.append(
                    f"- id {drone.get('id')} ({drone.get('x')},{drone.get('y')}) hat={drone.get('hat')}"
                )
            lines.append("")
    stack = snap.get("call_stack") or []
    if stack:
        lines.append("## 调用栈")
        lines.append("")
        for frame in stack:
            lines.append(f"- {frame.get('func')} @ {frame.get('call')}")
        lines.append("")
    lines.append("## 库存 / 资产")
    lines.append("")
    for name, part in sorted(wealth["parts"].items(), key=lambda item: item[1]["wealth"]):
        lines.append(f"- {name}: {part['qty']:.2f} × {part['value']} = {part['wealth']:.0f}")
    lines.append("")
    if prev:
        dt = float(snap.get("sim_seconds") or 0) - float(prev.get("sim_seconds") or 0)
        prev_wealth = wealth_of(prev.get("items") or {})
        dw = wealth["total"] - prev_wealth["total"]
        lines.append("## 相对上一帧")
        lines.append("")
        lines.append(f"- Δ模拟秒：{dt:.3f}")
        lines.append(f"- Δ资产：{dw:.0f}")
        if dt > 0.05:
            lines.append(f"- 资产/秒：{dw / dt:.1f}")
        prev_items = prev.get("items") or {}
        for name in sorted(set(prev_items) | set(snap.get("items") or {})):
            before = float(prev_items.get(name) or 0)
            after = float((snap.get("items") or {}).get(name) or 0)
            if abs(after - before) >= 0.01:
                lines.append(f"- {name}: {before:.2f} → {after:.2f} ({after - before:+.2f})")
        lines.append("")
    output = snap.get("output") or ""
    if output.strip():
        lines.append("## Logger")
        lines.append("")
        lines.append("```")
        lines.append(output.strip()[-1200:])
        lines.append("```")
        lines.append("")
    md_path = dest / "snapshot.md"
    md_path.write_text("\n".join(lines), encoding="utf-8")
    (dest / "snapshot-prev.json").write_text(json.dumps(snap, ensure_ascii=False), encoding="utf-8")
    return md_path


def cmd_run_main(save_root: Path, file_name: str = "main") -> int:
    if file_name == "main_maze":
        raise SystemExit("run-main 默认只启动农场入口 main，不要拿它跑 main_maze。")
    code = invoke_game_command(save_root, file_name, wait=1.6)
    output = save_root / "output.txt"
    if output.is_file():
        text = output.read_text(encoding="utf-8", errors="replace")
        print("output.txt:")
        print(text[-400:] if text else "(empty)")
    return code


def cmd_snapshot(save_root: Path) -> int:
    dest = error_iter_dir(save_root)
    snap_path = dest / "snapshot.json"
    before = snap_path.stat().st_mtime_ns if snap_path.is_file() else 0
    code = invoke_game_command(save_root, "snapshot", wait=0.8)
    if code != 0:
        return code
    if not snap_path.is_file() or snap_path.stat().st_mtime_ns == before:
        print("snapshot.json 没有更新。游戏可能没进存档，或主线程还没跑到。")
        return 2
    snap = json.loads(snap_path.read_text(encoding="utf-8"))
    md_path = write_snapshot_report(save_root, snap)
    print(md_path.read_text(encoding="utf-8"), end="")
    return 0 if snap.get("ok") else 2


def cmd_stop_internal(save_root: Path) -> int:
    return invoke_game_command(save_root, "stop", wait=0.4)


def cmd_restart(save_root: Path) -> int:
    return cmd_run_main(save_root)


def cmd_status(save_root: Path, game_root: Path | None) -> int:
    found = find_game_hwnd()
    output = save_root / "output.txt"
    print(f"save: {save_root}")
    print(f"game: {game_root}")
    print(f"window: {found[1] if found else 'not found'}")
    if output.is_file():
        print(f"output: {output} ({output.stat().st_size} bytes)")
    else:
        print("output: missing")
    return 0


def extract_builtins(builtins_path: Path) -> dict:
    text = builtins_path.read_text(encoding="utf-8", errors="replace")
    functions = sorted(set(re.findall(r"^def ([A-Za-z_][A-Za-z0-9_]*)\(", text, flags=re.M)))
    enums: dict[str, list[str]] = {}
    current = None
    for line in text.splitlines():
        class_match = re.match(r"^class (Entities|Items|Hats|Unlocks|Grounds|Leaderboards)\b", line)
        if class_match:
            current = class_match.group(1)
            enums.setdefault(current, [])
            continue
        member = re.match(r"^[\t ]+([A-Za-z_][A-Za-z0-9_]*):", line)
        if current and member:
            name = member.group(1)
            if name.startswith("_"):
                continue
            if name not in enums[current]:
                enums[current].append(name)
        if line.startswith("class ") and current and not class_match:
            current = None
    return {"functions": functions, "enums": enums, "source": str(builtins_path)}


def cmd_extract_api(save_root: Path, game_root: Path) -> int:
    lang = game_root / "TheFarmerWasReplaced_Data" / "StreamingAssets" / "Languages"
    builtins_path = lang / "builtins.py"
    if not builtins_path.is_file():
        raise SystemExit(f"没有官方桩：{builtins_path}")
    api = extract_builtins(builtins_path)
    dest_dir = save_root / ".agents" / "skills" / "tfwr-control" / "references"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / "game-api.md"
    sunflower = lang / "ZH" / "docs" / "unlocks" / "sunflowers.md"
    megafarm = lang / "ZH" / "docs" / "unlocks" / "megafarm.md"
    notes = []
    if sunflower.is_file():
        notes.append("向日葵：至少 10 朵且收当前最大花瓣是 **8 倍**。田里还有更高花瓣时收低档，后面也没倍数。未熟就能 `measure()`。")
    if megafarm.is_file():
        notes.append("多无人机：内存各自一份拷贝。列表当参数传进去也是拷贝。列结果必须 `wait_for` 交回。`spawn_drone` 官方可以带额外参数，本存档仍用无参工厂闭包。")
    lines = [
        "# TFWR 公开脚本 API",
        "",
        "从游戏安装目录抽出，不是把 `Core.dll` 整份反编译成逻辑源码。",
        f"来源：`{builtins_path}`",
        "",
        "## 行为要点",
        "",
    ]
    for note in notes:
        lines.append(f"- {note}")
    lines.extend(["", "## 函数", ""])
    for name in api["functions"]:
        lines.append(f"- `{name}`")
    lines.extend(["", "## 枚举", ""])
    for enum_name, members in api["enums"].items():
        lines.append(f"### {enum_name}")
        lines.append("")
        for member in members:
            lines.append(f"- `{member}`")
        lines.append("")
    dest.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {dest}")
    print(f"functions: {len(api['functions'])}")
    return 0


def cmd_launch(game_root: Path) -> int:
    exe = game_root / "TheFarmerWasReplaced.exe"
    if find_game_hwnd() is not None:
        print("game already running")
        return 0
    steam = f"steam://rungameid/{STEAM_APP_ID}"
    try:
        os.startfile(steam)  # type: ignore[attr-defined]
        print(f"launch {steam}")
        return 0
    except OSError:
        if exe.is_file():
            os.startfile(exe)  # type: ignore[attr-defined]
            print(f"launch {exe}")
            return 0
        raise SystemExit("无法启动游戏")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="TFWR output / 热键 / API")
    parser.add_argument(
        "command",
        choices=(
            "parse",
            "watch",
            "play",
            "stop",
            "pause",
            "restart",
            "run-main",
            "snapshot",
            "screenshot",
            "status",
            "extract-api",
            "launch",
            "cycle",
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    args = build_parser().parse_args(argv)
    save_root = find_save_root()
    game_root = None
    try:
        game_root = find_game_root(save_root)
    except SystemExit:
        if args.command in {"extract-api", "launch"}:
            raise
    if args.command == "parse":
        return cmd_parse(save_root, game_root)
    if args.command == "cycle":
        return cmd_parse(save_root, game_root)
    if args.command == "watch":
        return cmd_watch(save_root, game_root)
    if args.command == "status":
        return cmd_status(save_root, game_root)
    if args.command == "extract-api":
        return cmd_extract_api(save_root, game_root)
    if args.command == "launch":
        return cmd_launch(game_root or find_game_root(save_root))
    if args.command == "screenshot":
        return cmd_screenshot(save_root)
    if args.command in {"restart", "run-main"}:
        return cmd_run_main(save_root)
    if args.command == "snapshot":
        return cmd_snapshot(save_root)
    if args.command == "play":
        print("警告：play 只 F5 当前焦点窗口，不等于启动 main。农场请用 run-main。")
        send_hotkey(args.command)
        return 0
    if args.command == "stop":
        return cmd_stop_internal(save_root)
    if args.command == "pause":
        send_hotkey(args.command)
        return 0
    raise SystemExit(args.command)


if __name__ == "__main__":
    sys.exit(main())
