#!/usr/bin/env python3
"""SSH transport for the existing supervisor; no remote daemon or scheduler."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import threading
import time
import uuid

from durable import atomic_write_json, file_lock, read_json
from monitoring import discover_capabilities
from process_identity import execution_host_identity
from supervisor import DEFAULT_STATE_ROOT, JobStore, SupervisorError, build_parser


def controller_root():
    return Path(os.environ.get("PLJS_STATE_ROOT", DEFAULT_STATE_ROOT)).resolve()


class RemoteClient:
    def __init__(self, project, target=None, via=None):
        self.project = Path(project).expanduser().resolve()
        self.local = self.project / ".local"
        self.config = read_json(self.local / "connections.json")
        if (self.local / "project.json").exists():
            shared = self.config
            project_config = read_json(self.local / "project.json")
            self.config = dict(project_config,
                targets=shared["targets"],
                default_target=shared.get("default_target"),
                supervisor=dict(shared.get("supervisor", {}),
                                **project_config.get("supervisor", {})))
        self.target = target or self.config.get("default_target")
        self.via = via

    def locator_path(self, job_id):
        # Reuse the core ID validation without creating a local job.
        import re
        if not re.fullmatch(r"[a-z0-9-]{8,80}", job_id):
            raise SupervisorError("invalid job_id")
        return self.local / "supervisor" / "jobs" / (job_id + ".json")

    def locator(self, job_id):
        return read_json(self.locator_path(job_id))

    def reserve(self, job_id, target, state_root, *, previous=None):
        path = self.locator_path(job_id)
        value = {"job_id": job_id, "target": target, "state_root": state_root}
        index = controller_root() / "remote_jobs" / (job_id + ".json")
        index.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        with file_lock(index.parent / "registry.lock"):
            if index.exists() and read_json(index)["project"] != str(self.project):
                raise SupervisorError("job ID belongs to another project")
            if path.exists():
                current = read_json(path)
                if current != value and current != previous:
                    raise SupervisorError("job ID is already bound to another target or state root")
            atomic_write_json(index, {"project": str(self.project)})
            atomic_write_json(path, value)

    def rpc(self, action, *, target=None, state_root=None, cancel_event=None, **values):
        target = self.via or target or self.target
        targets = self.config["targets"]
        if target not in targets:
            raise SupervisorError("execution target is no longer registered; use --via CURRENT_TARGET to read shared records")
        setup = self.config["supervisor"]
        payload = dict(action=action, state_root=state_root or setup["state_root"], **values)
        command = "exec " + shlex.join([setup["python"], setup["entry"], "serve"])
        process = subprocess.Popen(
            ["ssh", "-T", "-F", str(self.local / "ssh_config"), "-oBatchMode=yes",
             "-oConnectTimeout=8", targets[target]["ssh_alias"], command],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        data = json.dumps(payload)
        deadline = time.monotonic() + 60
        try:
            while True:
                if cancel_event is not None and cancel_event.is_set():
                    raise SupervisorError("wait cancelled; remote job and events are unchanged")
                if time.monotonic() >= deadline:
                    raise SupervisorError("SSH response timed out; remote outcome is unknown; inspect the same job ID")
                try:
                    stdout, stderr = process.communicate(input=data, timeout=0.2)
                    break
                except subprocess.TimeoutExpired:
                    data = None
            if process.returncode:
                raise SupervisorError("SSH request failed; remote outcome may be unknown: " + stderr[-1500:])
            try:
                return json.loads(stdout)
            except ValueError as error:
                raise SupervisorError("invalid remote response; inspect the original job ID") from error
        finally:
            if process.poll() is None:
                process.terminate()  # only this caller's SSH transport, never the job
                try:
                    process.communicate(timeout=2)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.communicate()

    def start_job(self, *, request_id=None, **values):
        if self.via:
            raise SupervisorError("--via is for reading existing jobs; use --target to start")
        if not self.target or self.target not in self.config["targets"]:
            raise SupervisorError("select a registered target before starting a job")
        job_id = request_id or uuid.uuid4().hex
        state_root = self.config["supervisor"]["state_root"]
        self.reserve(job_id, self.target, state_root)
        try:
            return self.rpc("start", request_id=job_id, **values)
        except SupervisorError as error:
            raise SupervisorError(f"job_id={job_id}; {error}") from error

    def action(self, action, job_id, **values):
        path = self.locator_path(job_id)
        if not path.exists() and self.via and action == "inspect":
            # Explicit shared-record inspection does not invent an execution route.
            return self.rpc(action, job_id=job_id)
        locator = self.locator(job_id)
        return self.rpc(action, target=locator["target"], state_root=locator["state_root"],
                        job_id=job_id, **values)

    def inspect_job(self, job_id):
        return self.action("inspect", job_id)

    def ack_event(self, job_id, event_id):
        return self.action("ack", job_id, event_id=event_id)

    def interrupt_wait(self, job_id):
        return self.action("interrupt", job_id)

    def clean_job(self, job_id, released_host=False):
        if released_host:
            # Explicit release confirmation, not route removal, authorizes discard.
            # The selected live target reads shared records; it never inherits execution.
            path = self.locator_path(job_id)
            locator = read_json(path) if path.exists() else {}
            result = self.rpc("clean", target=self.target, state_root=locator.get("state_root"),
                              job_id=job_id, released_host=True)
        else:
            result = self.action("clean", job_id)
        index = controller_root() / "remote_jobs" / (job_id + ".json")
        index.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        with file_lock(index.parent / "registry.lock"):
            self.locator_path(job_id).unlink(missing_ok=True)
            if index.exists() and read_json(index)["project"] == str(self.project):
                index.unlink()
        return result

    def wait_any(self, job_ids, poll_interval=2, cancel_event=None):
        locators = [self.locator(job_id) for job_id in job_ids]
        if len({(x["target"], x["state_root"]) for x in locators}) != 1:
            raise SupervisorError("remote wait group must share one execution target and state root")
        tokens = None
        while True:
            reply = self.rpc("wait", target=locators[0]["target"],
                             state_root=locators[0]["state_root"], job_ids=job_ids,
                             wait_tokens=tokens, cancel_event=cancel_event)
            if not reply.get("idle"):
                return reply
            tokens = reply["wait_tokens"]

    def recover(self):
        """Rebuild disposable local locators from existing shared registrations."""
        rows = self.rpc("registrations")
        recovered, unresolved = [], []
        state_root = self.config["supervisor"]["state_root"]
        for row in rows["jobs"]:
            job_id = row["job_id"]
            path = self.locator_path(job_id)
            old = read_json(path) if path.exists() else None
            if old and old["state_root"] != state_root:
                raise SupervisorError("recovery state root differs from existing locator")
            if old and old["target"] in self.config["targets"]:
                self.reserve(job_id, old["target"], state_root)
            elif row.get("terminal") or row.get("execution_host") == rows["execution_host"]:
                self.reserve(job_id, self.via or self.target, state_root, previous=old)
            else:
                unresolved.append(job_id)
                continue
            recovered.append(job_id)
        return {"recovered": recovered, "unresolved": unresolved}



def serve():
    request = json.load(sys.stdin)
    action = request.pop("action")
    if action == "capabilities":
        return discover_capabilities()
    store = JobStore(request.pop("state_root"))
    if action == "start":
        return store.start_job(event_lock="mkdir", **request)
    if action == "registrations":
        # Read metadata only: never inspect another node's PID to rebuild an index.
        return {"execution_host": execution_host_identity(), "jobs": [
            {"job_id": p.parent.name, "execution_host": read_json(p).get("execution_host"),
             "terminal": (p.parent / "result.json").exists()}
            for p in sorted(store.jobs_root.glob("*/job.json"))]}
    if action == "wait":
        ids = request["job_ids"]
        tokens = request.get("wait_tokens")
        if tokens is None:
            tokens = {job_id: store._wait_token(job_id) for job_id in ids}
        cancelled = threading.Event()
        timer = threading.Timer(20, cancelled.set)
        timer.daemon = True
        timer.start()
        try:
            return store.wait_any(ids, cancel_event=cancelled, wait_tokens=tokens)
        except SupervisorError as error:
            if cancelled.is_set() and "wait cancelled by MCP client" in str(error):
                return {"idle": True, "wait_tokens": tokens}
            raise
        finally:
            timer.cancel()
    methods = {"inspect": store.inspect_job, "ack": store.ack_event,
               "interrupt": store.interrupt_wait, "clean": store.clean_job}
    if action not in methods:
        raise SupervisorError("unsupported remote action")
    return methods[action](**request)


class RoutedJobStore(JobStore):
    """Existing MCP methods route known remote IDs through their local locator."""
    def remote(self, job_id):
        self.job_dir(job_id)  # validation
        path = self.state_root / "remote_jobs" / (job_id + ".json")
        return RemoteClient(read_json(path)["project"]) if path.exists() else None

    def inspect_job(self, job_id):
        client = self.remote(job_id)
        return client.inspect_job(job_id) if client else super().inspect_job(job_id)

    def ack_event(self, job_id, event_id):
        client = self.remote(job_id)
        return client.ack_event(job_id, event_id) if client else super().ack_event(job_id, event_id)

    def interrupt_wait(self, job_id):
        client = self.remote(job_id)
        return client.interrupt_wait(job_id) if client else super().interrupt_wait(job_id)

    def _list_rows(self):
        jobs, skipped = super()._list_rows()
        for path in sorted((self.state_root / "remote_jobs").glob("*.json")):
            try:
                jobs.append(self._list_row(self.inspect_job(path.stem)))
            except (OSError, ValueError, SupervisorError) as error:
                jobs.append({"job_id": path.stem, "status": "connection_unavailable", "detail": str(error)[:300]})
        return jobs, skipped

    def wait_any(self, job_ids, poll_interval=2, cancel_event=None, **kwargs):
        if not isinstance(job_ids, list) or not job_ids or len(job_ids) > 100:
            raise SupervisorError("job_ids must be a non-empty list of at most 100 IDs")
        groups = {}
        for job_id in job_ids:
            client = self.remote(job_id)
            if client:
                locator = client.locator(job_id)
                key = (str(client.project), locator["target"], locator["state_root"])
            else:
                key = None
            groups.setdefault(key, (client, []))[1].append(job_id)
        if not groups:
            raise SupervisorError("job_ids must be a non-empty list")
        stop = threading.Event()
        class Cancel:
            def is_set(self):
                return stop.is_set() or (cancel_event is not None and cancel_event.is_set())
            def wait(self, seconds):
                end = time.monotonic() + seconds
                while time.monotonic() < end and not self.is_set():
                    stop.wait(min(0.1, max(0, end-time.monotonic())))
        cancellation = Cancel()
        def group_wait(client, ids):
            if client:
                return client.wait_any(ids, cancel_event=cancellation)
            return JobStore.wait_any(self, ids, poll_interval=poll_interval, cancel_event=cancellation)
        pool = ThreadPoolExecutor(max_workers=len(groups))
        futures = {pool.submit(group_wait, client, ids) for client, ids in groups.values()}
        errors = []
        try:
            while futures:
                done, futures = wait(futures, return_when=FIRST_COMPLETED)
                for future in done:
                    try:
                        return future.result()
                    except SupervisorError as error:
                        # Terminal groups must not block still-waitable groups.
                        if not any(reason in str(error) for reason in ("already terminal or inactive", "no waitable execution target")):
                            raise
                        errors.append(str(error))
            raise SupervisorError("no remaining waitable observations; " + "; ".join(errors))
        finally:
            stop.set()
            pool.shutdown(wait=True)


def main(argv=None):
    if (argv or sys.argv[1:]) == ["serve"]:
        output = serve()
    else:
        parser = build_parser()
        parser.add_argument("--project", type=Path, required=True)
        parser.add_argument("--target")
        parser.add_argument("--via", help="current target used to read shared records after the original target was released")
        # Reuse the native command schema and add reconnect operations.
        subparsers = next(a for a in parser._actions if hasattr(a, "choices") and isinstance(a.choices, dict))
        subparsers.add_parser("recover")
        waiting = subparsers.add_parser("wait")
        waiting.add_argument("job_ids", nargs="+")
        args = parser.parse_args(argv)
        client = RemoteClient(args.project, args.target, args.via)
        if args.subcommand == "start":
            command = args.command[1:] if args.command[:1] == ["--"] else args.command
            output = client.start_job(name=args.name, cwd=str(args.cwd), command=command,
                request_id=args.request_id, stage_path=str(args.stage_path) if args.stage_path else None, monitors=args.monitor, artifacts=[str(p) for p in args.artifact],
                heartbeat_path=str(args.heartbeat_path) if args.heartbeat_path else None, stale_after=args.stale_after)
        elif args.subcommand == "capabilities":
            output = client.rpc("capabilities")
        elif args.subcommand == "recover":
            output = client.recover()
        elif args.subcommand == "wait":
            output = client.wait_any(args.job_ids)
        elif args.subcommand == "list":
            output = RoutedJobStore().list_jobs()
        elif args.subcommand == "clean":
            output = client.clean_job(args.job_id, released_host=args.released_host)
        else:
            methods = {"status": client.inspect_job, "ack": client.ack_event,
                       "interrupt-wait": client.interrupt_wait, "clean": client.clean_job}
            output = methods[args.subcommand](args.job_id, args.event_id) if args.subcommand == "ack" else methods[args.subcommand](args.job_id)
    print(json.dumps(output, ensure_ascii=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (SupervisorError, OSError, ValueError, KeyError, RuntimeError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False), file=sys.stderr)
        raise SystemExit(2)
