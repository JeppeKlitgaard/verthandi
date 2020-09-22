"""Tasks to be run using the invoke tool.

This is meant to make it easier for other people/interns
to develop the ProAPIClient and get a quick overview
of the commands to use."""

# pylint: disable=redefined-builtin,redefined-outer-name

import os
from pathlib import Path

from invoke import task
from invoke.exceptions import Exit

from rich import box, print
from rich.align import Align
from rich.console import Console
from rich.table import Table

ROOT_DIR = os.path.dirname(__file__)
ROOT_PATH = Path(ROOT_DIR)

APP_NAME = "verthandi"
APP_PATH = ROOT_PATH / APP_NAME
APP_DIR = APP_PATH.as_posix()

con = Console()


def _code_to_stat(exit_code: int, underline=False, emoji=True) -> str:
    r = "PASS" if exit_code == 0 else "FAIL"

    r = f"[green]{r}[/green]" if exit_code == 0 else f"[red]{r}[/red]"

    r = f"[underline]{r}[/underline]" if underline else r

    if emoji:
        r = r + " :sunglasses:" if exit_code == 0 else r + " :cold_sweat:"

    return r


@task
def list(c):
    """Lists the available tasks."""
    c.run("inv --list")


@task
def help(c, task):
    """Prints help information for task."""
    c.run(f"inv --help {task}")


@task(
    help={
        "coverage": "Whether to run the code coverage analysis.",
    }
)
def test(c, coverage=True, verbose=True):
    """Runs the test suite."""
    args = []

    if coverage:
        args.append(f"--cov={APP_NAME}")
        args.append("--cov-report=term-missing")

    if verbose:
        args.append("-v")

    with c.cd(APP_DIR):
        return c.run(f"pytest {' '.join(args)} .", pty=True, warn=True)


@task
def coverage(c):
    """Reports the coverage from the last test run."""
    with c.cd(APP_DIR):
        return c.run("coverage report --fail-under=100", pty=True, warn=True)


@task
def lint(c):
    """Runs pylint on the code."""
    with c.cd(ROOT_DIR):
        return c.run(f"pylint {APP_DIR}", pty=True, warn=True)


@task
def fixmes(c):
    """Lists the fixmes and TODOs of the project."""
    with c.cd(APP_PATH.as_posix()):
        return c.run(
            f"pylint {FOLDERS} --disable=all --enable=fixme",
            pty=True,
            warn=True,
        )


@task
def mypy(c):
    """Runs mypy type checking on the code."""
    with c.cd(ROOT_DIR):
        return c.run(f"mypy --config-file .mypy.ini {APP_DIR}", pty=True, warn=True)


@task(help={"check": "Whether to just check the code or format it."})
def black(c, check=False, diff=False):
    """
    Applies black formatter to the code.
    """
    args = []

    if check:
        args.append("--check")

    if diff:
        args.append("--diff")

    with c.cd(APP_PATH.as_posix()):
        return c.run(f"black {' '.join(args)} .", pty=True, warn=True)


@task(help={"check": "Whether to just check the code or format it."})
def isort(c, check=False, diff=False):
    """
    Applies black formatter to the code.
    """
    args = []

    if check:
        args.append("--check-only")

    if diff:
        args.append("--diff")

    with c.cd(APP_DIR):
        return c.run(f"isort {' '.join(args)} {APP_DIR}", pty=True, warn=True)


@task(help={"check": "Whether to just check the code or format it."})
def format(c, check=False, diff=False):
    """Formats the code."""

    black_ = black(c, check=check, diff=diff).exited
    isort_ = isort(c, check=check, diff=diff).exited

    return black_ + isort_


@task
def check(
    c,
    lint_=True,
    fixmes_=False,
    test_=True,
    coverage_=True,
    mypy_=True,
    black_=True,
    isort_=True,
    docs_=True,
    clean_=True,
):
    """Runs all checkers on the code."""
    results = {}

    if lint_:
        print("-" * 20)
        print("Running pylint...")
        print("-" * 20)
        results["lint"] = lint(c).exited

    if fixmes_:
        print("-" * 20)
        print("Running pylint (fixmes)...")
        print("-" * 20)
        results["FIXME's"] = fixmes(c).exited

    if test_:
        print("-" * 20)
        print("Running tests...")
        print("-" * 20)
        results["test"] = test(c, verbose=False).exited

    if coverage_:
        print("-" * 20)
        print("Reporting test coverage...")
        print("-" * 20)
        results["coverage"] = coverage(c).exited

    if mypy_:
        print("-" * 20)
        print("Running mypy...")
        print("-" * 20)
        results["mypy"] = mypy(c).exited

    if black_:
        print("-" * 20)
        print("Running black (formatting, just checking)...")
        print("-" * 20)
        results["black"] = black(c, check=True).exited

    if isort_:
        print("-" * 20)
        print("Running isort (formatting, just checking)...")
        print("-" * 20)
        results["isort"] = isort(c, check=True).exited

    if docs_:
        print("-" * 20)
        print("Running mkdocs...")
        print("-" * 20)
        results["docs"] = docs(c, build=True, verbose=False).exited

    result = 1 if any(results.values()) else 0

    t = Table(
        title="Report",
        title_style="bold white",
        show_header=True,
        header_style="bold white",
        show_footer=True,
        footer_style="bold white",
        show_lines=True,
        box=box.ROUNDED,
    )
    t.add_column("Task", "Summary")
    t.add_column("Result", f"[bold]{ _code_to_stat(result, underline=True) }[/bold]")

    for k, v in results.items():
        t.add_row(k, _code_to_stat(v))

    print("\n")
    con.print(Align(t, "center"))

    if result == 0:
        exit_msg = (
            "Congratulations :sparkles::fireworks::sparkles: "
            + "You may commit! :heavy_check_mark:"
        )

    else:
        exit_msg = (
            "Great code dude :+1:, but it could use some final touches. "
            + "Don't commit just yet! :x:"
        )

    print(Align(f"[underline bold]{exit_msg}[/underline bold]", "center"))
    print("\n")

    if clean_:
        clean(c, silent=True)

    raise Exit(code=result)


@task
def setuppy(c):
    """Converts pyproject.toml to setup.py format."""
    with c.cd(APP_DIR):
        print("Running dephell deps convert in main directory.")
        c.run("dephell deps convert", pty=True)

    for dir_ in APP_PATH_NAMES:
        with c.cd(dir_):
            print(f"Updating setup.py in {dir_}")
            c.run("dephell deps convert --from=pyproject.toml --to=setup.py", pty=True)

            c.run('echo -e "# pylint: disable=all\n$(cat setup.py)" > setup.py')
            c.run("black setup.py")


@task
def lock(c):
    """Updates the poetry.lock files."""
    with c.cd(APP_DIR):
        for dir_ in APP_PATH_NAMES:
            with c.cd(dir_):
                print(f"Updating lock in {dir_}")
                c.run("poetry update --lock", pty=True)


@task
def clean(
    c, coverage=True, setuppy=False, testdb=True, pyc=True, docs_=True, silent=False
):
    """Cleans up."""
    with c.cd(APP_DIR):
        if coverage:
            if not silent:
                print("Cleaning up after coverage...")
            c.run("rm .coverage* || true", hide=True)

        if setuppy:
            if not silent:
                print("Cleaning up after setup.py...")
            c.run("rm setup.py || true", hide=True)

            for app_path in APP_PATH_NAMES:
                c.run(f"rm {app_path}/setup.py || true", hide=True)

        if testdb:
            if not silent:
                print("Cleaning up after testing database...")
            c.run("rm test.db || true", hide=True)

        if pyc:
            if not silent:
                print("Cleaning up .pyc and __pycache__...")
            c.run(
                r'find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf || true',
                hide=True,
            )

        if docs_:
            if not silent:
                print("Cleaning up docs site...")
            c.run("rm -r site || true", hide=True)

@task
def docs(c, port=8002, build=False, verbose=False):
    """Serves the docs."""
    args = []

    if verbose:
        args.append("--verbose")

    with c.cd(APP_DIR):
        if build:
            return c.run(f"mkdocs build {' '.join(args)}", pty=True, warn=True)
        else:
            return c.run(f"mkdocs serve -a 0.0.0.0:{port} {' '.join(args)}", pty=True)
