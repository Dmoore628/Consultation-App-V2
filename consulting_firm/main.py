import argparse
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from project_assessor import ProjectAssessor
from expert_team import ExpertTeam
from validation_engine import ValidationEngine
from document_generator import DocumentGenerator
from exporter import generate_architecture_diagram, export_to_docx, export_to_pdf
from config import OUTPUT_PATH


def _ensure_project_docs(project_path: str):
    docs_dir = os.path.join(project_path, 'project_documents')
    os.makedirs(docs_dir, exist_ok=True)
    return docs_dir


def _interactive_consultation(project_path: str):
    """Interactive CLI to gather discovery inputs and write to consultation_notes.md.

    This is optional; if used in non-interactive environments, prefer --consult-file.
    """
    docs_dir = _ensure_project_docs(project_path)
    qa = []
    questions = [
        ("Project name and 1–2 sentence mission?", "name_mission"),
        ("Primary users and key jobs-to-be-done?", "users_jtbd"),
        ("Top 5 features for MVP (bulleted)?", "features_mvp"),
        ("Non-functional requirements (performance, availability, scale)?", "nfrs"),
        ("Data sources and data privacy/compliance constraints?", "data_compliance"),
        ("AI/ML goals (what decisions/predictions and why)?", "ai_goals"),
        ("Integrations (APIs, systems) and constraints?", "integrations"),
        ("Security and regulatory standards applicable (e.g., GDPR, SOC2)?", "security_standards"),
        ("Timeline and critical milestones?", "timeline"),
        ("Budget/constraints and team availability?", "budget_team"),
    ]
    print("\n[Consultation] Please answer the following. Press Enter to skip any question.\n")
    for q, key in questions:
        try:
            ans = input(f"- {q} \n> ")
        except EOFError:
            ans = ""
        qa.append((q, ans or "(no answer)"))

    out_path = os.path.join(docs_dir, 'consultation_notes.md')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write("# Consultation Notes\n\n")
        for q, a in qa:
            f.write(f"## {q}\n{a}\n\n")
    print(f"[Consultation] Saved answers to {out_path}")
    return out_path


def _ingest_consult_file(project_path: str, consult_file: str):
    docs_dir = _ensure_project_docs(project_path)
    out_path = os.path.join(docs_dir, 'consultation_notes.md')
    with open(consult_file, 'r', encoding='utf-8') as src, open(out_path, 'w', encoding='utf-8') as dst:
        dst.write(src.read())
    print(f"[Consultation] Loaded consultation file into {out_path}")
    return out_path


def run(project_path: str, outputs_path: str, max_rounds: int = 3, do_export: bool = False, log_callback=None):
    """Run the consulting firm pipeline with optional progress logging.
    
    Args:
        log_callback: Optional function(message: str) called for progress updates
    """
    log = log_callback or (lambda msg: None)
    
    os.makedirs(outputs_path, exist_ok=True)
    assessor = ProjectAssessor()
    maturity = assessor.assess(project_path)
    log(f"📋 Project Assessment: {maturity}")

    team = ExpertTeam(outputs_path=outputs_path, log_callback=log)
    validator = ValidationEngine()
    previous_sow_text = None
    feedback_text = None
    artifacts = {}

    for round_idx in range(1, max_rounds + 1):
        log(f"🔄 Discovery/SOW round {round_idx}/{max_rounds}")
        artifacts = team.run(project_path, maturity, previous_sow=previous_sow_text, feedback=feedback_text)
        
        log("✅ Validating outputs...")
        validation_report = validator.validate(artifacts)

        # Evaluate SOW completeness and decide to continue
        sow_path = artifacts.get('sow')
        if sow_path and os.path.exists(sow_path):
            with open(sow_path, 'r', encoding='utf-8') as f:
                sow_text = f.read()
            complete, missing, notes = validator.evaluate_sow(sow_text)
            if complete:
                log("✅ SOW completeness gate PASSED")
                break
            else:
                missing_str = ", ".join(missing)
                notes_str = "; ".join(notes)
                feedback_text = f"Missing sections: {missing_str}. Notes: {notes_str}"
                previous_sow_text = sow_text
                log(f"⚠️ SOW gate not met; refining. Feedback: {feedback_text[:100]}...")

    log(f"📄 Validation report: {validation_report}")

    if do_export:
        log("📦 Generating exports...")
        # Generate exports: HTML/CSS -> PDF (WeasyPrint preferred)
        dg = DocumentGenerator(output_path=outputs_path)
        sow_md = artifacts.get('sow')
        tech_md = artifacts.get('tech')
        if sow_md and os.path.exists(sow_md):
            try:
                pdf = dg.generate_from_markdown(sow_md, out_format='pdf')
                log(f"✅ SOW PDF: {pdf}")
            except Exception as e:
                log(f"⚠️ SOW export failed: {e}")

        # Generate architecture diagram from tech file (if present)
        if tech_md and os.path.exists(tech_md):
            try:
                with open(tech_md, 'r', encoding='utf-8') as tf:
                    img = generate_architecture_diagram(tf.read(), outputs_path)
                log(f"✅ Architecture diagram: {img}")
            except Exception as e:
                log(f"⚠️ Diagram generation failed: {e}")

        # Create combined DOCX and PDF of all artifacts
        try:
            docx_path = export_to_docx(artifacts, out_docx=os.path.join(outputs_path, 'final_deliverable.docx'))
            pdf_path = export_to_pdf(artifacts, out_pdf=os.path.join(outputs_path, 'final_deliverable.pdf'))
            log(f"✅ DOCX: {docx_path}")
            log(f"✅ PDF: {pdf_path}")
        except Exception as e:
            log(f"⚠️ Combined export failed: {e}")
    
    log("🎉 Generation Complete!")
    return artifacts, validation_report


def main():
    parser = argparse.ArgumentParser(description="Consulting Firm in a Box - Conductor")
    parser.add_argument("project_path", help="Path to project folder (contains project_documents/)")
    parser.add_argument("--outputs", default=OUTPUT_PATH, help="Outputs directory")
    parser.add_argument("--export", action='store_true', help="Generate PDF/DOCX exports and diagrams")
    parser.add_argument("--rounds", type=int, default=3, help="Max refinement rounds for SOW")
    parser.add_argument("--provider", default=None, help="Model provider override: mock|openai|ollama")
    parser.add_argument("--interactive", action='store_true', help="Run an interactive consultation to collect inputs")
    parser.add_argument("--consult-file", default=None, help="Load consultation Q&A from a markdown/text file")
    args = parser.parse_args()

    # Allow override of model provider via CLI flag
    if args.provider:
        os.environ['MODEL_PROVIDER'] = args.provider

    # Optional consultation intake
    if args.interactive:
        _interactive_consultation(args.project_path)
    elif args.consult_file:
        if not os.path.exists(args.consult_file):
            raise FileNotFoundError(args.consult_file)
        _ingest_consult_file(args.project_path, args.consult_file)

    # Print mode for CLI
    def cli_log(msg):
        print(f"[Conductor] {msg}")
    
    run(args.project_path, args.outputs, max_rounds=args.rounds, do_export=args.export, log_callback=cli_log)


if __name__ == "__main__":
    main()
