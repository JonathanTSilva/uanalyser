from rich import print
from rich.console import Console
from typer import run

from uanalyser.preprocessing.file_handling import extract_attack_name

console = Console()


def analyse_package():
    print(extract_attack_name('path/0-normal_traffic.pcapng'))


if __name__ == '__main__':
    run(analyse_package)
