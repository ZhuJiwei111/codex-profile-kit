#!/usr/bin/env python3
"""Dependency-free MCP stdio server for bounded long-job observation."""

from __future__ import annotations

import json
import os
import sys
import threading

from supervisor import JobStore, SupervisorError


PROTOCOL_VERSION = "2025-06-18"
TOOL_NAMES = ("wait_event", "inspect_job", "list_jobs", "ack_event")
STORE = JobStore()


def wait_event(job_id: str, cancel_event=None) -> str:
    """Wait without model sampling until this job has an unacknowledged event."""
    interval = float(os.environ.get("PLJS_POLL_INTERVAL_SECONDS", "2"))
    return STORE.render_payload(STORE.wait_event(job_id, poll_interval=interval, cancel_event=cancel_event))


def inspect_job(job_id: str) -> str:
    """Inspect current job, unit, paths, and any pending event without reading logs."""
    return STORE.render_payload(STORE.inspect_job(job_id))


def list_jobs() -> str:
    """List durable job registrations and pending event state without reading logs."""
    return STORE.render_payload(STORE.list_jobs())


def ack_event(job_id: str, event_id: int) -> str:
    """Idempotently acknowledge one delivered event; never alter the underlying job."""
    return STORE.render_payload(STORE.ack_event(job_id, event_id))


def tool_definitions() -> list[dict]:
    job_id = {"type": "string", "description": "Durable job ID returned by start"}
    return [
        {
            "name": "wait_event",
            "description": "Block inside the host until a durable unacknowledged job event exists; never read logs or alter the job.",
            "inputSchema": {
                "type": "object",
                "properties": {"job_id": job_id},
                "required": ["job_id"],
                "additionalProperties": False,
            },
            "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True},
        },
        {
            "name": "inspect_job",
            "description": "Inspect bounded job, unit, path, and pending-event state without reading logs.",
            "inputSchema": {
                "type": "object",
                "properties": {"job_id": job_id},
                "required": ["job_id"],
                "additionalProperties": False,
            },
            "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True},
        },
        {
            "name": "list_jobs",
            "description": "List durable long-job registrations and pending events without reading logs.",
            "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
            "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True},
        },
        {
            "name": "ack_event",
            "description": "Idempotently mark one delivered event consumed; never alter the underlying job.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "job_id": job_id,
                    "event_id": {"type": "integer", "minimum": 1},
                },
                "required": ["job_id", "event_id"],
                "additionalProperties": False,
            },
            "annotations": {"readOnlyHint": False, "destructiveHint": False, "idempotentHint": True},
        },
    ]


class StdioMcpServer:
    def __init__(self):
        self._write_lock = threading.Lock()
        self._requests_lock = threading.Lock()
        self._requests: dict[object, threading.Event] = {}

    def _send(self, value: dict) -> None:
        encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        with self._write_lock:
            sys.stdout.write(encoded + "\n")
            sys.stdout.flush()

    def _result(self, request_id, result: dict) -> None:
        self._send({"jsonrpc": "2.0", "id": request_id, "result": result})

    def _error(self, request_id, code: int, message: str) -> None:
        self._send({"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}})

    def _tool_call(self, name: str, arguments: dict, cancel_event: threading.Event) -> dict:
        if not isinstance(arguments, dict):
            raise SupervisorError("tool arguments must be an object")
        if name == "wait_event":
            payload = wait_event(arguments["job_id"], cancel_event=cancel_event)
        elif name == "inspect_job":
            payload = inspect_job(arguments["job_id"])
        elif name == "list_jobs":
            payload = list_jobs()
        elif name == "ack_event":
            payload = ack_event(arguments["job_id"], int(arguments["event_id"]))
        else:
            raise KeyError(name)
        return {
            "content": [{"type": "text", "text": payload}],
            "structuredContent": json.loads(payload),
            "isError": False,
        }

    def _dispatch_request(self, message: dict, cancel_event: threading.Event) -> None:
        request_id = message["id"]
        try:
            method = message.get("method")
            params = message.get("params") or {}
            if method == "initialize":
                requested = params.get("protocolVersion")
                negotiated = requested if isinstance(requested, str) else PROTOCOL_VERSION
                self._result(
                    request_id,
                    {
                        "protocolVersion": negotiated,
                        "capabilities": {"tools": {"listChanged": False}},
                        "serverInfo": {"name": "personal-long-job-supervisor", "version": "0.1.0"},
                        "instructions": "Observe durable local job events. Never cancel, retry, restart, reconfigure, or launch a next stage.",
                    },
                )
            elif method == "ping":
                self._result(request_id, {})
            elif method == "tools/list":
                self._result(request_id, {"tools": tool_definitions()})
            elif method == "tools/call":
                name = params.get("name")
                if name not in TOOL_NAMES:
                    self._error(request_id, -32602, f"unknown tool: {name}")
                else:
                    try:
                        self._result(request_id, self._tool_call(name, params.get("arguments") or {}, cancel_event))
                    except (KeyError, TypeError, ValueError, SupervisorError) as error:
                        self._result(
                            request_id,
                            {
                                "content": [{"type": "text", "text": str(error)}],
                                "isError": True,
                            },
                        )
            else:
                self._error(request_id, -32601, f"method not found: {method}")
        except Exception as error:
            self._error(request_id, -32603, f"internal error: {error}")
        finally:
            with self._requests_lock:
                self._requests.pop(request_id, None)

    def handle(self, message: dict) -> None:
        method = message.get("method")
        if "id" not in message:
            if method == "notifications/cancelled":
                request_id = (message.get("params") or {}).get("requestId")
                with self._requests_lock:
                    cancel_event = self._requests.get(request_id)
                if cancel_event:
                    cancel_event.set()
            return
        request_id = message["id"]
        cancel_event = threading.Event()
        with self._requests_lock:
            self._requests[request_id] = cancel_event
        thread = threading.Thread(target=self._dispatch_request, args=(message, cancel_event), daemon=True)
        thread.start()

    def run(self) -> None:
        for line in sys.stdin:
            try:
                message = json.loads(line)
                if not isinstance(message, dict) or message.get("jsonrpc") != "2.0":
                    raise ValueError("expected JSON-RPC 2.0 object")
                self.handle(message)
            except (json.JSONDecodeError, ValueError) as error:
                self._error(None, -32700, str(error))


def main() -> None:
    StdioMcpServer().run()


if __name__ == "__main__":
    main()
