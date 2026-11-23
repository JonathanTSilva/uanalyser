from typing import Annotated

from main import main
from typer import Argument, Option, run


def analyse_package(
    pcapng_file: Annotated[str, Argument(help='PCAPNG capture to analyse.')],
    server: Annotated[str, Option(help='IP address of the OPC UA server.')],
    client: Annotated[
        list[str],
        Option(help='IP address of a legitimate client. Repeat for several.'),
    ],
    show_plots: Annotated[
        bool, Option(help='Open the plots instead of only saving them.')
    ] = False,
) -> None:
    """Analyse a capture and write the plots to `uanalyser/output/`."""
    main(pcapng_file, server, client, show_plots=show_plots)


if __name__ == '__main__':  # pragma: no cover
    run(analyse_package)
