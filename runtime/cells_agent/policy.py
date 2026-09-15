"""Command-aware advisory policy. Native host sandbox/permissions remain authoritative."""
from __future__ import annotations

from pathlib import Path
import re
import shlex

from .project import is_native_script, project_info, script_commands


def _commands(command: str) -> list[list[str]]:
    lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|()\n")
    lexer.whitespace_split = True
    lexer.commenters = "#"
    parts, current = [], []
    for token in lexer:
        if token and all(char in ";&|()\n" for char in token):
            if current:
                parts.append(current)
                current = []
        else:
            current.append(token)
    if current:
        parts.append(current)
    return parts


def assess_command(command: str, cwd: str | Path) -> dict:
    if not isinstance(command, str) or not command.strip() or len(command) > 100_000:
        return {"decision": "review", "reason": "Missing or oversized command payload"}
    try:
        commands = _commands(command)
        info = project_info(cwd)
    except (ValueError, OSError) as exc:
        return {"decision": "review", "reason": str(exc)}
    for words in commands:
        while words:
            if re.fullmatch(r"\w+=.*", words[0]):
                words = words[1:]
                continue
            wrapper = Path(words[0]).name
            if wrapper not in {"env", "command", "sudo"}:
                break
            words = words[1:]
            while words and words[0].startswith("-"):
                option = words.pop(0)
                if option == "--":
                    break
                if wrapper == "env" and option in {"-i", "--ignore-environment"} or wrapper == "sudo" and option in {"-n", "-E"}:
                    continue
                if wrapper == "sudo" and option in {"-u", "-g"} and words:
                    words.pop(0)
                    continue
                return {"decision": "review", "reason": f"Cannot resolve the {wrapper} wrapper option {option}; inspect its actual command before execution."}
        if not words:
            continue
        exe, args = Path(words[0]).name.lower(), words[1:]
        posix_shell = exe in {"sh", "bash", "zsh", "dash", "ksh", "ash"}
        shell_option = next((i for i, arg in enumerate(args) if arg in {"-c", "-lc", "-cl", "-ic", "-ci"}), None)
        if posix_shell and shell_option is not None:
            nested = args[shell_option + 1:]
            if nested and nested[0] == "--":
                nested = nested[1:]
            if nested:
                result = assess_command(nested[0], cwd)
                if result["decision"] != "allow":
                    return result
            else:
                return {"decision": "review", "reason": "Shell command payload is missing; inspect the actual command before execution."}
        elif posix_shell or exe in {"fish", "csh", "tcsh", "cmd", "cmd.exe", "powershell", "powershell.exe", "pwsh", "pwsh.exe"}:
            return {"decision": "review", "reason": "This shell wrapper requires direct inspection; its command syntax was not validated by the advisory policy."}
        if exe == "git":
            i = 0
            while i < len(args) and args[i].startswith("-"):
                i += 2 if args[i] in {"-C", "-c", "--git-dir", "--work-tree"} else 1
            op, rest = (args[i], args[i + 1:]) if i < len(args) else ("", [])
            destructive = (op == "reset" and "--hard" in rest or op == "clean" and any("f" in a for a in rest if a.startswith("-"))
                           or op in {"checkout", "restore"} and ("--" in rest or op == "restore")
                           or op == "push" and any(a == "-f" or a.startswith("--force") for a in rest))
            if destructive:
                return {"decision": "review", "reason": "This git operation may discard changes or rewrite remote history; exact user authorization is required."}
        if exe in {"rm", "rmdir", "del", "remove-item"}:
            flags = [arg.lower() for arg in args if arg.startswith(("-", "/"))]
            recursive = exe in {"rmdir", "remove-item", "del"} or any("r" in flag or flag == "--recursive" for flag in flags)
            targets = [arg for arg in args if not arg.startswith("-")]
            if recursive and any(target in {"/", ".", "..", "*", "./", "./*", "~"} for target in targets):
                return {"decision": "review", "reason": "Recursive deletion targets a root, working directory or wildcard; exact user authorization is required."}
        if info["is_cells"] and exe in {"npm", "pnpm", "yarn", "npx"}:
            script = None
            if args and args[0] in {"run", "run-script"} and len(args) >= 2:
                script = args[1]
            elif args and args[0] in {"test", "start"}:
                script = args[0]
            if exe == "npx" and any("web-test-runner" in arg for arg in args):
                return {"decision": "review", "reason": "Cells tests need a verified native script, not an unverified generic runner."}
            if script and (script.startswith("test") or script in {"coverage", "start", "dev"}):
                intent = "start" if script in {"start", "dev"} else "coverage" if "coverage" in script else "test"
                try:
                    native = is_native_script(script_commands(info["scripts"], script), intent)
                except ValueError:
                    native = False
                if not native:
                    return {"decision": "review", "reason": "Package script is not verified to resolve exclusively to the Cells CLI. Inspect the script and local command documentation."}
    return {"decision": "allow", "reason": "No scoped policy conflict recognized; command parsing is not a security sandbox."}


def assess_tool(payload: dict) -> dict:
    if not isinstance(payload, dict):
        return {"decision": "review", "reason": "Hook payload must be a JSON object"}
    name = str(payload.get("tool_name", payload.get("toolName", ""))).lower().split(".")[-1]
    if name not in {"bash", "exec_command", "runterminalcommand", "run_in_terminal", "runinterminal", "terminal"}:
        return {"decision": "allow", "reason": "Not a recognized command tool; prose is not evaluated as shell code."}
    inputs = payload.get("tool_input", payload.get("toolInput", {}))
    if not isinstance(inputs, dict):
        return {"decision": "review", "reason": "Command tool input must be an object"}
    return assess_command(inputs.get("command", inputs.get("cmd")), inputs.get("cwd", inputs.get("workdir", payload.get("cwd", "."))))
