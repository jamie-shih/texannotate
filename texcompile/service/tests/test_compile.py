from lib.compile_autotex import (
    CompiledTexFile,
    did_compilation_fail,
    get_compiled_tex_files_from_autotex_output,
    get_errors,
    get_last_autotex_compiler,
    _contains_cjk,
    _guess_main_tex,
)


def test_get_compiled_tex_files():
    stdout = bytearray(
        "[verbose]:  ~~~~~~~~~~~ Processing file 'main.tex'\n" + "...\n"
        # DVI files that are successfully processed should not be considered TeX files.
        + "[verbose]:  ~~~~~~~~~~~ Processing file 'main.dvi'\n"
        + "...\n"
        + "[verbose]:  ~~~~~~~~~~~ Processing file 'other.tex'\n"
        + "..."
        + "<other.tex> appears to be tex-type, but was neither included nor processable:"
        + "...",
        "utf-8",
    )
    compiled_tex_files = get_compiled_tex_files_from_autotex_output(stdout)
    assert len(compiled_tex_files) == 1
    assert CompiledTexFile("main.tex") in compiled_tex_files


def test_get_errors():
    stdout = bytearray(
        "[verbose]: This is TeX, Version 3.14159265 (TeX Live 2017) (preloaded format=tex)\n"
        + "(./BioVELum.tex\n"
        + "! Undefined control sequence.\n"
        + "l.1 \\documentclass\n"
        + "                  [10pt]{article}\n"
        + "? \n"
        + "! Emergency stop.\n"
        + "l.1 \\documentclass\n"
        + "                  [10pt]{article}\n"
        + "No pages of output.\n"
        + "Transcript written on BioVELum.log.\n",
        "utf-8",
    )
    errors = list(get_errors(stdout, context=3))
    assert len(errors) == 2

    error1 = errors[0]
    assert len(error1.splitlines()) == 3
    assert error1.startswith(b"! Undefined control sequence")

    error2 = errors[1]
    assert len(error2.splitlines()) == 3
    assert error2.startswith(b"! Emergency stop.")


def test_get_last_autotex_compiler():
    autotex_log = "\n".join(
        [
            "[verbose]:  ~~~~~~~~~~~ Running hpdflatex for the first time ~~~~~~~~",
            "...",
            "[verbose]:  ~~~~~~~~~~~ Running pdflatex for the first time ~~~~~~~~",
            "...",
            "[verbose]:  ~~~~~~~~~~~ Running pdflatex for the second time ~~~~~~~~",
            "...",
        ]
    )
    compiler = get_last_autotex_compiler(autotex_log)
    assert compiler == "pdflatex"


def test_detect_compilation_failure():
    autotex_log = "\n".join(
        [
            "[verbose]:  ~~~~~~~~~~~ Running pdflatex for the first time ~~~~~~~~",
            "! Emergency stop.",
        ]
    )
    failed = did_compilation_fail(autotex_log, "pdflatex")
    assert failed


def test_ignore_compilation_failure_for_other_compiler():
    autotex_log = "\n".join(
        [
            "[verbose]:  ~~~~~~~~~~~ Running pdflatex for the first time ~~~~~~~~",
            "! Emergency stop.",
        ]
    )
    failed = did_compilation_fail(autotex_log, "other-compiler-not-pdflatex")
    assert not failed


def test_contains_cjk(tmp_path):
    tex = tmp_path / "main.tex"
    tex.write_text("Hello 你好")
    assert _contains_cjk(str(tmp_path))


def test_contains_cjk_false(tmp_path):
    tex = tmp_path / "main.tex"
    tex.write_text("Hello world")
    assert not _contains_cjk(str(tmp_path))


def test_guess_main_tex(tmp_path):
    (tmp_path / "main.tex").write_text("")
    (tmp_path / "other.tex").write_text("")
    assert _guess_main_tex(str(tmp_path)) == "main.tex"


def test_guess_main_tex_single(tmp_path):
    (tmp_path / "foo.tex").write_text("")
    assert _guess_main_tex(str(tmp_path)) == "foo.tex"


def test_guess_main_tex_none(tmp_path):
    (tmp_path / "a.tex").write_text("")
    (tmp_path / "b.tex").write_text("")
    assert _guess_main_tex(str(tmp_path)) is None
