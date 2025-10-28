import os
import shutil
from consulting_firm.project_assessor import ProjectAssessor


def test_assess_no_docs(tmp_path):
    pa = ProjectAssessor()
    # directory does not contain project_documents
    assert pa.assess(str(tmp_path)) == "Greenfield Discovery Path"


def test_assess_empty_docs(tmp_path):
    docs = tmp_path / "project_documents"
    docs.mkdir()
    pa = ProjectAssessor()
    assert pa.assess(str(tmp_path)) == "Greenfield Discovery Path"


def test_assess_sow_present(tmp_path):
    docs = tmp_path / "project_documents"
    docs.mkdir()
    sow = docs / "SOW.md"
    sow.write_text("# Statement of Work\nContent")
    pa = ProjectAssessor()
    assert pa.assess(str(tmp_path)) == "Validation & Enhancement Path"
