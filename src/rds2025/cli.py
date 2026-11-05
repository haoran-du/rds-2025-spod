import argparse
import json
import sys
from pathlib import Path


def main(argv=None):
    parser = argparse.ArgumentParser(description="Paper-specific RdS reproduction; source data are read-only")
    sub = parser.add_subparsers(dest="command", required=True)
    recover = sub.add_parser("recover", help="Recover saved SPOD/POD eigenpairs")
    recover.add_argument("--verify-projection", action="store_true")
    commands = (recover,)
    for command in commands:
        command.add_argument("--data-root", type=Path, required=True)
        command.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    root, output = args.data_root.resolve(strict=True), args.output.resolve()
    if output == root or root in output.parents:
        parser.error("Output must be outside the read-only source data tree")
    if getattr(args, "batch", 1) < 1:
        parser.error("--batch must be positive")
    from .analysis import recover_spod
    result = recover_spod(args.data_root, args.output, args.verify_projection)
    print(json.dumps(result, indent=2))
    if result.get("failed"):
        sys.exit(1)


if __name__ == "__main__":
    main()
