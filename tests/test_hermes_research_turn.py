"""Exercise the operator script with only the OS Docker process launch mocked."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'tools/hermes/research_turn.ps1'
SHA = 'a' * 40

MOCK = r'''
class FakeDockerProcess {
    [IO.StringReader]$StandardOutput
    [IO.StringReader]$StandardError
    [IO.StringWriter]$StandardInput = [IO.StringWriter]::new()
    [int]$ExitCode = 0
    [bool]$Timeout = $false
    [string[]]$Arguments
    [bool] WaitForExit([int]$milliseconds) { return -not $this.Timeout }
    [void] Kill([bool]$tree) { }
    [void] Dispose() {
        @{args=$this.Arguments; input=$this.StandardInput.ToString()} | ConvertTo-Json -Compress -Depth 20 |
            Add-Content -LiteralPath $env:MOCK_LOG
    }
}
function New-MockDockerProcess($info) {
    $p = [FakeDockerProcess]::new()
    $p.Arguments = @($info.ArgumentList)
    $a = $p.Arguments
    $text = ''
    if ($a -contains 'ps') { $text = 'bbbbbbbbbbbb' }
    elseif ($a -contains 'inspect') {
        $text = @{Config=@{Labels=@{
            'com.docker.compose.project'=$env:COMPOSE_PROJECT_NAME
            'com.docker.compose.service'='hermes'
            'com.docker.compose.project.working_dir'=$PSScriptRoot
        }};Mounts=@(@{Destination='/opt/data';Source=$env:HERMES_PROJECT_HOME})} | ConvertTo-Json -Depth 10 -Compress
        if ($env:MOCK_CASE -eq 'desktop-mount') {
            $mount = $env:HERMES_PROJECT_HOME.Replace('\', '/') -replace '^([a-zA-Z]):/', '/run/desktop/mnt/host/$1/'
            $object = $text | ConvertFrom-Json
            $object.Mounts[0].Source = $mount
            $text = $object | ConvertTo-Json -Depth 10 -Compress
        }
        if ($env:MOCK_CASE -eq 'ownership') { $text = $text.Replace('"hermes"','"unrelated"') }
    } elseif ($a -contains 'exec') {
        $script:turnCount++
        $answer = 'Source bounded hypothesis analysis; profitability UNKNOWN.'
        if ($script:turnCount -eq 1) {
            $answer = @{sources=@(@{id='S1';kind='public';url_or_uri='https://example.org/source'})
                hypotheses=@('one','two','three');materials_markdown='Supplied source data'} | ConvertTo-Json -Depth 10 -Compress
        }
        if ($env:MOCK_CASE -eq 'missing' -and $script:turnCount -eq 2) { $answer = '' }
        if ($env:MOCK_CASE -eq 'secret' -and $script:turnCount -eq 2) { $answer = $env:BROWSERBASE_API_KEY }
        if ($env:MOCK_CASE -eq 'unknown-token' -and $script:turnCount -eq 2) { $answer = 'Bearer unregistered-test-credential-value' }
        if ($env:MOCK_CASE -eq 'failed' -and $script:turnCount -eq 2) { $p.ExitCode = 3 }
        if ($env:MOCK_CASE -eq 'timeout' -and $script:turnCount -eq 2) { $p.Timeout = $true }
        $text = @{type='result';session_id="real-protocol-mocked-$script:turnCount";exit_code=$p.ExitCode;text=$answer} | ConvertTo-Json -Compress
    }
    $p.StandardOutput = [IO.StringReader]::new($text)
    $p.StandardError = [IO.StringReader]::new('diagnostic that must not be published')
    return $p
}
function global:git {
    $global:LASTEXITCODE = 0
    if ($args -contains 'rev-parse') { return ('a' * 40) }
    if ($args -contains 'branch') {
        if ($env:MOCK_CASE -eq 'identity') { return 'codex/wrong-branch' }
        return 'codex/research-test'
    }
}
$script:turnCount = 0
'''


def run_script(tmp_path, case='success', extra=()):
    pwsh = shutil.which('pwsh')
    if not pwsh:
        pytest.skip('PowerShell 7 required for operator behavior tests')
    folder = tmp_path / 'repo/tools/hermes'
    folder.mkdir(parents=True, exist_ok=True)
    source = SCRIPT.read_text(encoding='utf-8')
    # Keep all validation/argv/I/O/finalization code. Replace only Process.Start.
    source = source.replace('$process = [Diagnostics.Process]::Start($info)', '$process = New-MockDockerProcess $info')
    insertion = source.index("$ErrorActionPreference = 'Stop'")
    source = source[:insertion] + MOCK + source[insertion:]
    copy = folder / 'research_turn.ps1'
    copy.write_text(source, encoding='utf-8')
    output = tmp_path / 'output'
    env = dict(os.environ, COMPOSE_PROJECT_NAME='cpw-hermes-research-test',
               HERMES_PROJECT_HOME=str(tmp_path / 'home'), MOCK_CASE=case,
               MOCK_LOG=str(tmp_path / 'calls.jsonl'), BROWSERBASE_API_KEY='test-credential-marker-123')
    if case == 'existing-output':
        output.mkdir()
        (output / 'preserve.txt').write_text('untouched')
    if case == 'inside-repo':
        output = folder / 'output'
    if case == 'project':
        env['COMPOSE_PROJECT_NAME'] = 'unrelated-project'
    result = subprocess.run([pwsh, '-NoProfile', '-File', str(copy), '-OutputRoot', str(output),
                             '-RepoSha', SHA, '-RepoBranch', 'codex/research-test', '-Theme',
                             'BTC $(do-not-execute); funding "source text"', *extra],
                            env=env, capture_output=True, text=True, timeout=30)
    log = tmp_path / 'calls.jsonl'
    calls = [json.loads(line) for line in log.read_text(encoding='utf-8-sig').splitlines()] if log.exists() else []
    return result, output, calls


@pytest.mark.parametrize('case', ['success', 'desktop-mount'])
def test_one_cycle_exact_commands_profiles_and_atomic_artifacts(tmp_path, case):
    result, output, calls = run_script(tmp_path, case)
    assert result.returncode == 0, result.stdout + result.stderr
    manifest = json.loads((output / 'run_manifest.json').read_text())
    assert manifest['state'] == 'COMPLETED'
    assert len(manifest['invocations']) == 4
    assert all(x['exit_code'] == 0 and x['session_id'] for x in manifest['invocations'])
    turns = [c for c in calls if 'exec' in c['args']]
    assert len(turns) == 4
    for role, call in zip(('director-sources', 'research-scout', 'research-critic', 'director-synthesis'), turns):
        args = call['args']
        assert args[args.index('--query-file') + 1] == '-'
        assert 'timeout' in args and '--kill-after=10' in args
        assert '--oneshot' in args and '--reasoning' in args and 'high' in args
        assert args[args.index('--toolsets') + 1] == ('search,skills,project-evidence' if role == 'director-sources' else 'memory,session_search')
        assert '$(do-not-execute)' in call['input'] and '$(do-not-execute)' not in args
        if role.startswith('research-'):
            assert args[args.index('-p', 2) + 1] == role
            for name in ('BROWSERBASE_API_KEY', 'BROWSERBASE_PROJECT_ID', 'OPENAI_API_KEY',
                         'TERMINAL_SSH_KEY', 'RESEARCH_MEMORY_READONLY_DSN'):
                index = args.index(name)
                assert args[index - 1] == '-u'
    assert (output / 'source_index.json').is_file()
    assert (output / 'scout_result.md').is_file()
    assert (output / 'critic_result.md').is_file()
    assert (output / 'research_opportunity_brief.md').is_file()
    assert not list(tmp_path.glob('*.partial-*'))
    assert 'diagnostic that must not be published' not in ''.join(p.read_text() for p in output.iterdir())


@pytest.mark.parametrize('case', ['missing', 'failed', 'secret', 'unknown-token', 'timeout'])
def test_failure_is_nonzero_no_retry_no_success_brief_and_owned_cleanup(tmp_path, case):
    result, output, calls = run_script(tmp_path, case)
    assert result.returncode != 0
    manifest = json.loads((output / 'run_manifest.json').read_text())
    assert manifest['state'] == 'FAILED'
    assert len([c for c in calls if 'exec' in c['args']]) == 2
    assert calls[-1]['args'] == ['stop', '--time', '10', 'bbbbbbbbbbbb']
    assert not (output / 'research_opportunity_brief.md').exists()
    assert not list(tmp_path.glob('*.partial-*'))
    assert 'test-credential-marker-123' not in ''.join(p.read_text() for p in output.iterdir())
    assert 'unregistered-test-credential-value' not in ''.join(p.read_text() for p in output.iterdir())


def test_unowned_service_rejected_before_model_invocation(tmp_path):
    result, output, calls = run_script(tmp_path, 'ownership')
    assert result.returncode != 0
    assert not output.exists()
    assert not any('exec' in c['args'] or 'stop' in c['args'] for c in calls)


def test_schedule_argument_is_not_accepted(tmp_path):
    result, output, calls = run_script(tmp_path, extra=('-InstallSchedules',))
    assert result.returncode != 0
    assert not output.exists() and not calls


@pytest.mark.parametrize('case', ['identity', 'project', 'inside-repo', 'existing-output'])
def test_invalid_operator_inputs_do_not_invoke_docker_or_overwrite(tmp_path, case):
    result, output, calls = run_script(tmp_path, case)
    assert result.returncode != 0
    assert not calls
    if case == 'existing-output':
        assert (output / 'preserve.txt').read_text() == 'untouched'
    else:
        assert not output.exists()


ADAPTER_STUB = '''import json, os, sys
with open(os.environ["MOCK_ADAPTER_LOG"], "w", encoding="utf-8") as handle:
    json.dump(sys.argv[1:], handle)
raise SystemExit(int(os.environ.get("MOCK_ADAPTER_EXIT", "0")))
'''


@pytest.mark.parametrize('adapter_exit', [0, 3])
def test_structured_intent_handoff_is_opt_in_fifth_turn_and_packet(tmp_path, monkeypatch, adapter_exit):
    import sys
    stub_log = tmp_path / 'adapter.json'
    monkeypatch.setenv('MOCK_ADAPTER_LOG', str(stub_log))
    monkeypatch.setenv('MOCK_ADAPTER_EXIT', str(adapter_exit))
    (tmp_path / 'repo/tools/hermes').mkdir(parents=True)
    (tmp_path / 'repo/tools/hermes/discovery_intent.py').write_text(ADAPTER_STUB, encoding='utf-8')
    result, output, calls = run_script(tmp_path, extra=('-StructuredIntentHandoff', '-PythonExe', sys.executable))
    manifest = json.loads((output / 'run_manifest.json').read_text())
    assert manifest['state'] == 'COMPLETED'
    roles = [x['role'] for x in manifest['invocations']]
    assert roles == ['director-sources', 'research-scout', 'research-critic', 'director-synthesis', 'director-intent']
    turns = [c for c in calls if 'exec' in c['args']]
    intent = turns[4]
    assert intent['args'][intent['args'].index('--toolsets') + 1] == 'memory,session_search'
    assert '-p' not in intent['args'][intent['args'].index('hermes', 5):]
    assert 'cpw_bounded_research_request_v1' in intent['input'] and 'Independent critic:' in intent['input']
    assert 'admitted or executable intents, dispatch' in intent['input'] and 'RESEARCH-INTENT DRAFTS' in intent['input']
    assert 'prepared payloads, intents, canonical writes' not in intent['input']
    assert all('prepared payloads, intents, canonical writes' in t['input'] for t in turns[:4])
    assert (output / 'structured_intent_drafts.json').is_file()
    assert json.loads(stub_log.read_text()) == ['build', '--cycle-dir', str(output),
                                                '--output', str(output) + '.discovery-intent']
    assert (result.returncode == 0) == (adapter_exit == 0)


def test_default_cycle_never_runs_intent_turn_or_adapter(tmp_path):
    result, output, calls = run_script(tmp_path)
    assert result.returncode == 0
    assert not any('director-intent' in json.dumps(c) for c in calls)
    assert not (output / 'structured_intent_drafts.json').exists()
    assert not list(tmp_path.glob('*.discovery-intent'))
