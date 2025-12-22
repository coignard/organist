#!/usr/bin/env python3

import sys

from app import OrganistApp
from config import ORGANTEQ_URL
from midi_utils import select_midi_port
from models import StopRegistry
from organteq_client import OrganteqClient


def main() -> None:
    client = OrganteqClient(ORGANTEQ_URL)
    registry = StopRegistry()

    if not client.load_stops_into_registry(registry):
        print("Failed to connect to Organteq")
        print(
            f"Make sure Organteq is running and JSON-RPC is enabled at {ORGANTEQ_URL}"
        )
        sys.exit(1)

    midi_port = select_midi_port()
    if not midi_port:
        print("No valid MIDI port selected")
        sys.exit(1)

    app = OrganistApp(midi_port, client, registry)
    app.run()


if __name__ == "__main__":
    main()
