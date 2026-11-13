<!-- brand:header:start -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/brand/header-2f13d5d7-dark.svg">
  <img alt="uanalyser: Traffic analyser for intrusion detection in OPC UA networks" src="assets/brand/header-2f13d5d7-light.svg" width="100%">
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

## What it is

A research tool built for an MSc project on intrusion detection in OPC UA networks. It reads PCAPNG captures of OPC UA traffic between a server and a client, finds the packet where an attack starts, and computes throughput, OPC UA packets per second and round-trip times, optionally next to CPU and memory data recorded during the capture. It plots each result as a PNG. The project is finished and no longer maintained.

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

### Test captures

Guide to the capture files used while developing the tool. Each row is one capture, named `<type>-<file name>.pcapng`. The Attack column gives the packet number and time (seconds) where the attack is detected.

| Type | File name | Size | Server (IP / MAC) | Client (IP / MAC) | Attacker (IP / MAC) | Sniffer (IP / MAC) | Attack |
|---|---|---|---|---|---|---|---|
| 0 | dos_certificate_inf_chain_loop | 7997 | 192.168.164.101 / e4:5f:01:2e:1a:b6 | 192.168.164.102 / e4:5f:01:2e:1b:c1 | 192.168.164.103 / 00:09:5b:bd:64:06 | 192.168.164.115 / ac:1a:3d:a8:67:cd | packet 1967, time 32.3419 |
| 0 | dos_function_call_null_deref | 8805 | 192.168.164.101 / e4:5f:01:2e:1a:b6 | 192.168.164.102 / e4:5f:01:2e:1b:c1 | 192.168.164.103 / 00:09:5b:bd:64:06 | 192.168.164.115 / ac:1a:3d:a8:67:cd | packet 2275, time 31.7939 |
| 0 | dos_hping3 | 3521545 | 192.168.164.101 / e4:5f:01:2e:1a:b6 | 192.168.164.102 / e4:5f:01:2e:1b:c1 | 192.168.164.201 / 00:09:5b:bd:64:06 | 192.168.164.115 / ac:1a:3d:a8:67:cd | packet 4294, time 41.1575 |
| 0 | dos_open_multiple_secure_channels | 21200 | 192.168.164.101 / e4:5f:01:2e:1a:b6 | 192.168.164.102 / e4:5f:01:2e:1b:c1 | 192.168.164.103 / 00:09:5b:bd:64:06 | 192.168.164.115 / ac:1a:3d:a8:67:cd | packet 2224, time 32.9595 |
| 0 | dos_translate_browse_path_call_stack_overflow | 8759 | 192.168.164.101 / e4:5f:01:2e:1a:b6 | 192.168.164.102 / e4:5f:01:2e:1b:c1 | 192.168.164.103 / 00:09:5b:bd:64:06 | 192.168.164.115 / ac:1a:3d:a8:67:cd | packet 2366, time 31.7897 |
| 0 | mitm_arp | 6059 | 192.168.164.101 / e4:5f:01:2e:1a:b6 | 192.168.164.102 / e4:5f:01:2e:1b:c1 | - / 00:09:5b:bd:64:06 | 192.168.164.110 / 00:be:43:34:b8:54 | - |
| 0 | mitm_port | 619200 | 192.168.164.101 / e4:5f:01:2e:1a:b6 | 192.168.164.102 / e4:5f:01:2e:1b:c1 | - / 00:09:5b:bd:64:06 | 192.168.164.110 / 00:be:43:34:b8:54 | - |
| 0 | normal_local_server | 6129 | 192.168.164.101 / e4:5f:01:2e:1a:b6 | 192.168.164.102 / e4:5f:01:2e:1b:c1 | - | 192.168.164.110 / 00:be:43:34:b8:54 | - |
| 1 | dos_certificate_inf_chain_loop | 8811 | 192.168.164.101 / e4:5f:01:2e:1a:b6 | 192.168.164.102 / e4:5f:01:2e:1b:c1 | 192.168.164.103 / 00:09:5b:bd:64:06 | 192.168.164.115 / ac:1a:3d:a8:67:cd | packet 3470, time 32.2758 |
| 1 | dos_function_call_null_deref | 52709 | 192.168.164.101 / e4:5f:01:2e:1a:b6 | 192.168.164.102 / e4:5f:01:2e:1b:c1 | 192.168.164.103 / 00:09:5b:bd:64:06 | 192.168.164.115 / ac:1a:3d:a8:67:cd | packet 2814, time 30.9477 |
| 1 | dos_hping3 | 2065664 | 192.168.164.101 / e4:5f:01:2e:1a:b6 | 192.168.164.102 / e4:5f:01:2e:1b:c1 | 192.168.164.201 / 00:09:5b:bd:64:06 | 192.168.164.115 / ac:1a:3d:a8:67:cd | packet 4275, time 45.8889 |
| 1 | dos_open_multiple_secure_channels | 22739 | 192.168.164.101 / e4:5f:01:2e:1a:b6 | 192.168.164.102 / e4:5f:01:2e:1b:c1 | 192.168.164.103 / 00:09:5b:bd:64:06 | 192.168.164.115 / ac:1a:3d:a8:67:cd | packet 3540, time 31.8013 |
| 1 | dos_translate_browse_path_call_stack_overflow | 9362 | 192.168.164.101 / e4:5f:01:2e:1a:b6 | 192.168.164.102 / e4:5f:01:2e:1b:c1 | 192.168.164.103 / 00:09:5b:bd:64:06 | 192.168.164.115 / ac:1a:3d:a8:67:cd | packet 3397, time 31.7899 |
| 1 | mitm_arp | 7650 | 192.168.164.101 / e4:5f:01:2e:1a:b6 | 192.168.164.102 / e4:5f:01:2e:1b:c1 | - / 00:09:5b:bd:64:06 | 192.168.164.110 / 00:be:43:34:b8:54 | - |
| 1 | mitm_port | 601152 | 192.168.164.101 / e4:5f:01:2e:1a:b6 | 192.168.164.102 / e4:5f:01:2e:1b:c1 | 00:09:5b:bd:64:06 | 192.168.164.110 / 00:be:43:34:b8:54 | - |
| 1 | normal_local_server | 13861 | 192.168.164.101 / e4:5f:01:2e:1a:b6 | 192.168.164.102 / e4:5f:01:2e:1b:c1 | - | 192.168.164.110 / 00:be:43:34:b8:54 | - |
| 2 | dos_certificate_inf_chain_loop | 8686 | 192.168.164.101 / e4:5f:01:2e:1a:b6 | 192.168.164.102 / e4:5f:01:2e:1b:c1 | 192.168.164.103 / 00:09:5b:bd:64:06 | 192.168.164.115 / ac:1a:3d:a8:67:cd | packet 3225, time 32.3843 |
| 2 | dos_function_call_null_deref | 53351 | 192.168.164.101 / e4:5f:01:2e:1a:b6 | 192.168.164.102 / e4:5f:01:2e:1b:c1 | 192.168.164.103 / 00:09:5b:bd:64:06 | 192.168.164.115 / ac:1a:3d:a8:67:cd | packet 3338, time 31.6231 |
| 2 | dos_hping3 | 2203825 | 192.168.164.101 / e4:5f:01:2e:1a:b6 | 192.168.164.102 / e4:5f:01:2e:1b:c1 | 192.168.164.201 / 00:09:5b:bd:64:06 | 192.168.164.115 / ac:1a:3d:a8:67:cd | packet 5566, time 44.9302 |
| 2 | dos_open_multiple_secure_channels | 21213 | 192.168.164.101 / e4:5f:01:2e:1a:b6 | 192.168.164.102 / e4:5f:01:2e:1b:c1 | 192.168.164.103 / 00:09:5b:bd:64:06 | 192.168.164.115 / ac:1a:3d:a8:67:cd | packet 3292, time 31.7924 |
| 2 | dos_translate_browse_path_call_stack_overflow | 9437 | 192.168.164.101 / e4:5f:01:2e:1a:b6 | 192.168.164.102 / e4:5f:01:2e:1b:c1 | 192.168.164.103 / 00:09:5b:bd:64:06 | 192.168.164.115 / ac:1a:3d:a8:67:cd | packet 3464, time 31.1787 |
| 2 | mitm_arp | 6407 | 192.168.164.101 / e4:5f:01:2e:1a:b6 | 192.168.164.102 / e4:5f:01:2e:1b:c1 | - / 00:09:5b:bd:64:06 | 192.168.164.110 / 00:be:43:34:b8:54 | - |
| 2 | mitm_port | 600451 | 192.168.164.101 / e4:5f:01:2e:1a:b6 | 192.168.164.102 / e4:5f:01:2e:1b:c1 | - / 00:09:5b:bd:64:06 | 192.168.164.110 / 00:be:43:34:b8:54 | - |
| 2 | normal_local_server | 33034 | 192.168.164.101 / e4:5f:01:2e:1a:b6 | 192.168.164.102 / e4:5f:01:2e:1b:c1 | - | 192.168.164.110 / 00:be:43:34:b8:54 | - |

## Docs

The API reference is a MkDocs site generated from the docstrings, with the entry page in [`docs/index.md`](docs/index.md). Build it locally with `uv sync --group docs` and `uv run mkdocs serve`. The conventions this repository follows are in the [handbook](https://github.com/JonathanTSilva/.github/blob/main/handbook/README.md).

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
