"""
The TeX output has not changed: every fixture in tests/fixtures is converted and compared, byte for byte, with the
.tex file that md2tex wrote for it. name@variant.tex is the Markdown of name.md with the convert() arguments from
name@variant.args. See battery.py for how the fixtures are made.
"""
import json

import pytest

from battery import CONVERT_ARGS, FIXTURES
from md2misc import convert

TEX_FILES = sorted(FIXTURES.glob("*.tex"))


@pytest.mark.parametrize("tex_path", TEX_FILES, ids=[p.stem for p in TEX_FILES])
def test_tex_output_is_unchanged(tex_path):
    md_path = FIXTURES / (tex_path.stem.split("@")[0] + ".md")
    args_path = tex_path.with_suffix(".args")
    extra = json.loads(args_path.read_text()) if args_path.exists() else {}
    assert convert(md_path.read_text(), **{**CONVERT_ARGS, **extra}) == tex_path.read_text()
