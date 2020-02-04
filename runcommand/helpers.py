# -*- coding: utf-8 -*-

# standard library imports
import argparse
import ipaddress
import logging
import logging.config
import textwrap

# app imports
from .__version__ import __author__, __version__


def setup_logger(args) -> logging.Logger:
    if args.logging:
        if args.logging == "debug":
            logging_level = logging.DEBUG
        if args.logging == "warning":
            logging_level = logging.WARNING
    else:
        logging_level = logging.INFO

    default_logging = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"}
        },
        "handlers": {
            "default": {
                "level": logging_level,
                "formatter": "standard",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            }
        },
        "loggers": {"": {"handlers": ["default"], "level": logging_level}},
    }
    logging.config.dictConfig(default_logging)
    return logging.getLogger(__name__)


def setup_parser() -> argparse:
    """Setup the parser for arguments passed into the module from the CLI.

    Returns:
        argparse object.
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(
            """
            """
        ),
        epilog=f"Made with Python by {__author__}",
        fromfile_prefix_chars="2",
    )
    parser.add_argument(
        "--logging",
        help="change logging output",
        nargs="?",
        choices=("debug", "warning"),
    )
    parser.add_argument("cmd", help="command you want to run across controllers")
    parser.add_argument("iplist", help="file containing IPv4 addresses of controllers")
    parser.add_argument(
        "--syn",
        dest="syn",
        help="connect to controllers one at a time",
        action="store_true",
    )
    parser.add_argument(
        "--decrypt",
        dest="decrypt",
        help="runs encrypt disable before desired command",
        action="store_true",
    )
    parser.set_defaults(syn=False, decrypt=False)
    return parser


def is_valid_ipv4_address(ip_address):
    try:
        ipaddress.ip_address(ip_address)
    except ValueError:
        return False
    return True