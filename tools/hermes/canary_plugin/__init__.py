"""Reviewed inert plugin: no hooks, credentials, filesystem, network or process."""
import json


def canary_ping(args, **kwargs):
    return json.dumps({"canary": "cpw-canary", "version": "1.0.0", "status": "ok"}, sort_keys=True)


def register(ctx):
    ctx.register_tool(
        name="cpw_canary_ping", toolset="cpw-canary",
        schema={"name": "cpw_canary_ping", "description": "Return an inert canary response.",
                "parameters": {"type": "object", "properties": {}, "additionalProperties": False}},
        handler=canary_ping,
    )
