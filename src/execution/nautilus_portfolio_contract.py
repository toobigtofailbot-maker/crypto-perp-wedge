"""Pure admission for the offline P1 fixture profile."""
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path
import re


MODE = "NONCAPITAL_TEST_ONLY"
AUTHORITY = "UNAPPROVED_SYNTHETIC_FIXTURE_NO_TRADE_PERMISSION"
SOURCE_SHA256 = "sha256:3cd808afdc5bf7b89cbd2c800aa7b45ba78976de1600098b60ce8b1795964c37"
CAP = Decimal("250")
MAX_AGE = timedelta(seconds=60)
SOURCE = Path(__file__).resolve().parents[2] / "tests/fixtures/nautilus_native_portfolio/source.json"


def require(condition, reason):
    if not condition:
        raise ValueError(f"P1 HOLD: {reason}")


def digest(data):
    return "sha256:" + sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                      allow_nan=False).encode("ascii")


def decode(data):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "duplicate JSON key")
            result[key] = value
        return result

    return json.loads(data, object_pairs_hook=unique,
                      parse_constant=lambda _: require(False, "nonfinite JSON"))


def fields(value, expected):
    require(isinstance(value, dict) and value.keys() == set(expected.split()),
            "unknown or missing fields")


def decimal_string(value):
    require(isinstance(value, str) and re.fullmatch(r"-?(0|[1-9][0-9]{0,11})(\.[0-9]{1,8})?", value),
            "expected bounded exact Decimal string")
    return Decimal(value)


def timestamp(value):
    require(isinstance(value, str) and re.fullmatch(
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{1,6})?Z", value), "invalid UTC timestamp")
    return datetime.fromisoformat(value)


def check_time(request, *, recovery=False):
    evaluation, expiry = map(timestamp, (request["evaluation_utc"], request["expiry_utc"]))
    require(evaluation < expiry <= evaluation + MAX_AGE, "invalid validity interval")
    if not recovery:
        require(evaluation <= datetime.now(UTC) < expiry, "stale or future request")
    return evaluation


def read_requests(path, *, recovery=False):
    with Path(path).open("rb") as stream:
        raw = stream.read(65537)
    require(len(raw) <= 65536, "request file exceeds size bound")
    rows = decode(raw)
    require(isinstance(rows, list) and 1 <= len(rows) <= 12, "bounded cycle list required")
    source_bytes = SOURCE.read_bytes()
    require(digest(source_bytes) == SOURCE_SHA256, "untrusted offline source bytes")
    source = decode(source_bytes)
    metadata = {row["symbol"]: row for row in source["symbols"]}
    seen, cycles = {}, []
    previous = None
    for request in rows:
        fields(request, "schema mode authority request_id request_content_sha256 portfolio_id run_id "
               "lineage venue market_type execution_venue evaluation_utc expiry_utc cycle_index "
               "source_identities source_fixture_sha256 targets limits")
        require((request["schema"], request["mode"], request["authority"], request["venue"],
                 request["market_type"], request["execution_venue"]) ==
                ("portfolio_execution_request_v1", MODE, AUTHORITY, "BINANCE",
                 "USD-M_PERPETUAL", "CPWSIM"), "unsupported authority or environment")
        require(request["lineage"] == {"source": "SYNTHETIC_TEST_ONLY", "strategy_id": "P1-DUMMY-STRATEGY",
                                       "candidate_id": None, "approval_id": None}, "untrusted lineage")
        for key in ("request_id", "portfolio_id", "run_id"):
            require(isinstance(request[key], str) and re.fullmatch(r"P1-[A-Z0-9-]{1,52}", request[key]),
                    "invalid fixture identity")
        require(request["request_id"].startswith(request["run_id"] + "-"),
                "request ID must be scoped to run")
        content = digest(canonical({k: v for k, v in request.items() if k != "request_content_sha256"}))
        require(request["request_content_sha256"] == content, "request digest mismatch")
        identifier = request["request_id"]
        if identifier in seen:
            require(seen[identifier] == content, "changed-content replay")
            continue
        evaluation = check_time(request, recovery=recovery)
        require(type(request["cycle_index"]) is int and request["cycle_index"] == len(cycles)
                and (previous is None or evaluation >= previous), "cycle sequence mismatch")
        require(request["source_fixture_sha256"] == SOURCE_SHA256, "wrong source fixture")
        identities = request["source_identities"]
        require(isinstance(identities, list) and len(identities) == 2, "two fixture instruments required")
        universe = []
        for identity in identities:
            fields(identity, "symbol instrument_id metadata_sha256")
            symbol = identity["symbol"]
            require(isinstance(symbol, str) and symbol in metadata and symbol not in universe,
                    "unknown or duplicate source symbol")
            require(identity["instrument_id"] == f"{symbol}-PERP.BINANCE"
                    and identity["metadata_sha256"] == digest(canonical(metadata[symbol])),
                    "instrument identity mismatch")
            universe.append(symbol)
        if cycles:
            first = cycles[0][0]
            require(all(request[k] == first[k] for k in ("portfolio_id", "run_id", "source_identities")),
                    "mixed portfolio, run or universe")
        targets = {}
        require(isinstance(request["targets"], list) and len(request["targets"]) == 2,
                "complete two-symbol targets required")
        for target in request["targets"]:
            fields(target, "symbol target_qty units")
            symbol = target["symbol"]
            require(symbol in universe and symbol not in targets
                    and target["units"] == "BASE_CONTRACT_QUANTITY", "invalid target identity or units")
            targets[symbol] = decimal_string(target["target_qty"])
        limits = request["limits"]
        fields(limits, "test_only_per_order_max_notional_usdt test_only_portfolio_gross_max_usdt leverage")
        order_cap, gross_cap = [decimal_string(limits[k]) for k in
                                ("test_only_per_order_max_notional_usdt", "test_only_portfolio_gross_max_usdt")]
        require(0 < order_cap <= CAP and 0 < gross_cap <= CAP
                and limits["leverage"] == "1", "fixture caps or leverage exceeded")
        seen[identifier] = content
        previous = evaluation
        cycles.append((request, targets, order_cap, gross_cap))
    return cycles, source, digest(raw)


def order_id(request, symbol):
    return "P1-" + digest(canonical([request["request_content_sha256"], symbol]))[7:39]


def profile(request):
    return {"profile": "NONCAPITAL_NATIVE", "persist": True,
            "trader_id": "CPWNATIVE-" + digest(request["run_id"].encode("ascii"))[7:19]}
