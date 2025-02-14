import argparse
import atexit
import logging
import sys

import uvicorn

from api import app
from info_handler import setup_database
from settings import get_settings
from sniffers import sniff_manager

logging.basicConfig(level=logging.NOTSET, format='%(asctime)s %(module)s %(levelname)s %(message)s')


def parse_args() -> argparse.Namespace:
    """
    Parses and returns arguments passed to script.

    Returns:
        Namespace: Parsed arguments.
    """
    arg_parser = argparse.ArgumentParser(prog="Super cool Drone Monitor System")
    arg_parser.add_argument("-p", "--port", help="port", type=int, default=80)
    arg_parser.add_argument("-f", "--file", help="pcap file name")
    #arg_parser.add_argument("-l", "--lte", action="store_true", help="sniff on lte")
    return arg_parser.parse_args()


def shutdown() -> None:
    """
    Stops all services, handlers & connections on shutdown.
    """
    sniff_manager.shutdown()


def main():
    args = parse_args()
    port: int = args.port
    file: str = args.file
    #lte: bool = args.lte

    logging.info("Setting up database...")
    setup_database()

    # register shutdown manager
    atexit.register(shutdown)

    try:
        if file:  #or lte:
            logging.info(f"Started with file argument, starting parsing of {file}")
            sniff_manager.parse_file(file) #, lte=lte)

        logging.info("Starting sniff manager...")
        settings = get_settings()
        sniff_manager.set_sniffing_interfaces(settings.interfaces)

        logging.info(f"Starting API on port {port}...")
        uvicorn.run(app, host='0.0.0.0', port=port)
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == '__main__':
    main()
