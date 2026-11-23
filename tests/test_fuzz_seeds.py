"""Replay the fuzz corpus through the fuzz target, without atheris."""

import importlib.util
from pathlib import Path

import pytest
from scapy.layers.inet import IP, TCP
from scapy.layers.inet6 import IPv6
from scapy.layers.l2 import Ether

from uanalyser.preprocessing.operations import (
    define_communication_type,
    detect_opcua_attack,
)

FUZZ_DIR = Path(__file__).resolve().parent.parent / 'fuzz'
SEEDS = sorted((FUZZ_DIR / 'corpus' / 'packets').glob('*.bin'))


def _load_fuzz_packets():
    spec = importlib.util.spec_from_file_location(
        'fuzz_packets', FUZZ_DIR / 'fuzz_packets.py'
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


fuzz_packets = _load_fuzz_packets()


def test_seed_corpus_is_present():
    assert SEEDS


@pytest.mark.parametrize('seed', SEEDS, ids=lambda p: p.name)
def test_packet_seed_does_not_raise(seed):
    fuzz_packets.fuzz_one(seed.read_bytes())


def test_truncated_frame_is_ignored():
    # Shorter than an Ethernet header: scapy raises struct.error, which the
    # target treats as uninteresting input.
    fuzz_packets.fuzz_one(b'\x0a\x10')


def test_ipv6_tcp_packet_does_not_raise():
    # Found by fuzzing: TCP without an IPv4 layer used to raise
    # IndexError: Layer [IP] not found.
    packet = Ether() / IPv6() / TCP(dport=4840)
    assert not detect_opcua_attack(packet, '10.0.0.1', ['10.0.0.2'])
    assert define_communication_type(packet, '10.0.0.1', ['10.0.0.2']) == (
        'Unknown'
    )


def test_ipv4_tcp_packet_is_still_classified():
    packet = Ether() / IP(src='10.0.0.2', dst='10.0.0.1') / TCP()
    assert (
        define_communication_type(packet, '10.0.0.1', ['10.0.0.2'])
        == 'Client to Server'
    )
