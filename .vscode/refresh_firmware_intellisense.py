"""Map Arduino's generated sources to the original sketches for IntelliSense.

Run after compiling camera_head and/or voice_unit. No credential contents are
read. Generated database stays under the ignored firmware/.build directory.
"""
import json
import os
import shlex
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def expand_arguments(arguments, depth=0):
    if depth > 8:
        raise ValueError("Nested response files exceed limit")
    expanded = []
    for arg in arguments:
        if arg.startswith("@"):
            response = Path(arg[1:])
            expanded.extend(expand_arguments(shlex.split(response.read_text(encoding="utf-8")), depth + 1))
        else:
            expanded.append(arg)
    return expanded


def explicit_arguments(arguments):
    """Expose GCC's response-file and prefix include paths to the editor."""
    expanded = expand_arguments(arguments)
    result = []
    prefix = None
    i = 0
    while i < len(expanded):
        arg = expanded[i]
        if arg == "-iprefix":
            prefix = expanded[i + 1]
            i += 2
            continue
        if arg in ("-iwithprefixbefore", "-iwithprefix"):
            if prefix is None:
                raise ValueError("Prefix include without -iprefix")
            result.append("-I" + (Path(prefix) / expanded[i + 1]).as_posix())
            i += 2
            continue
        result.append(arg)
        i += 1
    compiler = Path(result[0])
    if not compiler.is_file() and compiler.with_suffix(".exe").is_file():
        result[0] = compiler.with_suffix(".exe").as_posix()
    return result


def main():
    commands = []
    for name in ("camera_head", "voice_unit", "wifi_diagnostic"):
        build = ROOT / "firmware" / ".build" / name
        database = build / "compile_commands.json"
        source_dir = ROOT / "firmware" / name
        if name == "wifi_diagnostic":
            source_dir = ROOT / "firmware" / "bench" / name
        if not database.is_file():
            continue
        for entry in json.loads(database.read_text(encoding="utf-8")):
            generated = Path(entry["file"])
            if generated.name != f"{name}.ino.cpp":
                continue
            entry = dict(entry)
            entry["arguments"] = explicit_arguments(entry["arguments"])
            commands.append(entry)
            original = source_dir / f"{name}.ino"
            mapped = dict(entry)
            mapped["file"] = str(original)
            mapped["arguments"] = [
                str(original) if arg == entry["file"] else arg
                for arg in entry["arguments"]
            ]
            # .ino is a C++ translation unit, despite its custom extension.
            mapped["arguments"][1:1] = ["-x", "c++"]
            commands.append(mapped)
    if not commands:
        raise SystemExit("Compile a firmware sketch first; no sketch commands found.")
    output = ROOT / "firmware" / ".build" / "intellisense_commands.json"
    temporary = output.with_suffix(".tmp")
    temporary.write_text(json.dumps(commands, indent=2) + "\n", encoding="utf-8")
    temporary.replace(output)
    # Standalone headers need explicit fallback settings too. Recursive SDK
    # search can pick a similarly named header for the wrong SDK component.
    config_file = ROOT / ".vscode" / "c_cpp_properties.json"
    config = json.loads(config_file.read_text(encoding="utf-8-sig"))
    for profile in config["configurations"]:
        chip = "esp32c3" if "C3" in profile["name"] else "esp32s3"
        sdk = Path(os.environ["LOCALAPPDATA"]) / "Arduino15/packages/esp32/tools" / f"{chip}-libs/3.3.11"
        flags = explicit_arguments([
            profile["compilerPath"], "@" + str(sdk / "flags/cpp_flags"),
            "-iprefix", str(sdk / "include") + "/", "@" + str(sdk / "flags/includes"),
            "@" + str(sdk / "flags/defines"),
        ])[1:]
        local_appdata = Path(os.environ["LOCALAPPDATA"]).as_posix()
        direct_includes = [arg[2:].replace(local_appdata, "${env:LOCALAPPDATA}")
                           for arg in flags if arg.startswith("-I")]
        direct_defines = [arg[2:] for arg in flags if arg.startswith("-D")]
        profile["includePath"] = list(dict.fromkeys(
            [path for path in profile["includePath"]
             if not path.endswith("/**") and f"/{chip}-libs/3.3.11/include/" not in path]
            + direct_includes
        ))
        profile["defines"] = list(dict.fromkeys(profile["defines"] + direct_defines))
        profile["compilerArgs"] = [arg for arg in flags if not arg.startswith(("-I", "-D"))]
    config_file.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    print(f"Mapped {len(commands) // 2} sketch(es) into {output.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
