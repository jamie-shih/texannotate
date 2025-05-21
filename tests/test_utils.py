import sys
import pathlib
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from utils import utils


def test_tup2str_valid():
    assert utils.tup2str((0.0, 0.5, 1.0)) == "0.0,0.5,1.0"


def test_tup2str_invalid_length():
    assert utils.tup2str((1.0, 0.5)) is None


def test_tup2str_error():
    with pytest.raises(Exception):
        utils.tup2str((0.2, 1.2, 0.3))
