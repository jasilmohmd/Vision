"""Phase 0 entry point: validate configuration without starting hardware."""

import argparse

from app.config import DEFAULT_CONFIG_PATH, load_config


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Hands-free photography rig (Phase 0 scaffold)")
    parser.add_argument("--config", default=DEFAULT_CONFIG_PATH, help="YAML configuration path")
    parser.add_argument("--mock", action="store_true", help="Use localhost mocks (runtime planned for Phase 3)")
    parser.add_argument("--mic", choices=("laptop", "udp"), default="laptop", help="Audio source (runtime planned for Phase 2)")
    args = parser.parse_args(argv)
    try:
        config = load_config(args.config)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(f"Configuration valid. Photo directory: {config.photos_dir}")
    print("Phase 0 scaffold only; runtime components are pending.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
