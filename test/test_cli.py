import shutil
import tempfile
import traceback
from pathlib import Path

import pytest
from acclimatise.cli import main
from click.testing import CliRunner

from .util import validate_cwl, validate_wdl


@pytest.fixture()
def runner():
    return CliRunner()


def cli_worked(result):
    if result.exit_code == 0:
        return True
    else:
        traceback.print_exception(*result.exc_info)
        assert result.exit_code == 0


def test_pipe_wdl(runner, htseq_help):
    result = runner.invoke(
        main, ["pipe", "htseq-count", "--format", "wdl"], input=htseq_help
    )
    cli_worked(result)
    validate_wdl(result.output)


def test_pipe_cwl(runner, htseq_help):
    result = runner.invoke(
        main, ["pipe", "htseq-count", "--format", "cwl"], input=htseq_help
    )
    cli_worked(result)
    validate_cwl(result.output)


@pytest.mark.skipif(
    not shutil.which("htseq-count"), reason="htseq-count is not installed"
)
def test_explore(runner):
    with tempfile.TemporaryDirectory() as tempdir:
        result = runner.invoke(main, ["explore", "htseq-count", "--out-dir", tempdir])
        cli_worked(result)
        assert len(list(Path(tempdir).iterdir())) == 1


def test_grammar(runner):
    result = runner.invoke(main, ["grammar"])
    assert result.exit_code == 0
    assert len(result.output) > 20
