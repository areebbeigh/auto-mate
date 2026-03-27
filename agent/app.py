#!/usr/bin/env python3

import logging
import argparse
import threading

from agent.config import settings
from common.service.mqtt import get_mqtt_service_ctx
from agent.factory import AGENT_CLASSES

logger = logging.getLogger(__name__)

def _start_agent(klass):
    with get_mqtt_service_ctx() as mqtt:
        agent = klass(name=klass.__name__, mqtt_service=mqtt)
        agent.start()
        agent.loop_forever()

def start_agents(args):
    print("Starting edge agents...")
    threads = []
    for klass in AGENT_CLASSES:
        t = threading.Thread(target=_start_agent, args=[klass])
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

def list_agents(args):
    print("Listing running agents...")
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