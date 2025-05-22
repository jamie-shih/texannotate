import sys
import pathlib
import base64
import io
import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from texcompile.client import (
    compile_pdf,
    compile_pdf_return_bytes,
    compile_html_return_text,
    OutputFile,
    CompilationException,
)


def _mock_send_request_factory(result):
    def _mock_send_request(sources_dir, host, port, autotex_or_latexml, main_tex=' '):
        return result
    return _mock_send_request


def test_compile_pdf_success(tmp_path, monkeypatch):
    data = {
        'success': True,
        'has_output': True,
        'main_tex_files': ['main.tex'],
        'log': 'ok',
        'output': [
            {
                'type': 'pdf',
                'path': 'build/main.pdf',
                'contents': base64.b64encode(b'PDFDATA').decode(),
            }
        ],
    }
    monkeypatch.setattr('texcompile.client.send_request', _mock_send_request_factory(data))
    result = compile_pdf('src', tmp_path)
    assert result.success
    assert result.main_tex_files == ['main.tex']
    assert result.output_files == [OutputFile('pdf', 'main.pdf')]
    assert (tmp_path / 'main.pdf').read_bytes() == b'PDFDATA'


def test_compile_pdf_failure(monkeypatch, tmp_path):
    data = {
        'success': False,
        'has_output': False,
        'main_tex_files': [],
        'log': 'fail',
        'output': [],
    }
    monkeypatch.setattr('texcompile.client.send_request', _mock_send_request_factory(data))
    with pytest.raises(CompilationException):
        compile_pdf('src', tmp_path)


def test_compile_pdf_return_bytes(monkeypatch):
    data = {
        'success': True,
        'has_output': True,
        'main_tex_files': ['main.tex'],
        'log': 'ok',
        'output': [
            {
                'type': 'pdf',
                'path': 'main.pdf',
                'contents': base64.b64encode(b'BYTES').decode(),
            }
        ],
    }
    monkeypatch.setattr('texcompile.client.send_request', _mock_send_request_factory(data))
    name, bio = compile_pdf_return_bytes('src')
    assert name == 'main.pdf'
    assert isinstance(bio, io.BytesIO)
    assert bio.read() == b'BYTES'


def test_compile_pdf_return_bytes_no_pdf(monkeypatch):
    data = {
        'success': True,
        'has_output': True,
        'main_tex_files': ['main.tex'],
        'log': 'ok',
        'output': [],
    }
    monkeypatch.setattr('texcompile.client.send_request', _mock_send_request_factory(data))
    with pytest.raises(CompilationException):
        compile_pdf_return_bytes('src')


def test_compile_html_return_text(monkeypatch):
    html_content = '<p>Hi</p>'
    data = {
        'success': True,
        'has_output': True,
        'main_tex_files': ['main.tex'],
        'log': 'ok',
        'output': [
            {
                'type': 'html',
                'path': 'out.html',
                'contents': base64.b64encode(html_content.encode('utf-8')).decode(),
            }
        ],
    }
    monkeypatch.setattr('texcompile.client.send_request', _mock_send_request_factory(data))
    text = compile_html_return_text('main.tex', 'src')
    assert text == html_content
