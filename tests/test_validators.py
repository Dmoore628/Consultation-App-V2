import os
from consulting_firm.validation_engine import ValidationEngine


def test_validate_missing(tmp_path):
    ve = ValidationEngine()
    out = ve.validate({'a': str(tmp_path / 'nope.md')})
    assert os.path.exists(out)


def test_validate_basic_quality(tmp_path):
    # create a short file and a longer tech file with arrows
    a = tmp_path / 'short.md'
    a.write_text('short')
    tech = tmp_path / 'tech.md'
    tech.write_text('# Technical Architecture\nComponents:\n- Frontend\n- API\nFrontend -> API')
    ve = ValidationEngine()
    out = ve.validate({'discovery': str(a), 'tech': str(tech)})
    assert os.path.exists(out)
    txt = open(out, 'r', encoding='utf-8').read()
    assert 'TOO_SHORT' in txt
    assert 'connections' in txt.lower() or 'component' in txt.lower()
