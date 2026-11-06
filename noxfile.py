import nox
from nox_uv import session

nox.options.default_venv_backend = "uv"

PYPROJECT = nox.project.load_toml("pyproject.toml")
PYTHON_VERSIONS = nox.project.python_versions(
    PYPROJECT, max_version="3.12"
)  # loads Python versions from requires-python

DEV_GROUPS = ["dev"]


@session(uv_groups=DEV_GROUPS, default=False)
def erase_prev_cov_data(session: nox.Session) -> None:
    session.run("coverage", "erase")


@session(requires=["erase_prev_cov_data"], python=PYTHON_VERSIONS, uv_groups=DEV_GROUPS, default=False)
def test(session: nox.Session) -> None:
    session.run(
        "coverage", "run", "-m", "pytest", *session.posargs, env={"COVERAGE_FILE": f".coverage.{session.python}"}
    )


@session(requires=["test"], uv_groups=DEV_GROUPS, default=True)
def merge_report(session: nox.Session) -> None:
    session.run("coverage", "combine")
    session.run("coverage", "report", "--show-missing")
