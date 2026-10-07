"""Package boundaries; physical acceptance remains a separate mandatory gate."""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
HERMES = ROOT / "tools/hermes"
BASE = "11214acfb6d8af44586c50089eb9965063a505ee"
PATCH_SHA = "1294e8e88663691f49e4b78d074460f91f9097afbd23a0e005a161f20fe78a6e"


def document(name):
    return yaml.safe_load((HERMES / name).read_text(encoding="utf-8"))


def test_f0_bytes_equal_exact_base():
    for original, current in [("compose.yaml", "compose.f0.yaml"),
                              ("config/config.yaml", "config/config.yaml"),
                              ("config/SOUL.md", "config/SOUL.md")]:
        expected = subprocess.check_output(["git", "show", f"{BASE}:tools/hermes/{original}"], cwd=ROOT)
        # Git checkout may use CRLF: preservation is against pre-package working bytes.
        actual = (HERMES / current).read_bytes()
        assert actual.replace(b"\r\n", b"\n") == expected.replace(b"\r\n", b"\n")
    assert "v2026.8.13@sha256:68e15ae" in (HERMES / "compose.f0.yaml").read_text()
    assert hashlib.sha256((HERMES / "compose.f0.yaml").read_bytes()).hexdigest() == "0ba9dc88352c7d8b79da5e2a4a9b3eeb3c4b6127b858048516a7fa62a514b49a"
    assert hashlib.sha256((HERMES / "config/config.yaml").read_bytes()).hexdigest() == "7993c5fcdaa9df3a7c42a698a61d22b92feca49f83e08d714c159bb976326899"
    assert hashlib.sha256((HERMES / "config/SOUL.md").read_bytes()).hexdigest() == "77ebe8acfe70ccab45592fa4b5dd9e08f10b54287faedb0b3546efbad0bc81ac"


def test_exact_patch_provenance_and_build_preimage_guard():
    patch = (HERMES / "upstream_patches/59559-tool-scope.patch").read_bytes()
    assert hashlib.sha256(patch).hexdigest() == PATCH_SHA
    changed = [line.split(" b/", 1)[1] for line in patch.decode().splitlines() if line.startswith("diff --git ")]
    assert changed == ["gateway/run_agent_cache.py", "gateway/run_turn_runner.py", "model_tools.py",
                       "tests/gateway/test_gateway_turn_toolset_scope.py", "tests/tools/test_direct_tool_scope_enforcement.py"]
    dockerfile = (HERMES / "Dockerfile.extreme").read_text()
    assert "v2026.9.24@sha256:fca358f12efd65bfaaca05884166f15c0e2788375ca30d77061ac1ebc96452b7" in dockerfile
    assert "git apply --check" in dockerfile and PATCH_SHA in dockerfile
    assert "f97608f178d1ffeca59860195ab7da295f7c8e5f" in dockerfile
    assert "59559b858fb1a4578f51029112099462a431c3f1" in dockerfile


def test_execution_and_canary_topology_has_no_host_or_director_surface():
    compose = document("compose.yaml")
    assert set(compose["services"]) == {"project-evidence", "canary-mcp", "sandbox-keygen", "execution-sandbox", "hermes"}
    for service in compose["services"].values():
        assert not service.get("ports")
        assert "ALL" in service["cap_drop"]
        assert "no-new-privileges:true" in service["security_opt"]
        assert not any("docker.sock" in mount for mount in service.get("volumes", []))
    sandbox = compose["services"]["execution-sandbox"]
    assert sandbox["networks"] == ["execution"]
    assert not sandbox.get("environment")
    assert sandbox["volumes"] == ["sandbox-workspace:/workspace:rw", "sandbox-hostkeys:/run/cpw-sandbox-hostkeys:rw", "sandbox-public:/run/cpw-sandbox-public:ro"]
    assert "SYS_ADMIN" not in sandbox["cap_add"]
    for name in ["canary", "execution"]:
        assert compose["networks"][name]["internal"] is True
        assert compose["networks"][name]["driver_opts"]["com.docker.network.bridge.gateway_mode_ipv4"] == "isolated"
    keygen = compose["services"]["sandbox-keygen"]
    assert keygen["network_mode"] == "none"
    assert "sandbox-private:/run/cpw-sandbox-ssh:ro" in compose["services"]["hermes"]["volumes"]
    canary = compose["services"]["canary-mcp"]
    assert canary["networks"] == ["canary"] and not canary.get("volumes") and not canary.get("environment")


def test_locked_config_and_non_authoritative_surface():
    config = document("config/config.f1f2.yaml")
    assert config["_config_version"] == 46
    assert config["model"] == {"provider": "openai-codex", "default": "${HERMES_MODEL}"}
    assert config["browser"] == {"cloud_provider": "browserbase", "backend": "off",
                                 "auto_local_for_private_urls": False, "allow_private_urls": False,
                                 "use_real_profile": False}
    assert config["web"] == {"search_backend": "openai-native"}
    assert config["terminal"] == {"backend": "ssh", "cwd": "/workspace", "home_mode": "profile",
                                  "env_passthrough": [], "credential_files": []}
    assert config["delegation"]["max_spawn_depth"] == 1
    assert config["delegation"]["max_concurrent_children"] == config["delegation"]["oneshot_max_children"] == 2
    assert config["delegation"]["orchestrator_enabled"] is False
    assert config["delegation"]["subagent_auto_approve"] is False
    tools = config["platform_toolsets"]["cli"]
    assert config["toolsets"] == tools
    assert not {"all", "*", "web", "web_extract", "browser_exec", "computer_use", "cronjob", "kanban", "project", "desktop_ui"} & set(tools)
    assert config["plugins"]["enabled"] == ["cpw-canary"]
    assert config["curator"]["consolidate"] is False
    assert config["skills"]["create_dir"] == "/opt/data/writable-skills"
    assert config["skills"]["external_dirs"] == ["/opt/data/writable-skills"]
    assert "debugging" not in config["agent"]["disabled_toolsets"]
    assert len(config["mcp_servers"]["project-evidence"]["tools"]["include"]) == 14
    assert config["mcp_servers"]["cpw-canary"]["tools"]["include"] == ["canary_ping"]
    for server in config["mcp_servers"].values():
        assert server["sampling"]["enabled"] is server["elicitation"]["enabled"] is False
    compose = document("compose.yaml")
    env = compose["services"]["hermes"]["environment"]
    assert env["HERMES_SKIP_CONFIG_MIGRATION"] == env["HERMES_DISABLE_LAZY_INSTALLS"] == "1"
    for name in ["BROWSERBASE_API_KEY", "BROWSERBASE_PROJECT_ID"]:
        assert env[name] == "${" + name + ":-}"
    assert env["HERMES_WRITE_SAFE_ROOT"] == "/opt/data:/workspace"
    assert "/run:size=64m,mode=755,exec" in compose["services"]["hermes"]["tmpfs"]
    assert env["TERMINAL_SSH_KEY"] == "/run/cpw-sandbox-ssh/id_ed25519"
    assert env["TERMINAL_SSH_HOST"] == "execution-sandbox"
    assert env["TERMINAL_SSH_USER"] == "cpw" and env["TERMINAL_SSH_PORT"] == "2222"


def test_inert_canary_plugin_has_exact_one_tool_and_no_effects():
    path = HERMES / "canary_plugin/__init__.py"
    spec = importlib.util.spec_from_file_location("cpw_canary_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    registered = []
    class Context:
        def register_tool(self, **kw):
            registered.append(kw)
    module.register(Context())
    assert len(registered) == 1
    tool = registered[0]
    assert tool["name"] == "cpw_canary_ping"
    assert tool["schema"]["parameters"] == {"type": "object", "properties": {}, "additionalProperties": False}
    assert tool["handler"]({}) == tool["handler"]({})
    assert json.loads(tool["handler"]({})) == {"canary": "cpw-canary", "version": "1.0.0", "status": "ok"}
    tree = ast.parse(path.read_text())
    assert [node.names[0].name for node in tree.body if isinstance(node, ast.Import)] == ["json"]
    assert not any(isinstance(node, ast.ImportFrom) for node in ast.walk(tree))
    assert document("canary_plugin/plugin.yaml")["provides_hooks"] == []
    # MCP tool discovery without opening an HTTP server.
    spec = importlib.util.spec_from_file_location("cpw_mcp_test", HERMES / "canary_mcp_server.py")
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    assert module.canary_ping() == {"canary": "cpw-canary", "version": "1.0.0", "status": "ok"}
    assert set(module.mcp._tool_manager._tools) == {"canary_ping"}


def test_fixed_intake_and_explicit_start_modes_without_autonomous_schedules():
    source = (ROOT / "tools/prefect_integration/hermes_research_intake.py").read_text()
    assert '"hermes", "chat", "-q", build_hermes_prompt(validated)' in source
    assert "shell=False" in source and '"/opt/hermes/hermes"' not in source
    script = (HERMES / "start.ps1").read_text()
    assert '[ValidateSet("F0", "F1F2")]' in script
    assert "InstallSchedules is forbidden in F1F2 mode" in script
    assert '"compose.f0.yaml"' in script and '.no-bundled-skills' in script
    assert "ReparsePoint" in script
    assert 'HERMES_HOME' not in source.split('command = [',1)[1].split('process =',1)[0]
    readme = (HERMES / "README.md").read_text()
    assert "--no-skills" in readme and "research-scout" in readme and "research-critic" in readme
