import main as main_module
import matplotlib.pyplot as plt
from cli import cli
from plot import graphics
from pytest import fixture
from scapy.layers.inet import IP, TCP
from scapy.packet import Raw
from typer import Typer
from typer.testing import CliRunner

# RFC 5737 documentation addresses: no real network is involved.
SERVER = '192.0.2.1'
CLIENT = '192.0.2.2'
ATTACKER = '192.0.2.99'


def make_packet(time, src, dst, sport=49320, dport=4840):
    packet = IP(src=src, dst=dst) / TCP(sport=sport, dport=dport) / Raw(b'x')
    packet.time = time
    return packet


class FakeCapture(list):
    """Stands in for the PacketList returned by scapy.rdpcap."""


def build_capture(*, with_late_packet=True):
    packets = [
        make_packet(100.0, CLIENT, SERVER),
        make_packet(100.4, SERVER, CLIENT),
        make_packet(101.2, CLIENT, SERVER),
        make_packet(101.5, SERVER, CLIENT),
        make_packet(102.3, ATTACKER, SERVER),
        make_packet(102.6, SERVER, ATTACKER),
        make_packet(103.4, ATTACKER, SERVER),
        make_packet(103.7, SERVER, ATTACKER),
        make_packet(104.2, CLIENT, SERVER),
    ]
    if with_late_packet:
        packets.append(make_packet(170.0, CLIENT, SERVER))  # beyond 60 s
    return FakeCapture(packets)


@fixture
def paths(tmp_path, monkeypatch):
    out = tmp_path / 'out'
    perf = tmp_path / 'perf'
    out.mkdir()
    perf.mkdir()
    monkeypatch.setattr(graphics, 'OUTPUT', str(out))
    monkeypatch.setattr(graphics, 'DATA_PERF', str(perf))
    monkeypatch.setattr(main_module, 'DATA_PERF', str(perf))
    yield out, perf
    plt.close('all')


@fixture
def fake_capture(monkeypatch):
    opened = []

    def fake_open(path):
        opened.append(path)
        return build_capture()

    monkeypatch.setattr(main_module, 'open_pcapng_file', fake_open)
    return opened


def test_main_writes_all_plots_for_a_capture(paths, fake_capture):
    out, _ = paths

    main_module.main('0-fake_flood.pcapng', SERVER, [CLIENT])

    assert fake_capture == ['0-fake_flood.pcapng']
    assert sorted(p.name for p in out.iterdir()) == [
        '0-fake_flood-pack.png',
        '0-fake_flood-rttp.png',
        '0-fake_flood-rtts.png',
        '0-fake_flood-tput.png',
    ]
    assert plt.get_fignums() == []


def test_main_plots_performance_when_csv_exists(paths, fake_capture):
    out, perf = paths
    (perf / '0-fake_flood.csv').write_text(
        'Timestamp,CPU (%),Memory (%)\n0.0,5.0,3.0\n1.0,6.0,3.5\n'
    )

    main_module.main('0-fake_flood.pcapng', SERVER, [CLIENT])

    assert (out / '0-fake_flood-perf.png').is_file()


def test_main_passes_ips_to_attack_detection(paths, monkeypatch):
    monkeypatch.setattr(
        main_module, 'open_pcapng_file', lambda path: build_capture()
    )
    seen = []
    real = main_module.detect_opcua_attack

    def spy(packet, server_ip, client_ips):
        seen.append((server_ip, client_ips))
        return real(packet, server_ip, client_ips)

    monkeypatch.setattr(main_module, 'detect_opcua_attack', spy)

    main_module.main('0-fake_flood.pcapng', SERVER, [CLIENT])

    assert seen
    assert all(call == (SERVER, [CLIENT]) for call in seen)


def test_main_records_first_attack_packet(paths, monkeypatch):
    plotted = {}

    def spy(rtts, number_of_packets, attack, filename, **kwargs):
        plotted['attack'] = dict(attack)

    monkeypatch.setattr(
        main_module, 'open_pcapng_file', lambda path: build_capture()
    )
    monkeypatch.setattr(main_module, 'plot_round_trip_time_per_packet', spy)

    main_module.main('0-fake_flood.pcapng', SERVER, [CLIENT])

    assert plotted['attack']['Packet index'] == 4
    assert plotted['attack']['Relative time'] == 2.3


def test_main_show_plots_calls_plt_show(paths, fake_capture, monkeypatch):
    shown = []
    monkeypatch.setattr(plt, 'show', lambda *a, **k: shown.append(a))

    main_module.main('0-fake_flood.pcapng', SERVER, [CLIENT], show_plots=True)

    assert shown  # the final blocking show() at the end of main


def test_process_all_pcapng_files_lists_only_captures(tmp_path, capsys):
    (tmp_path / '0-a.pcapng').write_bytes(b'')
    (tmp_path / '1-b.pcapng').write_bytes(b'')
    (tmp_path / 'notes.txt').write_text('x')

    main_module.process_all_pcapng_files(str(tmp_path))

    lines = sorted(capsys.readouterr().out.split())
    assert lines == ['0-a.pcapng', '1-b.pcapng']


def test_main_module_has_no_hardcoded_lab_addresses():
    assert not hasattr(main_module, 'SERVER_IP')
    assert not hasattr(main_module, 'CLIENTS_IPS')


def _app():
    app = Typer()
    app.command()(cli.analyse_package)
    return app


def test_cli_requires_server_and_client():
    result = CliRunner().invoke(_app(), ['x.pcapng'])

    assert result.exit_code != 0


def test_cli_passes_arguments_to_main(monkeypatch):
    calls = []
    monkeypatch.setattr(
        cli,
        'main',
        lambda *args, **kwargs: calls.append((args, kwargs)),
    )

    result = CliRunner().invoke(
        _app(),
        [
            'cap.pcapng',
            '--server',
            SERVER,
            '--client',
            CLIENT,
            '--client',
            ATTACKER,
            '--show-plots',
        ],
    )

    assert result.exit_code == 0, result.output
    assert calls == [
        (('cap.pcapng', SERVER, [CLIENT, ATTACKER]), {'show_plots': True})
    ]


def test_cli_show_plots_defaults_to_false(monkeypatch):
    calls = []
    monkeypatch.setattr(
        cli, 'main', lambda *args, **kwargs: calls.append((args, kwargs))
    )

    result = CliRunner().invoke(
        _app(), ['cap.pcapng', '--server', SERVER, '--client', CLIENT]
    )

    assert result.exit_code == 0, result.output
    assert calls == [(('cap.pcapng', SERVER, [CLIENT]), {'show_plots': False})]
