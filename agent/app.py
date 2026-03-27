#!/usr/bin/env python3

import logging
import argparse

from agent.config import settings
from common.service.mqtt import get_mqtt_service_ctx
from agent.factory import get_agents

logger = logging.getLogger(__name__)

def start_agents(args):
    print("Starting edge agents...")
    with get_mqtt_service_ctx() as mqtt:
        agents = get_agents(mqtt)
        for agent in agents:
            agent.start()
        agents[0].loop_forever()


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