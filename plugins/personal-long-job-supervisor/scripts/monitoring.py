"""Strict monitor configuration, capability discovery, and worker-side sampling."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
import shutil
import subprocess
import time

from durable import append_event, locked_events, utc_now


class MonitorError(RuntimeError):
    pass


AUTHORITY = (
    "attention requests inspection only; preserve the original task authority and do not "
    "cancel, retry, restart, signal, reconfigure, or change parameters automatically"
)
KINDS = ("gpu_process_idle", "disk_free", "heartbeat_stale")


def _run(command: list[str], timeout: float = 5) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(
            command, text=True, capture_output=True, check=False, timeout=timeout
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise MonitorError(str(error)) from error


class NvidiaAdapter:
    """NVIDIA process-attributed samples; aggregate device utilization is never used."""

    def __init__(self, executable: str | None = None):
        self.executable = executable or shutil.which("nvidia-smi")

    def devices(self) -> list[dict]:
        if not self.executable:
            raise MonitorError("nvidia-smi is unavailable")
        result = _run(
            [
                self.executable,
                "--query-gpu=index,uuid,name",
                "--format=csv,noheader,nounits",
            ]
        )
        if result.returncode:
            raise MonitorError((result.stderr or result.stdout).strip()[:512])
        devices = []
        try:
            for line in result.stdout.splitlines():
                index, uuid, name = (part.strip() for part in line.split(",", 2))
                devices.append({"index": int(index), "uuid": uuid, "name": name})
        except (TypeError, ValueError) as error:
            raise MonitorError("nvidia-smi returned invalid device metadata") from error
        if not devices:
            raise MonitorError("nvidia-smi reported no visible devices")
        return devices

    def process_sample(self, target_pids: set[int]) -> dict[int, float]:
        if not self.executable:
            raise MonitorError("nvidia-smi is unavailable")
        result = _run([self.executable, "pmon", "-c", "1", "-s", "u"])
        if result.returncode:
            raise MonitorError((result.stderr or result.stdout).strip()[:512])
        utilization: dict[int, float] = {}
        try:
            for line in result.stdout.splitlines():
                stripped = line.strip()
                if not stripped or stripped.startswith("#"):
                    continue
                fields = stripped.split()
                if len(fields) < 4 or fields[1] == "-":
                    continue
                gpu_index, pid = int(fields[0]), int(fields[1])
                if pid not in target_pids:
                    continue
                sm = 0.0 if fields[3] == "-" else float(fields[3])
                utilization[gpu_index] = min(100.0, utilization.get(gpu_index, 0.0) + sm)
        except (TypeError, ValueError) as error:
            raise MonitorError("nvidia-smi pmon returned invalid process data") from error
        return utilization


def discover_capabilities(adapter: NvidiaAdapter | None = None) -> dict:
    adapter = adapter or NvidiaAdapter()
    linux = os.name == "posix" and Path("/proc/self/stat").is_file()
    gpu = {
        "available": False,
        "provider": "nvidia-smi",
        "process_attribution": False,
        "devices": [],
    }
    gap = None
    if linux:
        try:
            devices = adapter.devices()
            adapter.process_sample(set())
            gpu.update(available=True, process_attribution=True, devices=devices)
        except MonitorError as error:
            gap = str(error)[:512]
    else:
        gap = "Linux procfs is required"
    if gap:
        gpu["evidence_gap"] = gap
    return {
        "schema_version": 1,
        "platform": "linux" if linux else "unsupported",
        "procfs": linux,
        "monitors": {
            "gpu_process_idle": gpu,
            "disk_free": {"available": linux, "provider": "statvfs"},
            "heartbeat_stale": {"available": linux, "provider": "stat"},
        },
    }


def _number(value, field: str, *, minimum=0, maximum=None, strictly=False) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise MonitorError(f"{field} must be a number")
    number = float(value)
    if (strictly and number <= minimum) or (not strictly and number < minimum):
        relation = "greater than" if strictly else "at least"
        raise MonitorError(f"{field} must be {relation} {minimum}")
    if maximum is not None and number > maximum:
        raise MonitorError(f"{field} must be at most {maximum}")
    return number


def _keys(config: dict, required: set[str], optional: set[str]) -> None:
    missing = required - config.keys()
    unknown = config.keys() - required - optional
    if missing:
        raise MonitorError(f"missing monitor fields: {sorted(missing)}")
    if unknown:
        raise MonitorError(f"unknown monitor fields: {sorted(unknown)}")


def normalize_monitors(
    raw_configs: list[str | dict], cwd: Path, adapter: NvidiaAdapter | None = None
) -> list[dict]:
    adapter = adapter or NvidiaAdapter()
    parsed = []
    seen = set()
    for position, raw in enumerate(raw_configs, 1):
        try:
            config = json.loads(raw) if isinstance(raw, str) else dict(raw)
        except (json.JSONDecodeError, TypeError, ValueError) as error:
            raise MonitorError(f"monitor {position} must be a JSON object: {error}") from error
        if not isinstance(config, dict) or config.get("kind") not in KINDS:
            raise MonitorError(f"monitor {position} has unsupported kind")
        kind = config["kind"]
        if kind in seen:
            raise MonitorError(f"duplicate monitor kind: {kind}")
        seen.add(kind)
        monitor_id = f"m{position}"
        if kind == "gpu_process_idle":
            _keys(
                config,
                {"kind", "devices", "utilization_below_percent", "duration_seconds", "startup_grace_seconds"},
                {"mode", "sample_interval_seconds"},
            )
            devices_input = config["devices"]
            if not isinstance(devices_input, list) or not devices_input:
                raise MonitorError("devices must be a non-empty array")
            available = adapter.devices()
            by_index = {item["index"]: item for item in available}
            by_uuid = {item["uuid"]: item for item in available}
            devices = []
            for requested in devices_input:
                device = by_index.get(requested) if isinstance(requested, int) else by_uuid.get(requested)
                if not device:
                    raise MonitorError(f"unknown or unavailable NVIDIA device: {requested}")
                if device["uuid"] not in {item["uuid"] for item in devices}:
                    devices.append(device)
            adapter.process_sample(set())
            mode = config.get("mode", "any")
            if mode not in ("any", "all"):
                raise MonitorError("mode must be 'any' or 'all'")
            parsed.append(
                {
                    "monitor_id": monitor_id,
                    "kind": kind,
                    "devices": devices,
                    "mode": mode,
                    "utilization_below_percent": _number(config["utilization_below_percent"], "utilization_below_percent", strictly=True, maximum=100),
                    "duration_seconds": _number(config["duration_seconds"], "duration_seconds", strictly=True),
                    "startup_grace_seconds": _number(config["startup_grace_seconds"], "startup_grace_seconds"),
                    "sample_interval_seconds": _number(config.get("sample_interval_seconds", 10), "sample_interval_seconds", strictly=True, maximum=300),
                }
            )
        elif kind == "disk_free":
            _keys(
                config,
                {"kind", "paths", "duration_seconds"},
                {"available_below_gib", "available_below_percent", "sample_interval_seconds"},
            )
            paths = config["paths"]
            if not isinstance(paths, list) or not paths or not all(isinstance(path, str) and path for path in paths):
                raise MonitorError("paths must be a non-empty string array")
            if "available_below_gib" not in config and "available_below_percent" not in config:
                raise MonitorError("disk_free requires an absolute or percentage threshold")
            normalized = {
                "monitor_id": monitor_id,
                "kind": kind,
                "paths": [str((cwd / path).resolve()) if not Path(path).is_absolute() else str(Path(path).resolve()) for path in paths],
                "duration_seconds": _number(config["duration_seconds"], "duration_seconds", strictly=True),
                "sample_interval_seconds": _number(config.get("sample_interval_seconds", 30), "sample_interval_seconds", strictly=True, maximum=600),
            }
            if "available_below_gib" in config:
                normalized["available_below_gib"] = _number(config["available_below_gib"], "available_below_gib", strictly=True)
            if "available_below_percent" in config:
                normalized["available_below_percent"] = _number(config["available_below_percent"], "available_below_percent", strictly=True, maximum=100)
            for path in normalized["paths"]:
                try:
                    os.statvfs(filesystem_probe_path(path))
                except (OSError, MonitorError) as error:
                    raise MonitorError(f"cannot monitor filesystem for {path}: {error}") from error
            parsed.append(normalized)
        else:
            _keys(
                config,
                {"kind", "path", "stale_after_seconds"},
                {"startup_grace_seconds", "sample_interval_seconds"},
            )
            path = Path(config["path"])
            if not isinstance(config["path"], str) or not config["path"]:
                raise MonitorError("path must be a non-empty string")
            parsed.append(
                {
                    "monitor_id": monitor_id,
                    "kind": kind,
                    "path": str((cwd / path).resolve()) if not path.is_absolute() else str(path.resolve()),
                    "stale_after_seconds": _number(config["stale_after_seconds"], "stale_after_seconds", strictly=True),
                    "startup_grace_seconds": _number(config.get("startup_grace_seconds", 0), "startup_grace_seconds"),
                    "sample_interval_seconds": _number(config.get("sample_interval_seconds", 5), "sample_interval_seconds", strictly=True, maximum=300),
                }
            )
    return parsed


def process_tree(root_pid: int) -> set[int]:
    parents: dict[int, int] = {}
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit():
            continue
        try:
            raw = (entry / "stat").read_text(encoding="utf-8")
            _, separator, tail = raw.rpartition(")")
            fields = tail.strip().split() if separator else []
            if len(fields) >= 2:
                parents[int(entry.name)] = int(fields[1])
        except (FileNotFoundError, PermissionError, OSError, ValueError):
            continue
    result = {root_pid}
    changed = True
    while changed:
        changed = False
        for pid, parent in parents.items():
            if parent in result and pid not in result:
                result.add(pid)
                changed = True
    return result


def filesystem_probe_path(path: str) -> Path:
    candidate = Path(path)
    while not candidate.exists() and candidate != candidate.parent:
        candidate = candidate.parent
    if not candidate.exists():
        raise MonitorError(f"no existing filesystem ancestor for {path}")
    return candidate


class MonitorEngine:
    def __init__(self, job_dir: Path, registration: dict, target_pid: int, adapter=None):
        self.job_dir = job_dir
        self.registration = registration
        self.target_pid = target_pid
        self.adapter = adapter or NvidiaAdapter()

    @staticmethod
    def _attention(data, registration, monitor, reason, scope, subject, since, evidence=None, evidence_gap=None):
        fields = {
            "monitor_id": monitor["monitor_id"],
            "reason": reason,
            "scope": scope,
            "subject": subject,
            "condition_since": datetime.fromtimestamp(float(since), timezone.utc).isoformat().replace("+00:00", "Z"),
            "evidence": evidence or {},
            "authority": AUTHORITY,
        }
        if evidence_gap:
            fields["evidence_gap"] = evidence_gap[:512]
        append_event(data, registration, "attention", **fields)

    def _update_subject(self, data, monitor, subject, active, now, reason, scope, evidence):
        states = data.setdefault("monitor_states", {})
        monitor_state = states.setdefault(monitor["monitor_id"], {"kind": monitor["kind"], "subjects": {}})
        state = monitor_state["subjects"].setdefault(subject, {})
        state["last_sample_at"] = utc_now()
        state["evidence"] = evidence
        if not active:
            state.update(condition_since=None, alerted=False, active=False)
            return
        state["active"] = True
        if state.get("condition_since") is None:
            state["condition_since"] = now
        duration = now - float(state["condition_since"])
        if duration >= float(monitor["duration_seconds"]) and not state.get("alerted"):
            self._attention(data, self.registration, monitor, reason, scope, subject, state["condition_since"], evidence)
            state["alerted"] = True

    def _probe_error(self, data, monitor, now, detail):
        states = data.setdefault("monitor_states", {})
        state = states.setdefault(monitor["monitor_id"], {"kind": monitor["kind"], "subjects": {}})
        error = state.setdefault("probe_error", {})
        if error.get("since") is None:
            error["since"] = now
        error["detail"] = str(detail)[:512]
        if now - float(error["since"]) >= 30 and not error.get("alerted"):
            reason = {
                "gpu_process_idle": "gpu_probe_error",
                "disk_free": "disk_probe_error",
                "heartbeat_stale": "heartbeat_probe_error",
            }[monitor["kind"]]
            self._attention(data, self.registration, monitor, reason, "monitor_probe", monitor["monitor_id"], error["since"], evidence_gap=error["detail"])
            error["alerted"] = True

    def _sample_gpu(self, data, monitor, now):
        try:
            observed = self.adapter.process_sample(process_tree(self.target_pid))
            indices = {device["uuid"]: device["index"] for device in self.adapter.devices()}
            state = data.setdefault("monitor_states", {}).setdefault(monitor["monitor_id"], {"kind": monitor["kind"], "subjects": {}})
            state.pop("probe_error", None)
        except MonitorError as error:
            self._probe_error(data, monitor, now, error)
            return
        statuses = []
        for device in monitor["devices"]:
            index = indices.get(device["uuid"])
            if index is None:
                self._probe_error(data, monitor, now, f"NVIDIA device disappeared: {device['uuid']}")
                return
            utilization = observed.get(index, 0.0)
            idle = utilization < float(monitor["utilization_below_percent"])
            statuses.append((device, index, utilization, idle))
        if monitor["mode"] == "all" and not all(item[3] for item in statuses):
            statuses = [(d, i, u, False) for d, i, u, _ in statuses]
        for device, index, utilization, idle in statuses:
            self._update_subject(
                data, monitor, device["uuid"], idle, now, "gpu_process_idle", "job_process_tree",
                {"gpu_uuid": device["uuid"], "current_index": index, "utilization_percent": utilization, "utilization_below_percent": monitor["utilization_below_percent"], "target_pid": self.target_pid},
            )

    def _sample_disk(self, data, monitor, now):
        seen = set()
        had_error = False
        for path in monitor["paths"]:
            try:
                probe_path = filesystem_probe_path(path)
                stat = os.stat(probe_path)
                fs = os.statvfs(probe_path)
            except (OSError, MonitorError) as error:
                had_error = True
                self._probe_error(data, monitor, now, error)
                continue
            subject = f"dev:{stat.st_dev}"
            if subject in seen:
                continue
            seen.add(subject)
            available = fs.f_bavail * fs.f_frsize
            total = fs.f_blocks * fs.f_frsize
            percent = (available / total * 100) if total else 0.0
            low = False
            if "available_below_gib" in monitor:
                low = low or available < float(monitor["available_below_gib"]) * 1024**3
            if "available_below_percent" in monitor:
                low = low or percent < float(monitor["available_below_percent"])
            self._update_subject(data, monitor, subject, low, now, "disk_free_low", "filesystem", {"path": path, "available_bytes": available, "available_percent": round(percent, 3)})
        if not had_error:
            data.setdefault("monitor_states", {}).setdefault(monitor["monitor_id"], {}).pop("probe_error", None)

    def _sample_heartbeat(self, data, monitor, now):
        try:
            age = max(0.0, now - Path(monitor["path"]).stat().st_mtime)
        except FileNotFoundError:
            age = max(0.0, now - self.registration["created_epoch"])
        except OSError as error:
            self._probe_error(data, monitor, now, error)
            return
        data.setdefault("monitor_states", {}).setdefault(monitor["monitor_id"], {}).pop("probe_error", None)
        active = age >= float(monitor["stale_after_seconds"])
        proxy = dict(monitor, duration_seconds=0)
        self._update_subject(data, proxy, monitor["path"], active, now, "heartbeat_stale", "job_declared_path", {"path": monitor["path"], "age_seconds": round(age, 3)})

    def tick(self, now: float | None = None) -> None:
        now = now if now is not None else time.time()
        with locked_events(self.job_dir) as data:
            states = data.setdefault("monitor_states", {})
            for monitor in self.registration.get("monitors", []):
                state = states.get(monitor["monitor_id"], {})
                last = state.get("last_dispatch_epoch", 0)
                if now - float(last) < float(monitor["sample_interval_seconds"]):
                    continue
                state = states.setdefault(monitor["monitor_id"], {"kind": monitor["kind"], "subjects": {}})
                state["last_dispatch_epoch"] = now
                if now < self.registration["created_epoch"] + float(monitor.get("startup_grace_seconds", 0)):
                    continue
                if monitor["kind"] == "gpu_process_idle":
                    self._sample_gpu(data, monitor, now)
                elif monitor["kind"] == "disk_free":
                    self._sample_disk(data, monitor, now)
                else:
                    self._sample_heartbeat(data, monitor, now)
