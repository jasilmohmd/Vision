"""Map Arduino's generated sources to the original sketches for IntelliSense.

Run after compiling camera_head and/or voice_unit. No credential contents are
read. Generated database stays under the ignored firmware/.build directory.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


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
    output.write_text(json.dumps(commands, indent=2) + "\n", encoding="utf-8")
    print(f"Mapped {len(commands) // 2} sketch(es) into {output.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
