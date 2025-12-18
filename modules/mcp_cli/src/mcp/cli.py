import argparse


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="mcp")
    parser.add_argument("--version", action="store_true")
    args = parser.parse_args(argv)

    if args.version:
        print("0.0.0")
        return 0

    parser.print_help()
    return 0
