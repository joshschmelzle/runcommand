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
    def __init__(
        self,
        platform: str,
        ip_address: str,
        command: str,
        decrypt: bool,
        username: str,
        password: str,
        counter: int,
    ):
        threading.Thread.__init__(self)
        self.thread_id = counter
        self.platform = platform
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
            self.platform,
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


def run_cmd(
    platform: str,
    ip_address: str,
    command_set: str,
    decrypt: bool,
    username: str,
    password: str,
    thread_id: int,
):
    log = logging.getLogger(inspect.stack()[0][3])
    try:
        log.info(
            f"thread {thread_id} - connecting to {ip_address} with user {username}"
        )

        wlc = netmiko.ConnectHandler(
            device_type=platform, ip=ip_address, username=username, password=password
        )
        if decrypt:
            wlc.send_command("encrypt disable")

        hostname = wlc.send_command("show hostname")
        hostname = hostname.split(" ")[2].strip()

        results = []
        for command in command_set:
            results.append(f"\n# command: {command}\n\n")
            results.append("```")
            results.append(wlc.send_command(command).strip())
            results.append("```")

        if isinstance(results, list):
            log.info(
                "thread {0} - retrieved results from {1}".format(thread_id, hostname)
            )
            build_output_file(results, hostname, ip_address, thread_id)
    except netmiko.ssh_exception.NetMikoTimeoutException as ex:
        log.error("{0}.".format(ex))
        sys.exit(-1)
    except netmiko.ssh_exception.NetMikoAuthenticationException as ex:
        log.error("{0}.".format(ex))
        sys.exit(-1)


def getresults(args):
    log = logging.getLogger(inspect.stack()[0][3])

    counter = 1
    controllers = []
    command_set = []

    iplist = args.iplist
    cmdlist = args.cmdlist

    if cmdlist:
        with open(cmdlist) as file:
            for line in file:
                line = line.strip()
                if line == "":
                    continue
                command_set.append(line)
    else:
        command_set.append(args.cmd)

    decrypt = args.decrypt

    if helpers.validateinput(args):
        if iplist:
            with open(iplist) as file:
                for line in file:
                    line = line.strip()
                    if line == "":
                        continue
                    if helpers.is_valid_ipv4_address(line):
                        controllers.append(line)
        else:
            controllers.append(args.ip)

        log.info(f"controllers: {controllers}")

        if not controllers:
            log.error("no controllers, or valid IPv4 addresses provided.")
            sys.exit(-1)

        if controllers:
            username = input("username: ")
            log.info(f"user: {username}")
            password = getpass.getpass(prompt="password: ")

            for ip_address in controllers:
                worker = Worker(
                    "aruba_os",
                    ip_address,
                    command_set,
                    decrypt,
                    username,
                    password,
                    counter,
                )
                worker.start()
                if args.syn:
                    worker.join()
                counter += 1


def build_output_file(results: list, hostname: str, ip_address: str, thread_id: int):
    """
    - naming convention: [name]-[ip]-[command]-[time].cfg
    - write to same directory
    """
    log = logging.getLogger(inspect.stack()[0][3])
    curtime = time.strftime("%Y%m%dt%H%M")
    output_filename = (
        "runcommand-" + hostname + "-" + ip_address + "-" + curtime + ".md"
    )
    log.info(f"thread {thread_id} - writing results to {output_filename}")

    out_file = open(output_filename, "w")
    for result in results:
        lines = result.splitlines()
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
