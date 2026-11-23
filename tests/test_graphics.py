import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from plot import graphics
from plot.graphics import (
    GraphUtils,
    performance_data_axle,
    plot_packets_per_second,
    plot_performance_data,
    plot_round_trip_time_per_packet,
    plot_round_trip_time_per_second,
    plot_throughput,
)
from pytest import fixture, mark, raises

ATTACK = {
    'Type': 'None',
    'Name': 'DOS ATTACK EXAMPLE',
    'Relative time': 2.5,
    'Packet index': 3,
}
SECONDS = [1, 2, 3, 4]
RTTS = [[1, 0.5, 0.2], [3, 1.5, 0.4], [5, 2.5, 0.3]]
ATTACKER_RTTS = [[7, 2.7, 0.1], [9, 3.1, 0.6]]
PERF_CSV = 'Timestamp,CPU (%),Memory (%)\n0.0,5.0,3.0\n1.0,6.5,3.5\n'


@fixture(autouse=True)
def isolated_paths(tmp_path, monkeypatch):
    """Send every plot to tmp_path and look for performance CSVs there."""
    out = tmp_path / 'out'
    perf = tmp_path / 'perf'
    out.mkdir()
    perf.mkdir()
    monkeypatch.setattr(graphics, 'OUTPUT', str(out))
    monkeypatch.setattr(graphics, 'DATA_PERF', str(perf))
    yield
    plt.close('all')


@fixture
def out_dir(tmp_path):
    return tmp_path / 'out'


@fixture
def perf_csv(tmp_path):
    path = tmp_path / 'perf' / 'cap.csv'
    path.write_text(PERF_CSV)
    return path


def test_graph_utils_can_be_instantiated():
    assert isinstance(GraphUtils(), GraphUtils)


def test_get_csv_data_reads_the_file(perf_csv):
    data = GraphUtils.get_csv_data(str(perf_csv))

    assert list(data.columns) == ['Timestamp', 'CPU (%)', 'Memory (%)']
    assert len(data) == 2


def test_get_csv_data_missing_file_raises_file_not_found(tmp_path):
    missing = str(tmp_path / 'missing.csv')

    with raises(FileNotFoundError) as error:
        GraphUtils.get_csv_data(missing)

    assert error.value.args[0] == f'No such file or directory: "{missing}".'


def test_get_csv_data_wraps_unknown_errors(tmp_path):
    empty = tmp_path / 'empty.csv'
    empty.write_text('')

    with raises(Exception, match='An error occurred'):
        GraphUtils.get_csv_data(str(empty))


def test_extract_rtt_plot_values_rejects_bad_width():
    with raises(ValueError, match='Each entry must have 2 or 3 elements'):
        GraphUtils.extract_rtt_plot_values([[1, 2, 3, 4]])


def test_extract_rtt_plot_values_rejects_empty_data():
    with raises(ValueError, match='extracting RTT plot values'):
        GraphUtils.extract_rtt_plot_values([])


def test_normalize_values_of_empty_list_is_empty():
    assert GraphUtils.normalize_values([]) == []


def test_normalize_values_constant_list_is_neutral():
    assert GraphUtils.normalize_values([3, 3, 3]) == [0.5, 0.5, 0.5]


def test_decode_attack_to_file_name_unknown_type():
    attack = {'Type': 'Other', 'Name': 'Some  Attack'}

    assert GraphUtils.decode_attack_to_file_name(attack) == (
        'unknown-some_attack'
    )


def test_performance_data_axle_without_performance_returns_axis():
    _, ax = plt.subplots()

    assert performance_data_axle(ax, 'cap', performance=False) is ax
    assert len(ax.lines) == 0


@mark.parametrize('twin', [True, False])
def test_performance_data_axle_plots_cpu_and_ram(perf_csv, twin):
    fig, ax = plt.subplots()

    result = performance_data_axle(ax, 'cap', performance=True, twin=twin)

    assert result is ax
    axes = fig.axes
    assert len(axes) == (2 if twin else 1)
    perf_ax = axes[-1]
    assert perf_ax.get_ylabel() == 'Performance (%)'
    legend = perf_ax.get_legend()
    assert legend is not None
    labels = [text.get_text() for text in legend.get_texts()]
    assert labels == ['CPU', 'RAM']


def test_performance_data_axle_missing_columns_prints_message(
    tmp_path, capsys
):
    (tmp_path / 'perf' / 'cap.csv').write_text('Timestamp,CPU (%)\n0,1\n')
    _, ax = plt.subplots()

    performance_data_axle(ax, 'cap', performance=True)

    assert 'missing required columns' in capsys.readouterr().out
    assert len(ax.lines) == 0


def test_performance_data_axle_missing_file_raises():
    _, ax = plt.subplots()

    with raises(FileNotFoundError, match='cap.csv not found'):
        performance_data_axle(ax, 'cap', performance=True)


def test_performance_data_axle_wraps_read_errors(tmp_path):
    (tmp_path / 'perf' / 'cap.csv').write_text('')
    _, ax = plt.subplots()

    with raises(Exception, match='error occurred while reading the file'):
        performance_data_axle(ax, 'cap', performance=True)


def assert_png(path):
    assert path.is_file()
    assert path.read_bytes().startswith(b'\x89PNG')


@mark.parametrize('is_twiny', [True, False])
def test_plot_performance_data_saves_png(out_dir, perf_csv, is_twiny):
    plot_performance_data(SECONDS, ATTACK, 'cap', is_twiny=is_twiny)

    assert_png(out_dir / 'cap-perf.png')


def test_plot_performance_data_without_attack_marker(out_dir, perf_csv):
    attack = {'Type': 'Sign', 'Name': 'NORMAL'}

    plot_performance_data(SECONDS, attack, 'cap', is_twiny=False)

    assert_png(out_dir / 'cap-perf.png')


def test_plot_performance_data_labels(out_dir, perf_csv, monkeypatch):
    saved = {}
    real_savefig = Figure.savefig

    def spy(self, *args, **kwargs):
        saved['ax'] = self.axes[0]
        return real_savefig(self, *args, **kwargs)

    monkeypatch.setattr(Figure, 'savefig', spy)

    plot_performance_data(SECONDS, ATTACK, 'cap', is_twiny=False)

    ax = saved['ax']
    assert ax.get_xlabel() == 'Tempo (s)'
    assert ax.get_ylabel() == 'Performance (%)'
    assert 'DOS ATTACK EXAMPLE' in ax.get_title()


def test_plot_performance_data_show_plots_keeps_figure_open(
    out_dir, perf_csv, monkeypatch
):
    shown = []
    monkeypatch.setattr(
        plt, 'show', lambda *a, **k: shown.append((a, k)), raising=True
    )

    plot_performance_data(
        SECONDS, ATTACK, 'cap', is_twiny=False, show_plots=True
    )

    assert shown == [((), {'block': False})]
    assert plt.get_fignums()


def test_plot_packets_per_second_saves_png_and_labels(out_dir):
    plot_packets_per_second([1, 2, 3, 40], SECONDS, ATTACK, 'cap')

    assert_png(out_dir / 'cap-pack.png')
    assert plt.get_fignums() == []


def test_plot_packets_per_second_show_and_no_attack_marker(
    out_dir, monkeypatch
):
    monkeypatch.setattr(plt, 'show', lambda *a, **k: None)
    attack = {'Type': 'None', 'Name': 'NORMAL'}

    plot_packets_per_second([1, 2], [1, 2], attack, 'cap', show_plots=True)

    assert_png(out_dir / 'cap-pack.png')
    ax = plt.gcf().axes[0]
    assert ax.get_xlabel() == 'Tempo (s)'
    assert ax.get_ylabel() == 'Pacotes OPC UA'
    assert len(ax.patches) == 2
    assert len(ax.lines) == 0


def test_plot_packets_per_second_with_performance_overlay(out_dir, perf_csv):
    plot_packets_per_second(
        [1, 2, 3, 4], SECONDS, ATTACK, 'cap', performance=True
    )

    assert_png(out_dir / 'cap-pack.png')


def test_plot_throughput_saves_png(out_dir):
    plot_throughput([0.1, 0.2, 0.3, 13.0], SECONDS, ATTACK, 'cap')

    assert_png(out_dir / 'cap-tput.png')


def test_plot_throughput_labels_and_data(out_dir, monkeypatch):
    monkeypatch.setattr(plt, 'show', lambda *a, **k: None)
    attack = {'Type': 'Sign', 'Name': 'NORMAL'}

    plot_throughput([1, 2, 3, 4], SECONDS, attack, 'cap', show_plots=True)

    ax = plt.gcf().axes[0]
    assert ax.get_ylabel() == 'Throughput (KBps)'
    assert np.asarray(ax.lines[0].get_ydata()).tolist() == [1, 2, 3, 4]
    assert len(ax.lines) == 1  # no attack marker without 'Relative time'


def test_plot_throughput_with_performance_overlay(out_dir, perf_csv):
    plot_throughput([1, 2, 3, 4], SECONDS, ATTACK, 'cap', performance=True)

    assert_png(out_dir / 'cap-tput.png')


def test_plot_rtt_per_packet_with_attacker(out_dir):
    plot_round_trip_time_per_packet(
        RTTS, 12, ATTACK, 'cap', attacker_rtts=ATTACKER_RTTS
    )

    assert_png(out_dir / 'cap-rttp.png')


def test_plot_rtt_per_packet_axes(out_dir, monkeypatch):
    monkeypatch.setattr(plt, 'show', lambda *a, **k: None)

    plot_round_trip_time_per_packet(
        RTTS,
        12,
        ATTACK,
        'cap',
        attacker_rtts=ATTACKER_RTTS,
        show_plots=True,
    )

    ax = plt.gcf().axes[0]
    assert ax.get_xlabel() == 'Pacote'
    assert ax.get_ylabel() == 'Round Trip Time'
    assert ax.get_yscale() == 'log'
    assert ax.get_xlim() == (0, 11)
    assert len(ax.collections) == 2
    assert ax.yaxis.get_major_formatter()(0.5, 0) == '0.500'


def test_plot_rtt_per_packet_without_attacker_or_marker(out_dir):
    attack = {'Type': 'None', 'Name': 'NORMAL'}

    plot_round_trip_time_per_packet(RTTS, 12, attack, 'cap')

    assert_png(out_dir / 'cap-rttp.png')


def test_plot_rtt_per_second_with_attacker(out_dir, monkeypatch):
    monkeypatch.setattr(plt, 'show', lambda *a, **k: None)

    plot_round_trip_time_per_second(
        RTTS,
        SECONDS,
        ATTACK,
        'cap',
        attacker_rtts=ATTACKER_RTTS,
        show_plots=True,
    )

    assert_png(out_dir / 'cap-rtts.png')
    ax = plt.gcf().axes[0]
    assert ax.get_xlabel() == 'Tempo (s)'
    assert ax.get_xlim() == (0, len(SECONDS) + 2)
    assert len(ax.collections) == 2
    assert ax.yaxis.get_major_formatter()(2.0, 0) == '2.000'


def test_plot_rtt_per_second_groups_by_second(out_dir, monkeypatch):
    monkeypatch.setattr(plt, 'show', lambda *a, **k: None)
    rtts = [[1, 0.1, 1.0], [2, 0.9, 3.0], [3, 2.2, 5.0]]
    attack = {'Type': 'None', 'Name': 'NORMAL'}

    plot_round_trip_time_per_second(rtts, SECONDS, attack, 'cap')

    assert_png(out_dir / 'cap-rtts.png')


def test_every_plot_closes_its_figure_unless_shown(out_dir):
    plot_packets_per_second([1], [1], ATTACK, 'a')
    plot_throughput([1], [1], ATTACK, 'b')
    plot_round_trip_time_per_packet(RTTS, 12, ATTACK, 'c')
    plot_round_trip_time_per_second(RTTS, SECONDS, ATTACK, 'd')

    assert plt.get_fignums() == []
    assert sorted(p.name for p in out_dir.iterdir()) == [
        'a-pack.png',
        'b-tput.png',
        'c-rttp.png',
        'd-rtts.png',
    ]
