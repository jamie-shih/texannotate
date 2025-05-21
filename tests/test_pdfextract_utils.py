import sys
import types
import pathlib
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

# provide stub for fitz so the module can be imported without dependency
stub_fitz = types.ModuleType('fitz')
stub_fitz.Rect = object
sys.modules['fitz'] = stub_fitz

from pdfextract import pdf_extract


def test_flags_decomposer():
    assert pdf_extract.flags_decomposer(0b10010) == [
        'italic',
        'sans',
        'proportional',
        'bold'
    ]


def test_convert_color_none():
    assert pdf_extract.convert_color(None) == '#000000'


def test_convert_color_valid():
    assert pdf_extract.convert_color((0.5, 0.5, 0.5)) == '#808080'


def test_token_in_bbox():
    token = {'x0': 0, 'x1': 10, 'top': 0, 'bottom': 10}
    assert pdf_extract.token_in_bbox(token, (0, 0, 20, 20))
    assert not pdf_extract.token_in_bbox(token, (20, 20, 40, 40))
