"""Check an AI agent before you call it, using GAIP's free readiness check."""
from __future__ import annotations

import json
import sys
import urllib.request
import uuid
from typing import Any, Callable

__all__ = ["check_agent", "watch_delivery", "main"]
__version__ = "0.1.0"

ENDPOINT = "https://www.gaipagents.com/a2a/agentverse"


def _ask(text: str, *, endpoint: str = ENDPOINT, timeout: float = 30.0,
         opener: Callable[..., Any] = urllib.request.urlopen) -> dict[str, Any]:
    body = json.dumps({
        "jsonrpc": "2.0", "id": str(uuid.uuid4()), "method": "message/send",
        "params": {"message": {"kind": "message", "role": "user", "messageId": str(uuid.uuid4()),
                               "parts": [{"kind": "text", "text": text}]}},
    }).encode()
    request = urllib.request.Request(endpoint, data=body, headers={
        "Content-Type": "application/json", "User-Agent": f"gaip-check/{__version__}"})
    with opener(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if "error" in payload:
        raise RuntimeError(payload["error"].get("message", "GAIP error"))
    parts = (payload.get("result") or {}).get("parts") or []
    routed = json.loads(parts[0]["text"]) if parts and "text" in parts[0] else {}
    result = routed.get("result") or {}
    result.setdefault("status", routed.get("status"))
    result["next_agents"] = [n.get("agent_id") for n in routed.get("next_agents", [])]
    return result


def check_agent(url: str, **kwargs: Any) -> dict[str, Any]:
    """Readiness verdict (READY / FIXES_NEEDED / UNREACHABLE), fixes and receipt for one agent."""
    if not isinstance(url, str) or not url.startswith("https://"):
        raise ValueError("A public https:// URL is required")
    return _ask(f"check {url}", **kwargs)


def watch_delivery(url: str, **kwargs: Any) -> dict[str, Any]:
    """Record what a good response from a public HTTPS service looks like and check it now."""
    if not isinstance(url, str) or not url.startswith("https://"):
        raise ValueError("A public https:// URL is required")
    return _ask(f"monitor delivery of {url}", **kwargs)


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in {"-h", "--help"}:
        print("usage: gaip-check <https://agent-url> [--watch]")
        return 2
    report = (watch_delivery if "--watch" in args else check_agent)(args[0])
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report.get("verdict") in (None, "READY") and report.get("status") != "BLOCKED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
