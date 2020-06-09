#!/usr/bin/env python3

# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# A copy of the License is located at
#     http://www.apache.org/licenses/LICENSE-2.0
# or in the "license" file accompanying this file. This file is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.

"""
Remote server monitoring script
"""
# pylint: disable=redefined-builtin

import logging
import sys
from gevent import socket
from gevent import select
from gevent import monkey
import argparse
import tempfile

monkey.patch_select()
monkey.patch_socket()

logger = logging.getLogger(__name__)
from metrics_collector import start_metric_collection, stop_process, store_pid, check_is_running
from process import find_procs_by_name, get_process_pid_from_file, \
    get_child_processes, get_server_processes, get_server_pidfile
import configuration

TMP_DIR = tempfile.gettempdir()
METRICS_MON_SERVER_PID_FILE = "{}/.metrics_monitoring_server.pid".format(TMP_DIR)

HOST = str(configuration.get('monitoring','HOST'))
PORT = int(configuration.get('monitoring','PORT', 9009))


SOCKET_LIST = []
RECV_BUFFER = 4096

interval = 1


def perf_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(10)
    SOCKET_LIST.append(server_socket)
    logger.info("Started metrics monitoring server on port {}".format(PORT))

    while True:
        ready_to_read, ready_to_write, in_error = select.select(SOCKET_LIST, [], [], 0)

        for sock in ready_to_read:
            # a new connection request recieved
            if sock == server_socket:
                sockfd, addr = server_socket.accept()
                SOCKET_LIST.append(sockfd)
                logger.info("client ({}, {}) connected".format(addr[0], addr[1]))

            # a message from a client, not a new connection
            else:
                try:
                    # receiving data from the socket.
                    data = sock.recv(RECV_BUFFER).decode()
                    if data:
                        if data == 'test\n':
                            send_message(sock, "Yep\n")
                        elif data == 'exit\n':
                            close_socket(sock)
                        elif data.startswith('interval'):
                            try:
                                 global interval
                                 interval = int(data.split(":")[1][:-1])
                            except Exception:
                                send_message(sock, "In-correct interval data")
                        elif data.startswith('metrics'):
                             metrics = data[:-1].split("metrics:")[1].split("\t")
                             server_pid = get_process_pid_from_file(get_server_pidfile())
                             server_process = get_server_processes(server_pid)
                             start_metric_collection(server_process, metrics, interval, sock)
                        else:
                            # TODO - decide what to do here
                            pass

                    else:
                        # remove the socket that's broken
                        if sock in SOCKET_LIST:
                            SOCKET_LIST.remove(sock)
                except Exception as e:
                    logger.warning("Error {}".format(str(e)))
                    continue

    server_socket.close()


def send_message(socket, message):
    try:
        socket.send(message.encode("latin-1"))
    except Exception as e:
        logger.warning("Error while sending the message {}. Closing the socket.".format(str(e)))
        close_socket(socket)


def close_socket(socket):
    socket.close()
    if socket in SOCKET_LIST:
        SOCKET_LIST.remove(socket)


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, format="%(message)s", level=logging.INFO)
    parser = argparse.ArgumentParser(prog='perf-mon-script', description='System Performance Monitoring')
    sub_parse = parser.add_mutually_exclusive_group(required=True)
    sub_parse.add_argument('--start', action='store_true', help='Start the perf-mon-script')
    sub_parse.add_argument('--stop', action='store_true', help='Stop the perf-mon-script')

    args = parser.parse_args()

    if args.start:
        check_is_running(METRICS_MON_SERVER_PID_FILE)
        store_pid(METRICS_MON_SERVER_PID_FILE)
        perf_server()
    elif args.stop:
        stop_process(METRICS_MON_SERVER_PID_FILE)




