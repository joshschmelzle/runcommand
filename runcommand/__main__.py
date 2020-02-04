#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
runcommand
~~~~~~~~~~

run a command on ArubaOS WLCs and save results
"""

# standard library imports
import getpass
import inspect
import logging
import logging.handlers
import sys
import threading
import time
from datetime import datetime

# third-party imports
import netmiko

# app imports
from . import helpers


class Worker(threading.Thread):
    def __init__(self, ip_address, command, decrypt, username, password, counter):
        threading.Thread.__init__(self)
        self.thread_id = counter
        self.ip_address = ip_address
        self.command = command
        self.decrypt = decrypt
        self.username = username
        self.password = password

    def run(self):
        start_time = datetime.now()
        log = logging.getLogger(inspect.stack()[0][3])
        log.info(
            "thread {0} - started {1} at {2}".format(
                self.thread_id, self.ip_address, datetime.now()
            )
        )
        run_cmd(
            self.ip_address,
            self.command,
            self.decrypt,
            self.username,
            self.password,
            self.thread_id,
        )
        log.info(
            "thread {0} - finished {1} in {2}".format(
                self.thread_id, self.ip_address, datetime.now() - start_time
            )
        )


def run_cmd(ip_address, command, decrypt, username, password, thread_id):
    log = logging.getLogger(inspect.stack()[0][3])
    try:
        log.info(
            f"thread {thread_id} - connecting to {ip_address} with user {username}"
        )

        wlc = netmiko.ConnectHandler(
            device_type="aruba_os", ip=ip_address, username=username, password=password
        )
        if decrypt:
            wlc.send_command("encrypt disable")

        hostname = wlc.send_command("show hostname")
        hostname = hostname.split(" ")[2].strip()

        results = wlc.send_command(command)

        if isinstance(results, str):
            log.info(
                "thread {0} - retrieved results from {1}".format(thread_id, hostname)
            )
            build_output_file(results, hostname, command, ip_address, thread_id)
    except netmiko.ssh_exception.NetMikoTimeoutException as ex:
        log.error("{0}.".format(ex))
        sys.exit(-1)
    except netmiko.ssh_exception.NetMikoAuthenticationException as ex:
        log.error("{0}.".format(ex))
        sys.exit(-1)


def getresults(args):
    log = logging.getLogger(inspect.stack()[0][3])

    i = 1
    controllers = []

    iplist = args.iplist
    command = args.cmd
    decrypt = args.decrypt

    if validateinput(args):
        with open(iplist) as file:
            for line in file:
                line = line.strip()
                if line == "":
                    continue
                if helpers.is_valid_ipv4_address(line):
                    controllers.append(line)

        log.info(f"controllers: {controllers}")

        if not controllers:
            log.error("no controllers, or valid IPv4 addresses provided.")
            sys.exit(-1)

        if controllers:
            username = input("username: ")
            log.info(f"user: {username}")
            password = getpass.getpass(prompt="password: ")

            for ip_address in controllers:
                worker = Worker(ip_address, command, decrypt, username, password, i)
                worker.start()
                if args.syn:
                    worker.join()
                i += 1


def validateinput(args) -> bool:
    log = logging.getLogger(inspect.stack()[0][3])
    if not validate_cmd(args.cmd):
        log.error(f"invalid command {args.cmd}")
        sys.exit(-1)
    return True


def validate_cmd(cmd: str) -> bool:
    if cmd.strip() == "":
        return False
    if len(cmd.split(" ")) == 1:
        return False
    if not isinstance(cmd, str):
        return False
    return True


def build_output_file(results, hostname, command, ip_address, thread_id):
    """
    - naming convention: [name]-[ip]-[command]-[time].cfg
    - write to same directory
    """
    log = logging.getLogger(inspect.stack()[0][3])
    curtime = time.strftime("%Y%m%dt%H%M")
    output_filename = (
        hostname
        + "-"
        + ip_address
        + "-"
        + command.replace(" ", "")
        + "-"
        + curtime
        + ".txt"
    )
    log.info(f"thread {thread_id} - writing results to {output_filename}")

    out_file = open(output_filename, "w")
    lines = results.splitlines()
    for line in lines:
        out_file.write(line + "\n")
    out_file.close()


def main() -> None:
    parser = helpers.setup_parser()
    args = parser.parse_args()

    log = helpers.setup_logger(args)
    log.info("args {0}".format(args))
    log.info("{0}".format(sys.version))

    getresults(args)


if __name__ == "__main__":
    main()
