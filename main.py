import argparse

from cyber_orakel.server import run_server

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Print fortune cookie messages")
    parser.add_argument("--no-printer", action="store_true", help="Set this flag to disable printing, e.g. for testing")
    args = parser.parse_args()

    enable_printer = not args.no_printer
    run_server(enable_printer)
