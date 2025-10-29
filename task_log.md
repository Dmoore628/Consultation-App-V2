# Task Log

## 2025-10-29 — Architectural and UX Audit

### Goal
Audit the application for unused/redundant code, monolithic files/functions, and evaluate UX and data flow. Produce actionable refactor recommendations and risks.

### What was done
- Mapped core modules and data flow end-to-end.
- Identified monolithic files/functions and separation-of-concerns issues.
- Flagged unused or redundant modules/patterns.
- Reviewed UX flow in `professional_ui.py` including session management and generation pipeline.

### Key findings
- Monolithic UI module: `consulting_firm/professional_ui.py` is ~500 lines and combines session bootstrap, intake form, document upload, generation, auto-generation logic, chat, QA, notes, and session controls in one class.
- Large function: `_render_consulting_interface` mixes UI, file I/O, orchestration, and model calls; difficult to test and maintain.
- Redundant intake definitions: `consulting_firm/intake_flow.py` defines `ClientProfile` and stages, but the UI recreates intake logic instead of reusing workflow definitions.
- Potentially unused module: `consulting_firm/feasibility_analyzer.py` is not referenced by the pipeline or UI.
- Personas breadth vs usage: Many personas defined; only a subset used by `ExpertTeam`/`AgentCoordinator` and `ModelClient`. This is fine but increases maintenance if not curated.
- Repeated `sys.path.insert(...)` in multiple modules; can be centralized or removed by using package-relative imports.
- Output scoping: UI reads from a global `outputs/` directory, which can mix runs. Better to scope outputs per project/timestamp.
- Long-running actions: Generation is synchronous in UI; needs clearer progress/disable states and error surfaces.

### Data flow overview
- UI collects `ClientProfile` → writes optional consultation notes → calls `main.run(project_path, outputs, do_export)` → `ExpertTeam.run(...)` produces artifacts → `ValidationEngine.validate(...)` writes `outputs/validation_report.md` → `exporter` and `document_generator` create PDFs/DOCX/diagrams.
- Discovery chat uses `ModelClient` with `engagement_manager` and QA feedback to update `session_state.discovery_status` and structured summary via `consultation_state.extract_structured_from_chat`.

### Risks and issues
- Tight coupling between UI and pipeline (UI imports `main.run`) complicates reuse/testing.
- Large UI method raises risk of regressions; minimal unit testability.
- Global outputs may surface stale artifacts to end users.
- Multiple model calls per chat step without rate limiting/error recovery could degrade UX.

### Recommendations (incremental, rollback-friendly)
1) Extract UI into submodules:
   - `ui/session.py`: session initialization and serialization of `ClientProfile` and statuses.
   - `ui/intake.py`: pure functions to render and validate intake; reuse `IntakeWorkflow`/`ClientProfile`.
   - `ui/docs.py`: upload/save and consultation notes writer.
   - `ui/generation.py`: trigger pipeline and display artifacts; isolate file I/O.
   - `ui/chat.py`: chat loop and QA controller; small functions for prompts and state updates.
2) Break `_render_consulting_interface` into focused methods per concern; target functions ≤ 60–80 lines.
3) Replace global outputs listing with project-scoped directory: `outputs/{project_slug}/{ts}/...` and display only current run.
4) Remove or integrate `feasibility_analyzer.py`. If desired, wire into discovery via `ExpertTeam` or delete.
5) Replace `sys.path.insert(...)` with package-relative imports; ensure package is installed in editable mode.
6) Add lightweight unit tests for:
   - `consultation_state.extract_structured_from_chat` JSON parsing fallbacks.
   - `validation_engine` SOW completeness and architecture checks.
   - `project_assessor.assess` maturity logic.
7) Add integration test for `main.run` with `MODEL_PROVIDER=mock` to produce deterministic artifacts.
8) UX: add progress bars/disabled states during generation; clear error banners; show next steps.

### Next steps
- Create feature branch `feature/audit-refactor-ui` and sub-branches per module extraction.
- First subtask: Extract intake and session management from `professional_ui.py` to `ui/intake.py` and `ui/session.py`, reusing `IntakeWorkflow`/`ClientProfile`.
- Add project-scoped outputs and update display logic.
- Stage and test each step with unit and integration tests before proceeding.

### What could go wrong
- Refactor may break existing session state keys; mitigate by migrating keys and providing defaults.
- Changing outputs path could hide legacy artifacts; provide a toggle to view past runs.
- Import path changes may fail if package not installed; add `pip install -e .` guidance or update `PYTHONPATH` in Streamlit run script.

### Rollback
- Each subtask should be on its own branch; to rollback, revert that branch or restore the original `professional_ui.py` and outputs listing logic.


