"""Atheris harness for the packet parsing and classification path.

Raw bytes are dissected by scapy as an Ethernet frame (the link type of the
captures this project reads) and then fed to the three packet helpers that
read transport and IP layers: ``is_opcua_packet``, ``detect_opcua_attack``
and ``define_communication_type``. None of them document an exception for
well-formed or malformed frames, so any exception is a finding.

atheris is not a project dependency. Run from the repository root with:

    uv run --with atheris python fuzz/fuzz_packets.py -runs=100000 \
        fuzz/corpus/packets
"""

import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

PORTS = [4840]
SERVER_IP = '192.168.164.101'
CLIENTS_IP = ['192.168.164.102']


def fuzz_one(data: bytes) -> None:
    """Dissect `data` as an Ethernet frame and classify it."""
    # Imported here so that main() can import them under atheris
    # instrumentation, and so the pytest seed replay needs no atheris.
    from scapy.layers.l2 import Ether

    from uanalyser.preprocessing.operations import (
        define_communication_type,
        detect_opcua_attack,
        is_opcua_packet,
    )

    try:
        packet = Ether(data)
    except struct.error:
        # scapy raises struct.error for frames shorter than an Ethernet
        # header. That is scapy's behaviour on truncated input, not project
        # code, and pcap readers never yield such frames.
        return
    is_opcua_packet(packet, PORTS)
    detect_opcua_attack(packet, SERVER_IP, CLIENTS_IP)
    define_communication_type(packet, SERVER_IP, CLIENTS_IP)


def main() -> None:
    import atheris

    with atheris.instrument_imports():
        import scapy.layers.l2  # noqa: F401

        import uanalyser.preprocessing.operations  # noqa: F401

    atheris.Setup(sys.argv, fuzz_one)
    atheris.Fuzz()


if __name__ == '__main__':
    main()
