import os
from typing import Literal


class ProjectAssessor:
    """Analyze a project folder and return a maturity assessment string.

    Outputs:
      - "Greenfield Discovery Path"
      - "Gap Analysis Path"
      - "Validation & Enhancement Path"
      - "Custom Assessment"
    """

    def __init__(self):
        pass

    def assess(self, project_path: str) -> str:
        docs_dir = os.path.join(project_path, "project_documents")
        if not os.path.isdir(docs_dir):
            return "Greenfield Discovery Path"

        files = os.listdir(docs_dir)
        if not files:
            return "Greenfield Discovery Path"

        # Look for a Statement of Work or SOW-like files
        lower = [f.lower() for f in files]
        if any("sow" in f or "statement_of_work" in f or "scope_of_work" in f for f in lower):
            return "Validation & Enhancement Path"

        # Partial documents present
        return "Gap Analysis Path"


if __name__ == '__main__':
    pa = ProjectAssessor()
    print(pa.assess('.'))
