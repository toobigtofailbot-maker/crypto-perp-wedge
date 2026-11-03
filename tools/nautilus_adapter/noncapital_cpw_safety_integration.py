"""Manual N4-04 CPW FROZEN proof; offline inspection grants no trading authority."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import time
import uuid
from dataclasses import asdict
from decimal import Decimal
from pathlib import Path

from src.execution import nautilus_recovery_hold_guard as guard
from src.execution.interfaces import OMSState, OrderIntent, OrderSide, OrderType
from tools.nautilus_adapter import noncapital_supervisor_hold as h

SCHEMA = "cpw_n4_04_frozen_decision_v1"
STATUS = "VERIFIED_CPW_FROZEN"


def external(path, *, empty=False):
    h.require(".." not in Path(path).parts, "traversal forbidden")
    return h.external(path, empty=empty)


def directory_identity(root):
    stat = root.stat()
    return {"path": str(root), "device": stat.st_dev, "inode": stat.st_ino}


def sources():
    return {str(p.relative_to(h.ROOT)): h.sha(p) for p in (
        Path(__file__), Path(guard.__file__), h.ROOT / "src/execution/interfaces.py",
        Path(h.__file__))}


class SpyClient:
    """Inert sink: count every attempted transport call, including queries."""

    def __init__(self):
        self.calls = dict.fromkeys(("place_order", "cancel_order", "flatten",
                                   "get_open_orders", "get_position", "get_fills"), 0)

    def _called(self, name):
        self.calls[name] += 1
        raise AssertionError("underlying transport reached")

    def place_order(self, intent):
        return self._called("place_order")

    def cancel_order(self, symbol, order_ref):
        return self._called("cancel_order")

    def flatten(self, symbol):
        return self._called("flatten")

    def get_open_orders(self, symbol):
        return self._called("get_open_orders")

    def get_position(self, symbol):
        return self._called("get_position")

    def get_fills(self, symbol, since_cursor=None):
        return self._called("get_fills")


def intercept():
    sink = SpyClient()
    client = guard.FrozenExchangeClient(sink)
    attempts = 0
    for side in OrderSide:
        for reduce_only in (False, True):
            intent = OrderIntent("BTCUSDT", side, Decimal("0.001"), None,
                                 OrderType.MARKET, reduce_only, "N4-04-DENIED", None,
                                 None, "N4-04", "N4-04")
            try:
                client.place_order(intent)
            except guard.RecoveryHoldRefusal:
                attempts += 1
    for method, args in ((client.cancel_order, ("BTCUSDT", "unknown")),
                         (client.flatten, ("BTCUSDT",)),
                         (client.get_open_orders, ("BTCUSDT",)),
                         (client.get_position, ("BTCUSDT",)),
                         (client.get_fills, ("BTCUSDT",))):
        try:
            method(*args)
        except guard.RecoveryHoldRefusal:
            attempts += 1
    h.require(attempts == 9 and not any(sink.calls.values()), "pre-dispatch denial failed")
    return {"refused_attempts": attempts, "underlying_calls": sink.calls}


def verify(original, expected):
    root = external(original)
    identity = directory_identity(root)
    before = h.inventory(root)
    decision = guard.inspect_hold(root, expected)
    observation = intercept()  # Also exercise the actual seam when verification refuses.
    h.require(decision.state is OMSState.FROZEN, "CPW state disagreement")
    record = h.load(root / "supervisor-hold.json")
    h.require(identity == directory_identity(external(original)) and before == h.inventory(root),
              "original evidence changed")
    h.require(decision.evidence_verified, decision.reason)
    return {"schema": SCHEMA, "status": STATUS, **h.DENIAL,
            "hold_sha256": expected, "decision": asdict(decision),
            "state": decision.state.value, "action": decision.action.value,
            "binding": record["binding"], "original_identity": identity,
            "original_inventory": before, "original_unchanged": True,
            "cases": {label: {"source_case": label, **intercept()} for label, *_ in h.CASES},
            "boundary": observation, "sources": sources()}


def atomic(directory_fd, name, value):
    # Exclusive publication: a crash leaves an incomplete directory that cannot verify/reseal.
    temporary = name + ".pending"
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                 0o600, dir_fd=directory_fd)
    with os.fdopen(fd, "wb") as stream:
        stream.write(h.p.encoded(value))
        stream.flush()
        os.fsync(stream.fileno())
    os.link(temporary, name, src_dir_fd=directory_fd, dst_dir_fd=directory_fd,
            follow_symlinks=False)
    os.unlink(temporary, dir_fd=directory_fd)
    os.fsync(directory_fd)


def seal(output, original, expected):
    root = external(output, empty=True)
    h.require(os.name == "posix", "immutable emission requires POSIX descriptor profile")
    identity = directory_identity(root)
    h.require(not root.is_relative_to(external(original))
              and not external(original).is_relative_to(root), "overlapping evidence")
    directory_fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        opened = os.fstat(directory_fd)
        h.require((opened.st_dev, opened.st_ino) == (identity["device"], identity["inode"]),
                  "decision directory changed before open")
        result = verify(original, expected)
        h.require(directory_identity(external(root, empty=True)) == identity, "output substituted")
        record = {**result, "decision_id": str(uuid.uuid4()), "sealed_ns": time.time_ns(),
                  "inspector_pid": os.getpid(), "directory": identity}
        atomic(directory_fd, "cpw-decision.json", record)
        trusted = hashlib.sha256(h.p.encoded(record)).hexdigest()
        h.require(directory_identity(external(root)) == identity, "output substituted")
        atomic(directory_fd, "cpw-ack.json", {"schema": SCHEMA, "decision_sha256": trusted,
                                            "decision_id": record["decision_id"]})
    finally:
        os.close(directory_fd)
    return trusted


def inspect_decision(output, expected_decision, original, expected_hold, decision_id):
    root = external(output)
    h.require(re.fullmatch(r"[0-9a-f]{64}", expected_decision or ""), "external decision trust required")
    h.require({p.name for p in root.iterdir()} == {"cpw-decision.json", "cpw-ack.json"}, "incomplete decision")
    before = h.inventory(root)
    h.require(h.sha(root / "cpw-decision.json") == expected_decision, "untrusted decision")
    record = h.load(root / "cpw-decision.json")
    h.require(record["directory"] == directory_identity(root), "decision directory substituted")
    h.require(str(uuid.UUID(decision_id)) == record["decision_id"] == decision_id,
              "old/replayed decision identity")
    h.require(type(record["sealed_ns"]) is int and 0 < record["sealed_ns"] <= time.time_ns()
              and type(record["inspector_pid"]) is int and record["inspector_pid"] > 0, "seal identity")
    h.require(h.load(root / "cpw-ack.json") == {"schema": SCHEMA,
              "decision_sha256": expected_decision, "decision_id": decision_id}, "torn decision ACK")
    fresh = verify(original, expected_hold)
    h.require(set(record) == set(fresh) | {"directory", "sealed_ns", "decision_id", "inspector_pid"}
              and all(h.p.encoded(record[k]) == h.p.encoded(v) for k, v in fresh.items()),
              "decision/source disagreement")
    h.require(before == h.inventory(root), "decision mutation")
    return {"status": STATUS, "state": "FROZEN", **h.DENIAL,
            "decision_sha256": expected_decision, "decision_id": decision_id, "pid": os.getpid()}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    for name in ("verify", "run", "inspect-decision"):
        command = sub.add_parser(name)
        command.add_argument("--original", type=Path, required=True)
        if name == "run":
            command.add_argument("--public-noncapital-proof", action="store_true", required=True)
        else:
            command.add_argument("--expected-hold-sha256", required=True)
        if name == "inspect-decision":
            command.add_argument("--decision-output", type=Path, required=True)
            command.add_argument("--expected-decision-sha256", required=True)
            command.add_argument("--decision-id", required=True)
        else:
            command.add_argument("--decision-output", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.action == "inspect-decision":
            result = inspect_decision(args.decision_output, args.expected_decision_sha256,
                                      args.original, args.expected_hold_sha256, args.decision_id)
        else:
            if args.decision_output:
                destination = external(args.decision_output, empty=True)
                original = external(args.original, empty=args.action == "run")
                h.require(not destination.is_relative_to(original)
                          and not original.is_relative_to(destination), "overlapping evidence")
            expected = (h.run(args.original)["hold_sha256"] if args.action == "run"
                        else args.expected_hold_sha256)
            if args.decision_output:
                trusted = seal(args.decision_output, args.original, expected)
                result = {"status": STATUS, "decision_sha256": trusted,
                          "decision_id": h.load(args.decision_output / "cpw-decision.json")["decision_id"],
                          "state": "FROZEN", **h.DENIAL}
            else:
                result = verify(args.original, expected)
    except Exception:  # noqa: BLE001 - Never expose unsanitized paths/payloads or treat errors as HOLD.
        result = {"status": "BLOCKED", "state": "FROZEN", "reason": "CPW_RECOVERY_PROOF_BLOCKED", **h.DENIAL}
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == STATUS else 1


if __name__ == "__main__":
    raise SystemExit(main())
