from scapy.layers.inet import ICMP, IP, TCP, UDP

from uanalyser.preprocessing.operations import is_opcua_packet

PORTS = [4840]


def test_tcp_destination_port_matches():
    assert is_opcua_packet(IP() / TCP(sport=50000, dport=4840), PORTS)


def test_tcp_source_port_matches():
    assert is_opcua_packet(IP() / TCP(sport=4840, dport=50000), PORTS)


def test_udp_port_matches():
    assert is_opcua_packet(IP() / UDP(sport=50000, dport=4840), PORTS)


def test_other_ports_do_not_match():
    assert not is_opcua_packet(IP() / TCP(sport=50000, dport=80), PORTS)


def test_ip_packet_without_transport_layer_does_not_raise():
    # IP has no dport/sport fields; this used to raise AttributeError.
    assert not is_opcua_packet(IP() / ICMP(), PORTS)
