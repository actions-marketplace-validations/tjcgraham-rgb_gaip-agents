#!/usr/bin/env python3
"""GAIP check for CI: ask GAIP's free public readiness check about one agent URL.

Standard library only. Reads its settings from environment variables set by
action.yml (so it can also be run locally):

  GAIP_AGENT_URL        public https:// URL of the agent (domain, card, MCP or OpenAPI URL)
  GAIP_FAIL_ON_ERROR    "true" (default) exits 1 on ERROR findings or an unreachable agent
  GAIP_ENDPOINT         GAIP A2A endpoint (default https://www.gaipagents.com/a2a/agentverse)
  GAIP_TIMEOUT_SECONDS  request timeout (default 60)

GAIP output is read-only evidence about what was observed at the time of the
check. It is not certification, endorsement, a security test or advice.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
import uuid
from typing import Any, Callable

DEFAULT_ENDPOINT = "https://www.gaipagents.com/a2a/agentverse"
USER_AGENT = "gaip-check-action-client/1.1"
DISCLAIMER = ("GAIP reports what it observed at the time of this check, from public metadata only. "
              "It is not certification, endorsement, a security test or legal advice. "
              "Terms: https://www.gaipagents.com/terms")


class CheckError(RuntimeError):
    pass


def _truthy(value: str | None, default: bool) -> bool:
    if value is None or value.strip() == "":
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def request_check(url: str, *, endpoint: str = DEFAULT_ENDPOINT, timeout: float = 60.0,
                  opener: Callable[..., Any] = urllib.request.urlopen) -> dict[str, Any]:
    """Send `check <url>` to GAIP's router and return the readiness result."""
    if not isinstance(url, str) or not url.startswith("https://"):
        raise CheckError("agent-url must be a public https:// URL")
    body = json.dumps({
        "jsonrpc": "2.0", "id": str(uuid.uuid4()), "method": "message/send",
        "params": {"message": {"kind": "message", "role": "user", "messageId": str(uuid.uuid4()),
                               "parts": [{"kind": "text", "text": f"check {url}"}]}},
    }).encode("utf-8")
    req = urllib.request.Request(endpoint, data=body, method="POST", headers={
        "Content-Type": "application/json", "User-Agent": USER_AGENT})
    try:
        with opener(req, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        raise CheckError(f"GAIP could not be reached or answered unexpectedly: {exc}") from exc
    if not isinstance(payload, dict):
        raise CheckError("GAIP returned a non-object response")
    if "error" in payload:
        error = payload["error"] if isinstance(payload["error"], dict) else {"message": str(payload["error"])}
        raise CheckError(f"GAIP error: {error.get('message', 'unknown')}")
    parts = (payload.get("result") or {}).get("parts") or []
    try:
        routed = json.loads(parts[0]["text"])
    except (IndexError, KeyError, TypeError, ValueError) as exc:
        raise CheckError("GAIP response did not contain a readiness result") from exc
    result = routed.get("result") or {}
    result.setdefault("status", routed.get("status"))
    return result


def findings_of(result: dict[str, Any]) -> list[dict[str, Any]]:
    conformance = result.get("conformance") if isinstance(result.get("conformance"), dict) else {}
    rows = conformance.get("findings") if isinstance(conformance.get("findings"), list) else []
    return [row for row in rows if isinstance(row, dict)]


def summarise(result: dict[str, Any]) -> dict[str, Any]:
    findings = findings_of(result)
    errors = [f for f in findings if f.get("severity") == "ERROR"]
    warnings = [f for f in findings if f.get("severity") == "WARNING"]
    verdict = str(result.get("verdict") or result.get("status") or "UNKNOWN")
    # Without structured findings (e.g. unreachable), GAIP's fixes stand in for errors.
    fixes = [str(x) for x in result.get("fixes") or []]
    blocking = len(errors) or (len(fixes) if verdict in {"UNREACHABLE", "NOT_CHECKED"} and not findings else 0)
    return {"verdict": verdict, "receipt_id": result.get("receipt_id") or "", "errors": errors,
            "warnings": warnings, "fixes": fixes, "blocking_count": blocking,
            "status": result.get("status")}


def _escape(text: str) -> str:
    return text.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def _line(finding: dict[str, Any]) -> str:
    code = finding.get("code") or "FINDING"
    message = finding.get("message") or ""
    where = finding.get("path") or ""
    fix = finding.get("how_to_fix") or finding.get("fix") or ""
    text = f"{code}: {message}"
    if where:
        text += f" (at {where})"
    if fix:
        text += f" Fix: {fix}"
    return text


def report(summary: dict[str, Any], url: str, out: Callable[[str], None] = print) -> None:
    out(f"GAIP check of {url}: verdict {summary['verdict']}"
        + (f", receipt {summary['receipt_id']}" if summary["receipt_id"] else ""))
    for finding in summary["errors"]:
        out(f"::error title=GAIP {finding.get('code') or 'ERROR'}::{_escape(_line(finding))}")
    for finding in summary["warnings"]:
        out(f"::warning title=GAIP {finding.get('code') or 'WARNING'}::{_escape(_line(finding))}")
    if not summary["errors"] and summary["fixes"]:
        for fix in summary["fixes"]:
            level = "error" if summary["blocking_count"] else "notice"
            out(f"::{level} title=GAIP fix::{_escape(fix)}")
    if summary["receipt_id"]:
        out(f"Verify the receipt: https://www.gaipagents.com/v1/free/receipts/{summary['receipt_id']}/verify")
    out(DISCLAIMER)


def _write_outputs(summary: dict[str, Any], env: dict[str, str]) -> None:
    path = env.get("GITHUB_OUTPUT")
    if path:
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(f"verdict={summary['verdict']}\n")
            handle.write(f"receipt-id={summary['receipt_id']}\n")
            handle.write(f"error-count={len(summary['errors'])}\n")
            handle.write(f"warning-count={len(summary['warnings'])}\n")
    summary_path = env.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as handle:
            handle.write(f"### GAIP check: {summary['verdict']}\n\n")
            handle.write(f"- ERROR findings: {len(summary['errors'])}\n- WARNING findings: {len(summary['warnings'])}\n")
            if summary["receipt_id"]:
                handle.write(f"- Receipt: `{summary['receipt_id']}`\n")
            handle.write(f"\n_{DISCLAIMER}_\n")


def main(env: dict[str, str] | None = None, opener: Callable[..., Any] = urllib.request.urlopen,
         out: Callable[[str], None] = print) -> int:
    env = dict(os.environ if env is None else env)
    url = (env.get("GAIP_AGENT_URL") or "").strip()
    fail_on_error = _truthy(env.get("GAIP_FAIL_ON_ERROR"), True)
    endpoint = (env.get("GAIP_ENDPOINT") or DEFAULT_ENDPOINT).strip()
    try:
        timeout = float(env.get("GAIP_TIMEOUT_SECONDS") or 60)
    except ValueError:
        timeout = 60.0
    try:
        result = request_check(url, endpoint=endpoint, timeout=timeout, opener=opener)
    except CheckError as exc:
        out(f"::error title=GAIP check not completed::{_escape(str(exc))}")
        return 2
    summary = summarise(result)
    report(summary, url, out)
    _write_outputs(summary, env)
    if summary["status"] == "BLOCKED" and not summary["errors"]:
        out("::error title=GAIP check refused::GAIP refused this URL (see the fix above).")
        return 1 if fail_on_error else 0
    if fail_on_error and summary["blocking_count"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
