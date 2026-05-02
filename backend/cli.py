import argparse
import subprocess


def main() -> None:
    parser = argparse.ArgumentParser(prog="zhuotuan")
    subparsers = parser.add_subparsers(dest="command", required=True)

    dev_parser = subparsers.add_parser("dev", help="Run FastAPI dev server")
    dev_parser.add_argument("--host", default="127.0.0.1")
    dev_parser.add_argument("--port", type=int, default=8000)

    subparsers.add_parser("test", help="Run test suite")
    subparsers.add_parser("lint", help="Run linter")

    args = parser.parse_args()

    if args.command == "dev":
        command = [
            "uvicorn",
            "backend.app.main:app",
            "--reload",
            "--host",
            args.host,
            "--port",
            str(args.port),
        ]
    elif args.command == "test":
        command = ["pytest"]
    else:
        command = ["ruff", "check", "."]

    raise SystemExit(subprocess.call(command))
