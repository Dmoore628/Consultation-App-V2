Consulting Firm in a Box — Local Quickstart
=========================================

What this repository provides
- A local, minimal prototype of the "Consulting Firm in a Box" conductor.
- Modules:
  - `project_assessor.py` — detects project maturity from `project_documents/`.
  - `expert_team.py` — generates baseline deliverables (discovery, SOW, tech doc, roadmap).
  - `validation_engine.py` — runs simple heuristics and produces `validation_report.md`.
  - `main.py` — conductor CLI to run the flow.

Quick run (Windows PowerShell)
1. Create a venv and activate it (optional but recommended):

```powershell
python -m venv consulting_ai; .\consulting_ai\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Run the conductor against the sample project included:

```powershell
python main.py sample_project --outputs outputs
```

Next steps
- Hook each module to real LLM/agent libraries (Ollama, OpenAI, crewai, langchain, etc.).
- Replace stub artifact content generation with role-specific agents and cross-review loops.
- Add diagram export integration (diagrams.net, mermaid, etc.) and richer templates.

Notes on recommended local AI (optional)
- Install Ollama (Windows): winget install Ollama.Ollama
- Pull a local model as desired and update agent code to call it.
