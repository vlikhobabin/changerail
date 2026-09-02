#!/usr/bin/env python3
"""Exercise the Linux repo-local Codex launcher without credentials or network."""

from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import tempfile
import time
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = ROOT / "bin" / "codex"
CONFIG = ROOT / ".codex" / "config.toml"
FAILURE_PREFIX = "changerail codex launcher: "
ROOT_CONFLICT = "user arguments must not override launcher-managed working root (-C/--cd)"
FILESYSTEM_CONFLICT = "user config override conflicts with launcher-managed filesystem MCP scope"
TRUST_CONFLICT = "user config override conflicts with launcher-managed project trust"
CONFIG_SOURCE_CONFLICT = "user arguments must not bypass launcher-managed Codex config (--ignore-user-config)"
UNCLASSIFIED_CONFIG = "cannot classify user Codex config override as an unrelated key=value"


def make_executable(path: Path, content: str) -> Path:
    path.write_text(content, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return path


def stage_checkout(parent: Path, name: str) -> Path:
    checkout = parent / name
    (checkout / "bin").mkdir(parents=True)
    (checkout / ".codex").mkdir()
    shutil.copy2(LAUNCHER, checkout / "bin" / "codex")
    shutil.copy2(CONFIG, checkout / ".codex" / "config.toml")
    return checkout


def fake_dispatcher(path: Path, *, label: str = "fake") -> Path:
    label_literal = json.dumps(label, ensure_ascii=False)
    return make_executable(
        path,
        f"""#!/usr/bin/python3
import json
import os
import pathlib
import sys

capture = pathlib.Path(os.environ["CHANGERAIL_LAUNCHER_CAPTURE"])
capture.write_text(json.dumps({{
    "argv": sys.argv[1:],
    "CODEX_HOME": os.environ.get("CODEX_HOME"),
    "CODEX_WORKDIR": os.environ.get("CODEX_WORKDIR"),
    "label": {label_literal},
}}, ensure_ascii=False), encoding="utf-8")
""",
    )


def run_launcher(
    checkout: Path,
    capture: Path,
    *,
    dispatcher: str | Path | None,
    args: list[str] | None = None,
    path: str | None = None,
    cwd: Path | None = None,
    timeout: float = 15,
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["CHANGERAIL_LAUNCHER_CAPTURE"] = str(capture)
    env["CODEX_WORKDIR"] = "/opt/example-project"
    if dispatcher is None:
        env.pop("CHANGERAIL_CODEX_BIN", None)
    else:
        env["CHANGERAIL_CODEX_BIN"] = str(dispatcher)
    if path is not None:
        env["PATH"] = path
    return subprocess.run(
        [str(checkout / "bin" / "codex"), *(args or ["exec", "--json", "prompt with spaces"])],
        cwd=cwd or checkout.parent,
        env=env,
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def load_capture(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def merge_config(target: dict[str, object], update: dict[str, object]) -> None:
    for key, value in update.items():
        current = target.get(key)
        if isinstance(current, dict) and isinstance(value, dict):
            merge_config(current, value)
        else:
            target[key] = value


def effective_exec_config(argv: list[str]) -> dict[str, object]:
    """Model the Codex 0.152.1 exec-local override layer seen by regressions."""
    terminator = argv.index("--") if "--" in argv else len(argv)
    exec_positions = [
        index for index, value in enumerate(argv[:terminator]) if value in ("exec", "e")
    ]
    assert exec_positions, argv
    effective: dict[str, object] = {}
    index = exec_positions[0] + 1
    while index < terminator:
        argument = argv[index]
        override: str | None = None
        if argument in ("-c", "--config"):
            index += 1
            override = argv[index]
        elif argument.startswith("--config="):
            override = argument.removeprefix("--config=")
        elif argument.startswith("-c") and len(argument) > 2:
            override = argument[3:] if argument.startswith("-c=") else argument[2:]
        if override is not None:
            merge_config(effective, tomllib.loads(override))
        index += 1
    return effective


def assert_scope(payload: dict[str, object], checkout: Path, user_args: list[str]) -> None:
    root = str(checkout.resolve())
    argv = payload["argv"]
    assert isinstance(argv, list)
    assert argv[:2] == ["-C", root]
    assert argv[2] == "-c" and argv[4] == "-c"
    overrides = tomllib.loads(f"{argv[3]}\n{argv[5]}\n")
    assert overrides["projects"] == {root: {"trust_level": "trusted"}}
    tracked = tomllib.loads((checkout / ".codex/config.toml").read_text())
    expected_args = [*tracked["mcp_servers"]["filesystem"]["args"][:-1], root]
    expected_filesystem = dict(tracked["mcp_servers"]["filesystem"])
    expected_filesystem["args"] = expected_args
    assert overrides["mcp_servers"]["filesystem"] == expected_filesystem
    expected_tail = list(user_args)
    terminator = expected_tail.index("--") if "--" in expected_tail else len(expected_tail)
    if any(value in ("exec", "e") for value in expected_tail[:terminator]):
        expected_tail[terminator:terminator] = ["-c", argv[3], "-c", argv[5]]
        effective = effective_exec_config(argv)
        assert effective["projects"][root] == {"trust_level": "trusted"}
        assert effective["mcp_servers"]["filesystem"] == expected_filesystem
    assert argv == [*argv[:6], *expected_tail]
    assert payload["CODEX_WORKDIR"] == root
    assert payload["CODEX_HOME"] == str(checkout / ".codex")


def assert_success(
    result: subprocess.CompletedProcess[str],
    capture: Path,
    checkout: Path,
    args: list[str],
    *,
    label: str = "fake",
) -> None:
    assert result.returncode == 0, result.stderr
    assert result.stdout == ""
    assert result.stderr == ""
    payload = load_capture(capture)
    assert payload["label"] == label
    assert_scope(payload, checkout, args)


def assert_failure(
    result: subprocess.CompletedProcess[str], capture: Path, diagnostic: str
) -> None:
    assert result.returncode == 1, (result.returncode, result.stdout, result.stderr)
    assert result.stdout == ""
    assert result.stderr == f"{FAILURE_PREFIX}{diagnostic}\n"
    assert not capture.exists()


def check_stable_config() -> None:
    config = tomllib.loads(CONFIG.read_text(encoding="utf-8"))
    assert config["approval_policy"] == "never"
    assert config["sandbox_mode"] == "danger-full-access"
    assert config["projects"] == {"/opt/changerail": {"trust_level": "trusted"}}
    assert config["mcp_servers"]["filesystem"]["args"][-1] == "/opt/changerail"


def check_path_bytes(tmp: Path) -> None:
    names = [
        "Unicode Ж portable 'single' \"double\" \\ root",
        "internal\bbackspace",
        "internal\ttab",
        "internal\nnewline",
        "internal\fform-feed",
        "internal\rcarriage-return",
        "terminal-space ",
        "terminal-backspace\b",
        "terminal-tab\t",
        "terminal-newline\n",
        "terminal-form-feed\f",
        "terminal-carriage-return\r",
    ]
    dispatcher = fake_dispatcher(tmp / "path-bytes-dispatcher")
    for index, name in enumerate(names):
        checkout = stage_checkout(tmp, name)
        capture = tmp / f"path-bytes-{index}.json"
        args = ["exec", "--json", f"prompt-{index}"]
        result = run_launcher(checkout, capture, dispatcher=dispatcher, args=args)
        assert_success(result, capture, checkout, args)
        assert "/opt/changerail" not in json.dumps(
            load_capture(capture)["argv"], ensure_ascii=False
        )


def check_explicit_dispatchers(tmp: Path) -> None:
    checkout = stage_checkout(tmp, "explicit-dispatchers")
    dispatcher_dir = tmp / "explicit-bin"
    dispatcher_dir.mkdir()
    direct = fake_dispatcher(dispatcher_dir / "codex", label="direct")
    args = ["exec", "--json", "explicit path"]

    capture = tmp / "explicit-path.json"
    result = run_launcher(checkout, capture, dispatcher=direct, args=args)
    assert_success(result, capture, checkout, args, label="direct")

    capture = tmp / "explicit-bare.json"
    result = run_launcher(
        checkout,
        capture,
        dispatcher="codex",
        args=args,
        path=str(dispatcher_dir),
    )
    assert_success(result, capture, checkout, args, label="direct")

    symlink = tmp / "symlink-dispatcher"
    symlink.symlink_to(direct)
    capture = tmp / "explicit-symlink.json"
    result = run_launcher(checkout, capture, dispatcher=symlink, args=args)
    assert_success(result, capture, checkout, args, label="direct")

    elf_result = run_launcher(
        checkout,
        tmp / "unused-elf-capture.json",
        dispatcher=Path("/bin/true"),
        args=["--version"],
    )
    assert elf_result.returncode == 0
    assert elf_result.stdout == "" and elf_result.stderr == ""


def check_path_resolution(tmp: Path) -> None:
    checkout = stage_checkout(tmp, "path-resolution")
    cwd = tmp / "path-cwd"
    cwd.mkdir()
    fake_dispatcher(cwd / "codex", label="cwd")
    relative_dir = cwd / "relative-bin"
    relative_dir.mkdir()
    fake_dispatcher(relative_dir / "codex", label="relative")
    external_dir = tmp / "external-bin"
    external_dir.mkdir()
    fake_dispatcher(external_dir / "codex", label="external")
    missing = str(tmp / "missing")
    cases = [
        (f":{missing}", "cwd"),
        (f"{missing}::{tmp / 'also-missing'}", "cwd"),
        (f"{missing}:", "cwd"),
        ("", "cwd"),
        ("relative-bin", "relative"),
        (f"{checkout / 'bin'}:{external_dir}", "external"),
    ]
    args = ["exec", "--json", "PATH matrix"]
    for index, (path, label) in enumerate(cases):
        capture = tmp / f"path-case-{index}.json"
        result = run_launcher(
            checkout, capture, dispatcher=None, args=args, path=path, cwd=cwd
        )
        assert_success(result, capture, checkout, args, label=label)

    for kind in ("symlink", "hardlink"):
        identity_dir = tmp / f"{kind}-self-bin"
        identity_dir.mkdir()
        identity = identity_dir / "codex"
        if kind == "symlink":
            identity.symlink_to(checkout / "bin" / "codex")
        else:
            os.link(checkout / "bin" / "codex", identity)
        capture = tmp / f"path-skip-{kind}.json"
        result = run_launcher(
            checkout,
            capture,
            dispatcher=None,
            args=args,
            path=f"{identity_dir}:{external_dir}",
            cwd=cwd,
        )
        assert_success(result, capture, checkout, args, label="external")


def check_recursion_and_dispatcher_failures(tmp: Path) -> None:
    checkout = stage_checkout(tmp, "dispatcher-failures")
    capture = tmp / "failure-capture.json"
    identities: list[Path] = [checkout / "bin" / "codex"]
    symlink = tmp / "symlinked-launcher"
    symlink.symlink_to(checkout / "bin" / "codex")
    identities.append(symlink)
    hardlink = tmp / "hardlinked-launcher"
    os.link(checkout / "bin" / "codex", hardlink)
    identities.append(hardlink)
    for identity in identities:
        result = run_launcher(checkout, capture, dispatcher=identity)
        assert_failure(result, capture, "CHANGERAIL_CODEX_BIN resolves to this launcher")

    invalid = tmp / "not-executable"
    invalid.write_text("not executable\n", encoding="utf-8")
    result = run_launcher(checkout, capture, dispatcher=invalid)
    assert_failure(
        result, capture, "CHANGERAIL_CODEX_BIN does not resolve to an executable"
    )

    result = run_launcher(
        checkout,
        capture,
        dispatcher="missing-codex",
        path=str(tmp / "missing-bin"),
    )
    assert_failure(
        result, capture, "CHANGERAIL_CODEX_BIN does not resolve to an executable"
    )

    result = run_launcher(
        checkout,
        capture,
        dispatcher=None,
        path=f"{checkout / 'bin'}:{tmp / 'missing-bin'}",
    )
    assert_failure(result, capture, "no external codex dispatcher found in PATH")


def check_argument_policy(tmp: Path) -> None:
    checkout = stage_checkout(tmp, "argument-policy")
    dispatcher = fake_dispatcher(tmp / "argument-policy-dispatcher")
    capture = tmp / "argument-policy.json"
    root_literal = json.dumps(str(checkout.resolve()), ensure_ascii=False)
    project_override = f"projects.{root_literal}.trust_level=\"untrusted\""

    protected = [
        (["-c", "mcp_servers={}", "exec"], FILESYSTEM_CONFLICT),
        (["-c", "mcp_servers.filesystem={}", "exec"], FILESYSTEM_CONFLICT),
        (["-c", "mcp_servers.filesystem.args=[]", "exec"], FILESYSTEM_CONFLICT),
        (["exec", "-c", "mcp_servers.filesystem.enabled=false"], FILESYSTEM_CONFLICT),
        (["exec", "-c", 'mcp_servers.filesystem.command="/bin/false"'], FILESYSTEM_CONFLICT),
        (["exec", "-c", 'mcp_servers.filesystem.cwd="/opt/example-a"'], FILESYSTEM_CONFLICT),
        (["exec", "-c", 'mcp_servers.filesystem.env={TOKEN="x"}'], FILESYSTEM_CONFLICT),
        (["exec", "-c", "mcp_servers.filesystem.startup_timeout_sec=1"], FILESYSTEM_CONFLICT),
        (["exec", "-c", "mcp_servers.filesystem.tool_timeout_sec=1"], FILESYSTEM_CONFLICT),
        (["exec", "-c", 'mcp_servers.filesystem.enabled_tools=["read_file"]'], FILESYSTEM_CONFLICT),
        (["exec", "-c", 'mcp_servers.filesystem.disabled_tools=["write_file"]'], FILESYSTEM_CONFLICT),
        (["exec", "-c", "mcp_servers.filesystem.future_field=true"], FILESYSTEM_CONFLICT),
        (["exec", "--config", "mcp_servers.filesystem={args=[]}"], FILESYSTEM_CONFLICT),
        (["exec", "-c=mcp_servers.filesystem.args=[]"], FILESYSTEM_CONFLICT),
        (["--config=mcp_servers.filesystem.args=[]", "exec"], FILESYSTEM_CONFLICT),
        (["exec", "-cmcp_servers.filesystem.args=[]"], FILESYSTEM_CONFLICT),
        (["exec", "-c", project_override], TRUST_CONFLICT),
        (["--config", "projects={}", "exec"], TRUST_CONFLICT),
    ]
    for args, diagnostic in protected:
        result = run_launcher(checkout, capture, dispatcher=dispatcher, args=args)
        assert_failure(result, capture, diagnostic)

    bypasses = [
        ["--ignore-user-config", "exec", "prompt"],
        ["exec", "--ignore-user-config", "prompt"],
        ["exec", "--ignore-user-config", "--ignore-user-config", "prompt"],
    ]
    for args in bypasses:
        result = run_launcher(checkout, capture, dispatcher=dispatcher, args=args)
        assert_failure(result, capture, CONFIG_SOURCE_CONFLICT)

    root_conflicts = [
        ["-C", "/opt/example-a", "exec"],
        ["exec", "--cd", "/opt/example-a"],
        ["exec", "--cd=/opt/example-a"],
        ["-C=/opt/example-a", "exec"],
        ["exec", "-C/opt/example-a"],
    ]
    for args in root_conflicts:
        result = run_launcher(checkout, capture, dispatcher=dispatcher, args=args)
        assert_failure(result, capture, ROOT_CONFLICT)

    for args in (["exec", "-c"], ["--config", "not-an-assignment", "exec"]):
        result = run_launcher(checkout, capture, dispatcher=dispatcher, args=list(args))
        assert_failure(result, capture, UNCLASSIFIED_CONFIG)

    unrelated = [
        "-c",
        'model="gpt-5"',
        "exec",
        "--profile",
        "adversarial",
        "--config=features.goals=false",
        "-cfeatures.multi_agent=true",
        '--config=projects."/opt/example-b".trust_level="untrusted"',
        '-cmcp_servers.context7.args=["--transport","stdio"]',
        "--json",
        "prompt",
    ]
    result = run_launcher(checkout, capture, dispatcher=dispatcher, args=unrelated)
    assert_success(result, capture, checkout, unrelated)

    after_terminator = [
        "exec",
        "--",
        "--config=mcp_servers.filesystem.args=[]",
        "-C/opt/example-a",
    ]
    capture = tmp / "after-terminator.json"
    result = run_launcher(checkout, capture, dispatcher=dispatcher, args=after_terminator)
    assert_success(result, capture, checkout, after_terminator)


def check_helper_hijack(tmp: Path) -> None:
    checkout = stage_checkout(tmp, "helper-hijack")
    hijack = tmp / "hijack-bin"
    hijack.mkdir()
    marker = tmp / "helper-hijack-marker"
    helper = f"#!/bin/sh\nprintf '%s\\n' \"$0\" >> {str(marker)!r}\nexit 91\n"
    for name in ("bash", "dirname", "python3", "readlink"):
        make_executable(hijack / name, helper)
    dispatcher_dir = tmp / "helper-dispatcher-bin"
    dispatcher_dir.mkdir()
    fake_dispatcher(dispatcher_dir / "codex", label="trusted-helpers")
    capture = tmp / "helper-hijack.json"
    args = ["exec", "--json", "helper path"]
    result = run_launcher(
        checkout,
        capture,
        dispatcher=None,
        args=args,
        path=f"{hijack}:{dispatcher_dir}",
    )
    assert_success(result, capture, checkout, args, label="trusted-helpers")
    assert not marker.exists()


def check_pinned_dispatcher_replacement(tmp: Path) -> None:
    checkout = stage_checkout(tmp, "pinned-dispatcher")
    config = checkout / ".codex" / "config.toml"
    with config.open("a", encoding="utf-8") as stream:
        stream.write("# dispatcher-open race window\n" * 300_000)
    candidate = fake_dispatcher(tmp / "mutable-codex", label="opened-original")
    replacement = fake_dispatcher(tmp / "replacement-codex", label="path-replacement")
    original_stat = candidate.stat()
    capture = tmp / "pinned-replacement.json"
    args = ["exec", "--json", "pinned inode"]
    env = os.environ.copy()
    env["CHANGERAIL_LAUNCHER_CAPTURE"] = str(capture)
    env["CHANGERAIL_CODEX_BIN"] = str(candidate)
    process = subprocess.Popen(
        [str(checkout / "bin" / "codex"), *args],
        cwd=checkout.parent,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    observed_open = False
    deadline = time.monotonic() + 10
    while process.poll() is None and time.monotonic() < deadline:
        fd_dir = Path(f"/proc/{process.pid}/fd")
        try:
            descriptors = list(fd_dir.iterdir())
        except (FileNotFoundError, PermissionError):
            descriptors = []
        for descriptor in descriptors:
            try:
                opened = descriptor.stat()
            except FileNotFoundError:
                continue
            if (opened.st_dev, opened.st_ino) == (original_stat.st_dev, original_stat.st_ino):
                os.replace(replacement, candidate)
                observed_open = True
                break
        if observed_open:
            break
        time.sleep(0.0005)
    stdout, stderr = process.communicate(timeout=15)
    assert observed_open, "launcher never exposed an opened dispatcher descriptor"
    result = subprocess.CompletedProcess(process.args, process.returncode, stdout, stderr)
    assert_success(result, capture, checkout, args, label="opened-original")


def check_exact_failures(tmp: Path) -> None:
    checkout = stage_checkout(tmp, "exact-failures")
    dispatcher = fake_dispatcher(tmp / "unused-dispatcher")
    capture = tmp / "exact-failure.json"

    (checkout / ".codex" / "config.toml").unlink()
    result = run_launcher(checkout, capture, dispatcher=dispatcher)
    assert_failure(result, capture, "missing repository Codex config")

    unsafe = stage_checkout(tmp, "unsafe\vroot")
    result = run_launcher(unsafe, capture, dispatcher=dispatcher)
    assert_failure(result, capture, "repository path contains a TOML-unsafe control character")


def check_real_codex_if_available(tmp: Path) -> str:
    node_wrapper = Path("/usr/local/bin/codex")
    node_target = node_wrapper.resolve() if node_wrapper.is_file() else None
    node_available = bool(
        node_target
        and node_target.read_bytes().startswith(b"#!/usr/bin/env node\n")
    )
    resolved = str(node_wrapper) if node_available else shutil.which("codex")
    if resolved is None:
        return "unavailable"
    candidate = Path(resolved).resolve()
    try:
        if candidate.samefile(LAUNCHER):
            return "unavailable"
    except OSError:
        return "unavailable"
    is_node_wrapper = candidate.read_bytes().startswith(b"#!/usr/bin/env node\n")
    checkout = stage_checkout(tmp, "real-codex-version")
    result = run_launcher(
        checkout,
        tmp / "unused-real-capture.json",
        dispatcher=candidate,
        args=["--version"],
        timeout=20,
    )
    assert result.returncode == 0, result.stderr
    assert result.stderr == "" or result.stderr.startswith(
        "WARNING: proceeding, even though we could not create PATH aliases:"
    ), result.stderr
    assert result.stdout.startswith("codex-cli ")
    version = result.stdout.strip()
    if version != "codex-cli 0.152.1":
        return f"version-only ({version}; effective probes require 0.152.1)"

    recorder_output = tmp / "filesystem-recorder.json"
    recorder = make_executable(
        tmp / "filesystem-recorder",
        "#!/usr/bin/python3\n"
        "import json, pathlib, sys\n"
        f"pathlib.Path({str(recorder_output)!r}).write_text(json.dumps(sys.argv[1:]))\n",
    )
    config = checkout / ".codex" / "config.toml"
    config.write_text(
        "[mcp_servers.filesystem]\n"
        f"command = {json.dumps(str(recorder))}\n"
        'args = ["static-placeholder"]\n'
        "startup_timeout_sec = 1\n"
        "tool_timeout_sec = 1\n"
        "enabled = true\n",
        encoding="utf-8",
    )
    (checkout / ".codex" / "adversarial.config.toml").write_text(
        "[mcp_servers.filesystem]\n"
        'command = "/bin/false"\n'
        'args = ["profile-bypass"]\n'
        "enabled = false\n",
        encoding="utf-8",
    )
    config_probe = run_launcher(
        checkout,
        tmp / "unused-config-capture.json",
        dispatcher=candidate,
        args=["--profile", "adversarial", "mcp", "get", "filesystem", "--json"],
        timeout=20,
    )
    assert config_probe.returncode == 0, config_probe.stderr
    filesystem = json.loads(config_probe.stdout)
    assert filesystem["enabled"] is True
    assert filesystem["transport"]["command"] == str(recorder)
    assert filesystem["transport"]["args"] == [str(checkout.resolve())]

    exec_args = [
        "exec",
        "--ephemeral",
        "--skip-git-repo-check",
        "--profile",
        "adversarial",
        "-c",
        "plugins={}",
        "-c",
        'model_provider="launcher_local"',
        "-c",
        'model_providers.launcher_local={name="launcher_local",base_url="http://127.0.0.1:9",wire_api="responses"}',
        "probe",
    ]
    process = subprocess.Popen(
        [str(checkout / "bin" / "codex"), *exec_args],
        cwd=checkout.parent,
        env={
            **os.environ,
            "CHANGERAIL_CODEX_BIN": str(candidate),
            "CODEX_WORKDIR": "/opt/example-project",
        },
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )
    deadline = time.monotonic() + 15
    while process.poll() is None and not recorder_output.exists() and time.monotonic() < deadline:
        time.sleep(0.01)
    if process.poll() is None:
        os.killpg(process.pid, 15)
    stdout, stderr = process.communicate(timeout=10)
    assert recorder_output.exists(), (process.returncode, stdout, stderr)
    assert json.loads(recorder_output.read_text()) == [str(checkout.resolve())]
    dispatcher_kind = "Node /proc fd" if is_node_wrapper else "dispatcher /proc fd"
    return f"passed: {dispatcher_kind}, profile/config and exec effective layers"


def main() -> int:
    check_stable_config()
    with tempfile.TemporaryDirectory(prefix="changerail-codex-launcher-") as raw_tmp:
        tmp = Path(raw_tmp)
        check_path_bytes(tmp)
        check_explicit_dispatchers(tmp)
        check_path_resolution(tmp)
        check_recursion_and_dispatcher_failures(tmp)
        check_argument_policy(tmp)
        check_helper_hijack(tmp)
        check_pinned_dispatcher_replacement(tmp)
        check_exact_failures(tmp)
        real_codex = check_real_codex_if_available(tmp)
    print(
        json.dumps(
            {
                "status": "pass",
                "checks": [
                    "stable config invariants",
                    "Unicode and supported internal/terminal path bytes",
                    "explicit path/bare-name and script/symlink/ELF dispatchers",
                    "leading/middle/trailing/full-empty/relative PATH resolution",
                    "direct/symlink/hardlink recursion and dispatcher failures",
                    "global/exec protected and unrelated argument policy",
                    "effective exec-layer precedence and full filesystem subtree",
                    "config-load bypass rejection and adversarial profile layering",
                    "fixed launcher helper identities",
                    "descriptor-pinned dispatcher pathname replacement",
                    "exact stderr and exit behavior",
                ],
                "real_codex_credential_free_probes": real_codex,
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
