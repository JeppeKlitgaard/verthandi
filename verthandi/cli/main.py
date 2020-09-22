"""
The main CLI entry point.
"""

import datetime as dt

import typer
from dateutil.parser import parse as dt_parse
from rich.console import Console
from rich.table import Table

from verthandi.clockify.client import ClockifyClient
from verthandi.config import settings

app = typer.Typer()
console = Console()
client = ClockifyClient(api_key=settings.API_KEY, base_url=settings.BASE_URL)


def get_timedelta(dts_1: str) -> str:
    """
    Returns the timedelta in a hh:mm:ss format.

    Args:
        dts_1 (str): ISO-like datetime string.

    Returns:
        str: The timedelta between dts_1 and now.
    """
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0)
    dt_1 = dt_parse(dts_1)

    timedelta = now - dt_1

    return str(timedelta)


@app.command(name="list")
def list_() -> None:
    time_entries = client.list_timeentry(params={"in-progress": True})

    t = Table(show_header=True)
    t.add_column("Description")
    t.add_column("Start :clock1:")
    t.add_column("\N{GREEK CAPITAL LETTER DELTA}t")

    for entry in time_entries:
        t.add_row(
            entry["description"],
            entry["timeInterval"]["start"],
            get_timedelta(entry["timeInterval"]["start"]),
        )

    console.print(t)


@app.command()
def start(description: str) -> None:
    body = {
        "description": description,
        "start": dt.datetime.now(dt.timezone.utc),
    }
    client.start_timeentry(body=body)


@app.command()
def finish() -> None:
    body = {
        "end": dt.datetime.now(dt.timezone.utc),
    }

    print(client.stop_timeentry(body=body))


@app.command()
def config() -> None:
    """
    Prints the configuration.
    """
    typer.echo(settings.to_str())


if __name__ == "__main__":
    app()
