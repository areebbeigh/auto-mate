#!/usr/bin/env python3

import logging
import sys
import time
import argparse
import threading

from agent.config import settings
from common.service.mqtt import get_mqtt_service_ctx
from agent.factory import AGENT_CLASSES

logger = logging.getLogger(__name__)
stop_event = threading.Event()

def _loop():
    while not stop_event.is_set():
        time.sleep(1)

def _start_agent(klass):
    try:
        with get_mqtt_service_ctx(klass.__name__) as mqtt:
            agent = klass(name=klass.__name__, mqtt_service=mqtt)
            agent.start()
            _loop()
    finally:
        logger.info(f"Stopping agent {klass.__name__}")

def start_agents(args):
    logger.info("Starting edge agents...")
    threads = []
    for klass in AGENT_CLASSES:
        t = threading.Thread(name=f"{klass.__name__}Thread", target=_start_agent, args=[klass])
        t.start()
        threads.append(t)

    for t in threads:
        try:
            t.join()
        except KeyboardInterrupt:
            logger.info(f"Received KeyboardInterrupt")
            stop_event.set()

def list_agents(args):
    logger.info(f"Listing running agents...")
    # TODO: your listing logic


def main():
    parser = argparse.ArgumentParser(prog="app.py", description="Auto-Mate CLI")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # ---- agents ----
    agents_parser = subparsers.add_parser("agents", help="Manage edge agents")
    agents_subparsers = agents_parser.add_subparsers(dest="agents_command", required=True)

    # agents start
    start_parser = agents_subparsers.add_parser("start", help="Start edge agents")
    start_parser.set_defaults(func=start_agents)

    # agents list
    list_parser = agents_subparsers.add_parser("list", help="List running agents")
    list_parser.set_defaults(func=list_agents)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()