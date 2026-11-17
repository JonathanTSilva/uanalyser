<!-- brand:header:start -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/brand/header-da37f6b9-dark.svg">
  <img alt="uanalyser: Traffic analyser for intrusion detection in OPC UA networks" src="assets/brand/header-da37f6b9-light.svg" width="100%">
</picture>
<!-- brand:header:end -->

<!-- badges:start -->
[![Status](https://img.shields.io/badge/status-inactive-silver?style=flat-square)](https://www.repostatus.org/#inactive)
[![CI](https://img.shields.io/github/actions/workflow/status/JonathanTSilva/uanalyser/ci.yml?branch=main&style=flat-square&label=ci)](https://github.com/JonathanTSilva/uanalyser/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/JonathanTSilva/uanalyser/graph/badge.svg)](https://codecov.io/gh/JonathanTSilva/uanalyser)
[![Quality](https://sonarcloud.io/api/project_badges/measure?project=JonathanTSilva_uanalyser&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=JonathanTSilva_uanalyser)
[![Scorecard](https://img.shields.io/ossf-scorecard/github.com/JonathanTSilva/uanalyser?style=flat-square&label=scorecard)](https://scorecard.dev/viewer/?uri=github.com/JonathanTSilva/uanalyser)
[![License](https://img.shields.io/badge/license-MIT-blue?style=flat-square)](LICENSE)
[![Codespaces](https://img.shields.io/badge/codespaces-open-181717?style=flat-square&logo=github)](https://codespaces.new/JonathanTSilva/uanalyser)
<!-- badges:end -->

**See the attack start in the traffic.** uanalyser reads a PCAPNG capture of OPC UA traffic, finds the packet where an attack begins and plots what the network did before and after it.

<p align="center">
  <img src="uanalyser/output/0-dos_hping3-tput.png" alt="Throughput of an OPC UA link jumping from near zero to about 3000 KBps when a DoS flood starts at 41 seconds" width="49%">
  <img src="uanalyser/output/0-dos_hping3-pack.png" alt="OPC UA packets per second jumping to about 30000 when the same flood starts" width="49%">
</p>

*Throughput (left) and OPC UA packets per second (right) over one minute of a `hping3` DoS flood. The dashed red line marks the detected start. Plot labels are in Portuguese, the language of the original research.*

## What it is

A research tool built for an MSc project on intrusion detection in OPC UA networks, the protocol that industrial plants use to move machine data. Given a capture of the traffic between a server and a client, it:

- **Finds the attack.** It flags the packet where a denial-of-service attack starts.
- **Measures the link.** It computes throughput, OPC UA packets per second and round-trip times for the client and for the attacker.
- **Adds machine load.** When CPU and memory data were recorded during the capture, it plots that next to the traffic.
- **Draws every result as a PNG**, one file per metric.

The test set covers five DoS attacks, two man-in-the-middle attacks (ARP spoofing and port mirroring) and a normal-traffic baseline, each captured in the three OPC UA security modes: None, Sign and Sign & Encrypt. The project is finished and no longer maintained, and it stays public as a record of the work.

## Quick start

```sh
git clone https://github.com/JonathanTSilva/uanalyser.git
cd uanalyser
uv sync
uv run pytest
```

Or open it in a dev container or GitHub Codespaces.

## Usage

The code is a set of scripts run from the checkout, not an installable package. Analyse one capture with `main`, which writes the plots to `uanalyser/output/`:

```sh
PYTHONPATH=uanalyser uv run python -c "from main import main; main('tests/assets/0-dos_attack_example.pcapng')"
```

Capture file names follow `<type>-<attack name>.pcapng`, where the type is the OPC UA security mode: `0` for None, `1` for Sign and `2` for Sign & Encrypt. Pass `show_plots=True` to open the plots instead of only saving them. The full capture set and the performance CSV files used in the research are not in this repository: `uanalyser/paths.py` expects them under `Data/`.

## Docs

The [capture guide](docs/captures.md) lists every test capture with its hosts and the packet where the attack starts. The API reference is a MkDocs site generated from the docstrings, with the entry page in [`docs/index.md`](docs/index.md). Build it locally with `uv sync --group docs` and `uv run mkdocs serve`. The conventions this repository follows are in the [handbook](https://github.com/JonathanTSilva/.github/blob/main/handbook/README.md).

## Contributing

See the [contributing guide](https://github.com/JonathanTSilva/.github/blob/main/CONTRIBUTING.md). Branches are named `<type>/<issue>-<slug>`, commits and PR titles follow Conventional Commits, and PRs are squash-merged. The project is inactive, so changes are unlikely to be reviewed quickly.

## License

MIT. See [LICENSE](LICENSE).

Author: [Jonathan T. da Silva](https://github.com/JonathanTSilva).

<!-- brand:footer:start -->
<p align="right"><a href="https://www.jontobias.com"><picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/JonathanTSilva/.github/main/assets/brand/jontobias-dark.svg">
  <img alt="jontobias.com" src="https://raw.githubusercontent.com/JonathanTSilva/.github/main/assets/brand/jontobias-light.svg" width="200">
</picture></a></p>
<!-- brand:footer:end -->
